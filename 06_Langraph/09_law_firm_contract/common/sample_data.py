"""
The sample contracts, described once.

Two places use this list so they can never disagree:
- scripts/upload_to_kb.py builds the Bedrock metadata files (client_id,
  contract_id, ...) from it.
- v2_rag_plus_postgres/seed.py loads the same rows into the Postgres table.

The full wording of each contract lives in sample_contracts/<file>.
All of this is fictional teaching data.
"""
from datetime import date
from typing import TypedDict


class Contract(TypedDict):
    """One sample contract. A TypedDict gives every key its own type, so
    c["file"] is a str and c["expiry_date"] is a date (a plain dict would make
    every value a str | date | int | bool mix, and editors complain)."""
    contract_id: str
    client_id: str
    counterparty: str
    contract_type: str
    effective_date: date
    expiry_date: date
    notice_days: int
    auto_renew: bool
    annual_value: int
    file: str


CONTRACTS: list[Contract] = [
    # --- Nova Foods (client_id = nova_foods) ---------------------------------
    Contract(contract_id="NOV-001", client_id="nova_foods", counterparty="CloudServe Inc",
         contract_type="Software services", effective_date=date(2025, 1, 1),
         expiry_date=date(2027, 12, 31), notice_days=90, auto_renew=True,
         annual_value=200_000, file="NOV-001_cloudserve_saas.md"),
    Contract(contract_id="NOV-002", client_id="nova_foods", counterparty="Prime Logistics Parks Pvt Ltd",
         contract_type="Warehouse lease", effective_date=date(2024, 3, 1),
         expiry_date=date(2027, 2, 28), notice_days=60, auto_renew=True,
         annual_value=360_000, file="NOV-002_prime_logistics_lease.md"),
    Contract(contract_id="NOV-003", client_id="nova_foods", counterparty="BrightMart Retail Ltd",
         contract_type="Customer supply", effective_date=date(2024, 2, 16),
         expiry_date=date(2027, 2, 15), notice_days=30, auto_renew=True,
         annual_value=1_200_000, file="NOV-003_brightmart_supply.md"),
    Contract(contract_id="NOV-004", client_id="nova_foods", counterparty="Quickship Couriers LLP",
         contract_type="Delivery services", effective_date=date(2025, 1, 21),
         expiry_date=date(2027, 1, 20), notice_days=30, auto_renew=False,
         annual_value=150_000, file="NOV-004_quickship_couriers.md"),
    Contract(contract_id="NOV-005", client_id="nova_foods", counterparty="Orbit Payments Inc",
         contract_type="Payment processing", effective_date=date(2025, 7, 1),
         expiry_date=date(2028, 6, 30), notice_days=90, auto_renew=True,
         annual_value=90_000, file="NOV-005_orbit_payments.md"),
    Contract(contract_id="NOV-006", client_id="nova_foods", counterparty="GreenLine Packaging Co",
         contract_type="Packaging supply", effective_date=date(2025, 2, 6),
         expiry_date=date(2027, 2, 5), notice_days=45, auto_renew=True,
         annual_value=480_000, file="NOV-006_greenline_packaging.md"),
    # --- Greenfield Retail (client_id = greenfield_retail) -------------------
    Contract(contract_id="GRN-001", client_id="greenfield_retail", counterparty="CloudServe Inc",
         contract_type="Software services", effective_date=date(2025, 6, 1),
         expiry_date=date(2027, 5, 31), notice_days=60, auto_renew=True,
         annual_value=50_000, file="GRN-001_cloudserve_saas.md"),
    Contract(contract_id="GRN-002", client_id="greenfield_retail", counterparty="Metro Realty Partners",
         contract_type="Shop lease", effective_date=date(2024, 1, 11),
         expiry_date=date(2027, 1, 10), notice_days=60, auto_renew=True,
         annual_value=120_000, file="GRN-002_metro_realty_lease.md"),
]
