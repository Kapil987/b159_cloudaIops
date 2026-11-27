"""
Upload the sample contracts to S3, with a metadata file next to each one, and
(optionally) start the Knowledge Base sync.

Why the metadata files: Bedrock reads <name>.metadata.json next to <name> and
stores those attributes with the document's chunks. That is what lets us filter
by client_id at search time.

    uploaded to S3:   contracts/NOV-001_cloudserve_saas.md
                      contracts/NOV-001_cloudserve_saas.md.metadata.json

Run from the project root:
    uv run python scripts/upload_to_kb.py           # upload only
    uv run python scripts/upload_to_kb.py --sync    # upload, then start the KB sync

Needs S3_BUCKET in .env. --sync also needs KB_ID and KB_DATA_SOURCE_ID.
"""
import json
import sys
from pathlib import Path

import boto3

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.config import AWS_REGION, KB_DATA_SOURCE_ID, KB_ID, PROJECT_ROOT, S3_BUCKET, S3_PREFIX
from common.sample_data import CONTRACTS


def main(sync: bool) -> None:
    if not S3_BUCKET:
        sys.exit("S3_BUCKET is empty. Set it in .env first.")

    s3 = boto3.client("s3", region_name=AWS_REGION)
    for c in CONTRACTS:
        key = f"{S3_PREFIX}{c['file']}"
        body = (PROJECT_ROOT / "sample_contracts" / c["file"]).read_bytes()
        s3.put_object(Bucket=S3_BUCKET, Key=key, Body=body)

        metadata = {"metadataAttributes": {
            "client_id": c["client_id"],
            "contract_id": c["contract_id"],
            "counterparty": c["counterparty"],
            "contract_type": c["contract_type"],
        }}
        s3.put_object(Bucket=S3_BUCKET, Key=f"{key}.metadata.json", Body=json.dumps(metadata).encode())
        print(f"uploaded s3://{S3_BUCKET}/{key}  (+ metadata)")

    if sync:
        if not (KB_ID and KB_DATA_SOURCE_ID):
            sys.exit("--sync needs KB_ID and KB_DATA_SOURCE_ID in .env.")
        agent = boto3.client("bedrock-agent", region_name=AWS_REGION)
        job = agent.start_ingestion_job(knowledgeBaseId=KB_ID, dataSourceId=KB_DATA_SOURCE_ID)
        print("sync started, job id:", job["ingestionJob"]["ingestionJobId"])
        print("Wait for the job to show Complete in the console before asking questions.")


if __name__ == "__main__":
    main(sync="--sync" in sys.argv)
