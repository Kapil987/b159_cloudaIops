"""
All settings in one place, read from the environment (.env in the project root).

AS_OF_DATE is the "today" this demo pretends it is. The sample contracts have
fixed dates, so "expiring in the next 90 days" gives the same answer every time
you run it, instead of slowly drifting as the real calendar moves on.
"""
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Bedrock Knowledge Base (create it in the console, then paste the ids into .env)
KB_ID = os.getenv("KB_ID", "")
KB_DATA_SOURCE_ID = os.getenv("KB_DATA_SOURCE_ID", "")
# "managed" = a managed Knowledge Base (Bedrock runs the search and vector store for you).
# "vector" = the classic type, with a vector store you chose. The Retrieve API uses a
# different setting name for each, and rejects the wrong one with a ValidationException.
KB_TYPE = os.getenv("KB_TYPE", "managed").strip().lower()
if KB_TYPE not in ("managed", "vector"):
    raise ValueError(f"KB_TYPE must be 'managed' or 'vector', not {KB_TYPE!r}")
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_PREFIX = os.getenv("S3_PREFIX", "contracts/")

# Bedrock chat model used by the router, metadata agent and merge step.
# amazon.nova-micro-v1:0 is the default used elsewhere in this repo. If the
# router picks the wrong route, try a stronger model.
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")

# v2 only: Postgres with the contract metadata table
POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql://lawfirm:lawfirm@localhost:5433/lawfirm")

AS_OF_DATE = date.fromisoformat(os.getenv("AS_OF_DATE", "2026-12-01"))
