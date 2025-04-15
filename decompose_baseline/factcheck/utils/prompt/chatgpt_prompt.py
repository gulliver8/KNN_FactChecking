decompose_prompt = """
Your task is to decompose the text into atomic claims.
The answer should be a JSON with a single key "claims", with the value of a list of strings, where each string should be a context-independent claim, representing one fact.
Note that:
1. Each claim should be concise (less than 15 words) and self-contained.
2. Avoid vague references like 'he', 'she', 'it', 'this', 'the company', 'the man' and using complete names.
3. Generate at least one claim for each single sentence in the texts.

For example,
Text: Mary is a five-year old girl, she likes playing piano and she doesn't like cookies.
Output:
{{"claims": ["Mary is a five-year old girl.", "Mary likes playing piano.", "Mary doesn't like cookies."]}}

Text: {doc}
Output:
"""

# restore_prompt = """Given a text and a list of facts derived from the text, your task is to identify the corresponding words in the text that derive each fact.
# For each fact, please find the minimal continues span in the original text that contains the information to derive the fact. The answer should be a JSON dict where the keys are the facts and the values are the corresponding spans copied from the original text.
#
# For example,
# Text: Mary is a five-year old girl, she likes playing piano and she doesn't like cookies.
# Facts: ["Mary is a five-year old girl.", "Mary likes playing piano.", "Mary doesn't like cookies."]
#
# Output:
# {{"Mary is a five-year old girl.":"Mary is a five-year old girl",
# "Mary likes playing piano.":"she likes playing piano",
# "Mary doesn't like cookies.":"she doesn't like cookies."]
#
# Text: {doc}
# Facts: {claims}
# Output:
# """

# use this for demo
restore_prompt = """Given a text and a list of facts derived from the text, your task is to split the text into chunks that derive each fact.
For each fact, please find the corresponding continues span in the original text that contains the information to derive the fact. The answer should be a JSON dict where the keys are the facts and the values are the corresponding spans copied from the original text.
Please make sure the returned spans can be concatenated to the full original doc.

For example,
Text: Mary is a five-year old girl, she likes playing piano and she doesn't like cookies.
Facts: ["Mary is a five-year old girl.", "Mary likes playing piano.", "Mary doesn't like cookies."]

Output:
{{"Mary is a five-year old girl.":"Mary is a five-year old girl,",
"Mary likes playing piano.":"she likes playing piano",
"Mary doesn't like cookies.":"and she doesn't like cookies."]

Text: {doc}
Facts: {claims}
Output:

"""

checkworthy_prompt = """
Your task is to evaluate each provided statement to determine if it presents information whose factuality can be objectively verified by humans, irrespective of the statement's current accuracy. Consider the following guidelines:
1. Opinions versus Facts: Distinguish between opinions, which are subjective and not verifiable, and statements that assert factual information, even if broad or general. Focus on whether there's a factual claim that can be investigated.
2. Clarity and Specificity: Statements must have clear and specific references to be verifiable (e.g., "he is a professor" is not verifiable without knowing who "he" is).
3. Presence of Factual Information: Consider a statement verifiable if it includes factual elements that can be checked against evidence or reliable sources, even if the overall statement might be broad or incorrect.
Your response should be in JSON format, with each statement as a key and either "Yes" or "No" as the value, along with a brief rationale for your decision.

For example, given these statements:
1. Gary Smith is a distinguished professor of economics.
2. He is a professor at MBZUAI.
3. Obama is the president of the UK.

The expected output is:
{{
    "Gary Smith is a distinguished professor of economics.": "Yes (The statement contains verifiable factual information about Gary Smith's professional title and field.)",
    "He is a professor at MBZUAI.": "No (The statement cannot be verified due to the lack of clear reference to who 'he' is.)",
    "Obama is the president of the UK.": "Yes (This statement contain verifiable information regarding the political leadership of a country.)"
}}

For these statements:
{texts}

The output should be:
"""

class ChatGPTPrompt:
    decompose_prompt = decompose_prompt
    restore_prompt = restore_prompt
    checkworthy_prompt = checkworthy_prompt