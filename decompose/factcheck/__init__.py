import concurrent.futures
import time
import tiktoken
import json

from dataclasses import dataclass, asdict
from factcheck.utils.llmclient import CLIENTS, model2client
from factcheck.utils.prompt import prompt_mapper
from factcheck.utils.logger import CustomLogger
from factcheck.utils.api_config import load_api_config
from factcheck.utils.data_class import PipelineUsage, FactCheckOutput, ClaimDetail, FCSummary
from factcheck.core import (
    Decompose,
    Checkworthy,
)

logger = CustomLogger(__name__).getlog()


class FactCheck:
    def __init__(
        self,
        default_model: str = "gpt-4o",
        client: str = None,
        prompt: str = "chatgpt_prompt",
        retriever: str = "serper",
        decompose_model: str = None,
        checkworthy_model: str = None,
        api_config: dict = None,
        num_seed_retries: int = 3,
    ):
        # TODO: better handle raw token count
        self.encoding = tiktoken.get_encoding("cl100k_base")

        self.prompt = prompt_mapper(prompt_name=prompt)

        # load configures for API
        self.load_config(api_config=api_config)

        # llms for each step (sub-module)
        step_models = {
            "decompose_model": decompose_model,
            "checkworthy_model": checkworthy_model,
            #"query_generator_model": query_generator_model,
            #"evidence_retrieval_model": evidence_retrieval_model,
            #"claim_verify_model": claim_verify_model,
        }

        for key, _model_name in step_models.items():
            _model_name = default_model if _model_name is None else _model_name
            print(f"== Init {key} with model: {_model_name}")
            if client is not None:
                #logger.info(f"== Use specified client: {client}")
                LLMClient = CLIENTS[client]
            else:
                #logger.info("== LLMClient is not specified, use default llm client.")
                LLMClient = model2client(_model_name)
            setattr(self, key, LLMClient(model=_model_name, api_config=self.api_config))

        # sub-modules
        self.decomposer = Decompose(llm_client=self.decompose_model, prompt=self.prompt)
        self.checkworthy = Checkworthy(llm_client=self.checkworthy_model, prompt=self.prompt)
        self.attr_list = ["decomposer", "checkworthy"]
        self.num_seed_retries = num_seed_retries

        #logger.info("===Sub-modules Init Finished===")

    def load_config(self, api_config: dict) -> None:
        # Load API config
        self.api_config = load_api_config(api_config)

    def check_text(self, raw_text: str):
        # first clear current usage
        self._reset_usage()

        st_time = time.time()
        # step 1
        claims = self.decomposer.getclaims(doc=raw_text, num_retries=self.num_seed_retries)
        # Parallel run restore claims and checkworthy
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_claim2doc = executor.submit(
                self.decomposer.restore_claims, doc=raw_text, claims=claims, num_retries=self.num_seed_retries
            )
            # step 2
            future_checkworthy_claims = executor.submit(
                self.checkworthy.identify_checkworthiness, claims, num_retries=self.num_seed_retries
            )
            # Wait for all futures to complete
            claim2doc = future_claim2doc.result()
            checkworthy_claims, claim2checkworthy = future_checkworthy_claims.result()

        checkworthy_claims_S = set(checkworthy_claims)
        

        #claim_queries_dict = {k: v for k, v in claim_queries_dict.items() if k in checkworthy_claims_S}

        for i, (claim, origin) in enumerate(claim2doc.items()):
            logger.info(f"== raw_text claims {i} --- {claim} --- {origin}")
        for i, claim in enumerate(checkworthy_claims):
            logger.info(f"== Checkworthy claims {i}: {claim}")

        if checkworthy_claims == []:
            return claim2doc
            return self._finalize_factcheck(raw_text=raw_text, claim_detail=[], return_dict=True)

        
        """
        # step 4
        claim_evidences_dict = self.evidence_crawler.retrieve_evidence(claim_queries_dict=claim_queries_dict)
        for claim, evidences in claim_evidences_dict.items():
            logger.info(f"== Claim: {claim}")
            logger.info(f"== Evidence: {evidences}\n")
        step4_time = time.time()

        # step 5
        claim_verifications_dict = self.claimverify.verify_claims(claim_evidences_dict=claim_evidences_dict)
        for k, v in claim_verifications_dict.items():
            logger.info(f"== Claim: {k} --- Verify: {v}")
        step5_time = time.time()
        logger.info(
            f"== State: Done! \n Total time: {step5_time-st_time:.2f}s. (create claims:{step123_time-st_time:.2f}s |||  retrieve:{step4_time-step123_time:.2f}s ||| verify:{step5_time-step4_time:.2f}s)"
        )
        """
        claim_detail = [
        asdict(claim) for claim in self._merge_claim_details(
            claim2doc=claim2doc,
            claim2checkworthy=claim2checkworthy,
        # claim2queries=claim_queries_dict
        )
        ]


        return claim_detail
    def _get_usage(self):
        return PipelineUsage(**{attr: getattr(self, attr).llm_client.usage for attr in self.attr_list})

    def _reset_usage(self):
        for attr in self.attr_list:
            getattr(self, attr).llm_client.reset_usage()

    def _merge_claim_details(
        self, claim2doc: dict, claim2checkworthy: dict
    ) -> list[ClaimDetail]:
        claim_details = []
        for i, (claim, origin) in enumerate(claim2doc.items()):
            claim_obj = ClaimDetail(
                id=i,
                claim=claim,
                checkworthy=True,
                checkworthy_reason=claim2checkworthy.get(claim, "No reason provided, please report issue."),
                origin_text=origin["text"],
                start=origin["start"],
                end=origin["end"],
                )
            claim_details.append(claim_obj)
        return claim_details

    def _finalize_factcheck(
        self, raw_text: str, claim_detail: list[ClaimDetail] = None, return_dict: bool = True
    ) -> FactCheckOutput:
        num_claims = len(claim_detail)
        num_checkworthy_claims = len(claim_detail)
    
        summary = FCSummary(
            num_claims,
            num_checkworthy_claims,
        )

        num_tokens = len(self.encoding.encode(raw_text))
        output = FactCheckOutput(
            raw_text=raw_text,
            token_count=num_tokens,
            usage=self._get_usage(),
            #claim_detail=claim_detail,
            #summary=summary,
        )

        if not output.attribute_check():
            raise ValueError("Output attribute check failed.")

        #logger.info(f"== Overall Factuality: {output.summary.factuality}\n")
        
        if return_dict:
            return asdict(output)
        else:
            return output

