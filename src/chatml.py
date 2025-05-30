import re
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("chatml")

BEGIN = "<|begin_of_text|>"
END = "<|end_of_text|>"

VALID_ROLES = ('system', 'assistant', 'user')


def chatml_role(role:str) -> str:
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid ChatML role: '${role}'")
    return f"<|{role}|>"

def chatml_block(role: str, content: str) -> str:
    return "\n".join([
        chatml_role(role),
        content.strip(),
        END
    ])
    
def chatml_prompt(
    system: str = "",
    history: list[tuple[str, str]] = [],
    next_user_prompt: str = ""
) -> str:
    """
    Builds a ChatML-style prompt for LLaMA 3.

    Args:
        system: System instruction text (optional)
        history: List of (role, message) message tuples
        next_user_prompt: Final user input for the model to respond to

    Returns:
        Full prompt string
    """
    blocks = [BEGIN]

    if system:
        blocks.append(chatml_block("system", system))

    for role, msg in history:
        blocks.append(chatml_block(role, msg))

    if next_user_prompt:
        blocks.append(chatml_block("user", sanitize_chatml_input(next_user_prompt)))
        blocks.append(chatml_role("assistant"))  # model's next turn to generate

    return "\n".join(blocks).strip()



# Reserved ChatML tokens
CHATML_TOKENS = {
    
    # Roles
    "<|system|>",
    "<|user|>",
    "<|assistant|>",
    
    # Control tokens
    "<|begin_of_text|>",
    "<|end_of_text|>",
    
    # I think these are just for the OpenAI variant? If so, they can be removed
    # since its ChatML is never exposed.
    "<|im_start|>",
    "<|im_end|>",
}

def sanitize_chatml_input(text: str) -> str:
    """
    Sanitize text to avoid injecting ChatML control tokens.

    Args:
        text: Raw user input

    Returns:
        Sanitized string
    """
    def replace_token(match):
        token = match.group(0)
        return f"[{token[2:-2]}]"  # e.g. <|user|> → [user]

    # Pattern: match full reserved tokens
    pattern = re.compile(r"<\|[a-z_]+?\|>")
    return pattern.sub(replace_token, text)
