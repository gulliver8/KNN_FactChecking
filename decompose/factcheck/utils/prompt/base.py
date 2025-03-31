from dataclasses import dataclass


@dataclass
class BasePrompt:
    decompose_prompt: str = None
    checkworthy_prompt: str = None
    