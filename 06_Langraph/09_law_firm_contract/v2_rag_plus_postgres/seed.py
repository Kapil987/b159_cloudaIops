"""
Create the contracts table and load the sample rows. Safe to run again.

Run from the project root:
    uv run python v2_rag_plus_postgres/seed.py
"""
import sys
from pathlib import Path
from typing import LiteralString, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import psycopg

from common.config import POSTGRES_DSN
from common.sample_data import CONTRACTS

# Our own file, so it is safe to treat as a literal SQL string (psycopg's type hints ask for that).
SCHEMA = cast(LiteralString, (Path(__file__).parent / "schema.sql").read_text())

UPSERT: LiteralString = """
INSERT INTO contracts (contract_id, client_id, counterparty, contract_type,
                       effective_date, expiry_date, notice_days, auto_renew,
                       annual_value, file_name)
VALUES (%(contract_id)s, %(client_id)s, %(counterparty)s, %(contract_type)s,
        %(effective_date)s, %(expiry_date)s, %(notice_days)s, %(auto_renew)s,
        %(annual_value)s, %(file)s)
ON CONFLICT (contract_id) DO UPDATE SET
    client_id = EXCLUDED.client_id, counterparty = EXCLUDED.counterparty,
    contract_type = EXCLUDED.contract_type, effective_date = EXCLUDED.effective_date,
    expiry_date = EXCLUDED.expiry_date, notice_days = EXCLUDED.notice_days,
    auto_renew = EXCLUDED.auto_renew, annual_value = EXCLUDED.annual_value,
    file_name = EXCLUDED.file_name
"""

if __name__ == "__main__":
    with psycopg.connect(POSTGRES_DSN) as conn:
        conn.execute(SCHEMA)
        for row in CONTRACTS:
            conn.execute(UPSERT, row)
    print(f"Loaded {len(CONTRACTS)} contracts.")
