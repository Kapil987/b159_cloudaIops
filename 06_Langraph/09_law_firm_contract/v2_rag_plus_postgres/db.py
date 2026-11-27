"""
The metadata agent's tools: a few fixed, read-only queries.

Why fixed queries and not "let the LLM write SQL": the LLM only picks WHICH tool
to run and a number of days. Our code runs the SQL, and our code adds
`client_id = %s` to every query. So the model cannot reach another client's rows,
and there is nothing to inject into.
"""
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, LiteralString

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import psycopg
from psycopg.rows import DictRow, dict_row

from common.config import POSTGRES_DSN

_COLUMNS: LiteralString = """contract_id, counterparty, contract_type, effective_date, expiry_date,
              notice_days, auto_renew, annual_value,
              (expiry_date - notice_days) AS notice_deadline"""


def _query(sql: LiteralString, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    # Naming the row type (DictRow) tells type checkers that rows come back as dicts, not tuples.
    # connect_timeout: fail in 5 seconds with a clear error if Postgres is not running,
    # instead of leaving the app hanging.
    with psycopg.Connection[DictRow].connect(POSTGRES_DSN, row_factory=dict_row, connect_timeout=5) as conn:
        return conn.execute(sql, params).fetchall()


def list_contracts(client_id: str, as_of: date, days: int = 0, counterparty: str = "") -> list[dict[str, Any]]:
    """Every contract for this client."""
    return _query(f"SELECT {_COLUMNS} FROM contracts WHERE client_id = %s ORDER BY expiry_date",
                  (client_id,))


def expiring_within(client_id: str, as_of: date, days: int, counterparty: str = "") -> list[dict[str, Any]]:
    """Contracts whose expiry date falls between as_of and as_of + days."""
    return _query(
        f"SELECT {_COLUMNS} FROM contracts "
        "WHERE client_id = %s AND expiry_date BETWEEN %s AND %s ORDER BY expiry_date",
        (client_id, as_of, as_of + timedelta(days=days)))


def auto_renewing_within(client_id: str, as_of: date, days: int, counterparty: str = "") -> list[dict[str, Any]]:
    """Like expiring_within, but only contracts that renew by themselves."""
    return _query(
        f"SELECT {_COLUMNS} FROM contracts "
        "WHERE client_id = %s AND auto_renew AND expiry_date BETWEEN %s AND %s ORDER BY expiry_date",
        (client_id, as_of, as_of + timedelta(days=days)))


def find_by_counterparty(client_id: str, as_of: date, days: int = 0, counterparty: str = "") -> list[dict[str, Any]]:
    """Contracts with a company whose name contains the given text."""
    return _query(
        f"SELECT {_COLUMNS} FROM contracts "
        "WHERE client_id = %s AND counterparty ILIKE %s ORDER BY expiry_date",
        (client_id, f"%{counterparty}%"))


# The menu the LLM picks from. Every function takes (client_id, as_of, days, counterparty),
# and ignores the ones it does not need, so the caller can treat them all the same.
TOOLS = {
    "list_contracts": list_contracts,
    "expiring_within": expiring_within,
    "auto_renewing_within": auto_renewing_within,
    "find_by_counterparty": find_by_counterparty,
}
