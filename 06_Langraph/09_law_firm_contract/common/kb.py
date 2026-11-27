"""
Search the Bedrock Knowledge Base, always limited to ONE client's contracts.

The filter is built here, in code, from the client_id the login gave us. The
LLM is never asked to write it. Each contract was uploaded with a small
metadata file (see scripts/upload_to_kb.py), and Bedrock applies the filter on
that metadata before it returns any text.
"""
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError

from common.config import AWS_REGION, KB_ID, KB_TYPE


@lru_cache(maxsize=1)
def _client():
    return boto3.client("bedrock-agent-runtime", region_name=AWS_REGION)


def build_filter(client_id: str, contract_ids: list[str] | None = None) -> dict:
    """Metadata filter: this client's contracts, optionally only these contract ids."""
    conditions: list[dict] = [{"equals": {"key": "client_id", "value": client_id}}]
    if contract_ids:
        conditions.append({"in": {"key": "contract_id", "value": contract_ids}})
    # Bedrock's andAll needs 2 or more conditions, so only wrap when we have them.
    return conditions[0] if len(conditions) == 1 else {"andAll": conditions}


def retrieve(question: str, client_id: str, contract_ids: list[str] | None = None, k: int = 5) -> list[dict]:
    """Return the best-matching passages as dicts: text, source, contract_id, counterparty."""
    if not KB_ID:
        raise RuntimeError("KB_ID is empty. Create the Knowledge Base and put its id in .env (see README).")
    if contract_ids:
        k = min(max(k, 4 * len(contract_ids)), 50)  # enough room for every contract in scope
    # Both Knowledge Base types take the same settings, under a different name.
    search_key = "managedSearchConfiguration" if KB_TYPE == "managed" else "vectorSearchConfiguration"
    try:
        response = _client().retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": question},
            retrievalConfiguration={search_key: {
                "numberOfResults": k,
                "filter": build_filter(client_id, contract_ids),
            }},
        )
    except ClientError as exc:
        if "SearchConfiguration" in str(exc):  # the wrong type name was used
            raise RuntimeError(
                f"{exc}\nYour Knowledge Base looks like the other type. "
                f"KB_TYPE is '{KB_TYPE}'. Change it to '{'vector' if KB_TYPE == 'managed' else 'managed'}' in .env."
            ) from exc
        raise
    passages = []
    for item in response.get("retrievalResults", []):
        meta = item.get("metadata", {})
        passages.append({
            "text": item["content"]["text"],
            "source": item.get("location", {}).get("s3Location", {}).get("uri", ""),
            "contract_id": meta.get("contract_id", ""),
            "counterparty": meta.get("counterparty", ""),
        })
    return passages


def label(p: dict) -> str:
    """Short citation label for a passage, like 'NOV-001 CloudServe Inc'."""
    return f"{p['contract_id']} {p['counterparty']}".strip() or p["source"]
