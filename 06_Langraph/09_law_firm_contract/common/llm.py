"""One small helper for calling the Bedrock chat model."""
from functools import lru_cache

from langchain_aws import ChatBedrockConverse

from common.config import AWS_REGION, BEDROCK_MODEL_ID


@lru_cache(maxsize=1)
def _model() -> ChatBedrockConverse:
    # Created on first use, so importing this file never needs AWS credentials.
    return ChatBedrockConverse(model=BEDROCK_MODEL_ID, region_name=AWS_REGION, temperature=0)


def ask(prompt: str) -> str:
    """Send one prompt, get the reply as plain text."""
    content = _model().invoke(prompt).content
    if isinstance(content, list):  # some models return a list of content blocks
        content = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return content.strip()
