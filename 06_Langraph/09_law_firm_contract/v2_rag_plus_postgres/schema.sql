-- One row per contract: the exact facts (dates, flags, amounts).
-- The full wording of each contract lives in the Bedrock Knowledge Base, not here.
CREATE TABLE IF NOT EXISTS contracts (
    contract_id    TEXT PRIMARY KEY,
    client_id      TEXT NOT NULL,          -- which client owns this contract
    counterparty   TEXT NOT NULL,          -- the other company
    contract_type  TEXT NOT NULL,
    effective_date DATE NOT NULL,
    expiry_date    DATE NOT NULL,
    notice_days    INT  NOT NULL,          -- how early notice must be given
    auto_renew     BOOLEAN NOT NULL,
    annual_value   NUMERIC(12, 2),
    file_name      TEXT NOT NULL           -- the matching file in the Knowledge Base
);

CREATE INDEX IF NOT EXISTS idx_contracts_client_expiry ON contracts (client_id, expiry_date);
