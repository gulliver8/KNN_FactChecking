from .gpt_client import GPTClient
from .claude_client import ClaudeClient
from .local_openai_client import LocalOpenAIClient
from .ollama_client import OllamaClient

# fmt: off
CLIENTS = {
    "gpt": GPTClient,
    "claude": ClaudeClient,
    "local_openai": LocalOpenAIClient,
    "llama": LocalOpenAIClient
}
# fmt: on


def model2client(model_name: str):
    """If the client is not specified, use this function to map the model name to the corresponding client."""
    if model_name.startswith("gpt"):
        return GPTClient
    elif model_name.startswith("claude"):
        return ClaudeClient
    elif model_name.startswith("vicuna"):
        return LocalOpenAIClient
    elif model_name.startswith("phi") or model_name.startswith("llama"):
        return OllamaClient
    else:
        raise ValueError(f"Model {model_name} not supported.")
