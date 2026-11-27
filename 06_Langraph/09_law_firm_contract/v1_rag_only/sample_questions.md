# v1 sample questions

Questions to try in the v1 app, with the answer you should expect. Log in as Priya (Nova Foods) or Arjun (Greenfield Retail), as shown in each table.

The expected answers come straight from the sample contract text in [sample_contracts](../sample_contracts). Check each answer against the **Passages used** panel. The model's wording will vary, so compare the facts, not the sentences.

## Priya (Nova Foods)

| Ask | Expected answer |
|---|---|
| What does the liability clause say in the CloudServe contract? | Capped at the fees Nova paid in the preceding 12 months [NOV-001] |
| How much does Nova pay CloudServe, and when is it invoiced? | USD 200,000 a year, invoiced in advance on each anniversary [NOV-001] |
| What happens to the BrightMart supply agreement if nobody gives notice? | Renews automatically for 1 year, unless notice is given 30 days before expiry [NOV-003] |
| Is there any limit on liability in the Quickship Couriers agreement? | No cap or ceiling for either party [NOV-004] |
| Which contract has an exception to its liability cap? | Orbit Payments: the cap does not apply to data breaches or fraud [NOV-005] |
| Which law governs the Orbit Payments agreement? | State of Delaware [NOV-005] |
| How can Nova end the Prime Logistics lease early? | Only by paying the remaining rent for the next 3 months [NOV-002] |

## Arjun (Greenfield Retail)

| Ask | Expected answer |
|---|---|
| What does the liability clause say in the CloudServe contract? | A flat cap of USD 50,000, whatever the cause [GRN-001] |
| How much does Greenfield pay CloudServe? | USD 50,000 a year [GRN-001] |
| How can Greenfield end the shop lease early? | 6 months' notice and a fee of 2 months' rent [GRN-002] |
| What is the renewal notice period for the Metro Realty lease? | 60 days before expiry. It renews for 1 year if no notice is given [GRN-002] |

Same question as Priya, different client, different contract and different cap. That is the client filter working.

## Client isolation test

Each of these should end with an answer saying it has nothing about that, because the contract belongs to the other client. The search is limited to the logged-in client, so the **Passages used** panel should never show the other client's contract text. The exact wording of the "nothing found" answer will vary.

| Log in as | Ask | Expected |
|---|---|---|
| Arjun | What does the BrightMart contract say about liability? | Not found (it is Nova's) |
| Priya | How much is the Metro Realty rent? | Not found (it is Greenfield's) |
| Priya | Tell me about Greenfield Retail's contracts | Not found |

## Questions v1 should struggle with

These show why [v2](../v2_rag_plus_postgres/README.md) exists.

| Ask | Why v1 fails |
|---|---|
| Which contracts expire in the next 90 days? | It has no dates table and doesn't know today's date |
| How many contracts does Nova have? | It only sees the few passages that come back, not a full list |
| Which contracts auto-renew within 90 days and have unlimited liability? | It needs the date filter first. The answer will be partial or wrong |
| Which contracts have unlimited liability? | May find some of NOV-003, NOV-004 and NOV-006 but not all, because only the top 5 passages come back |

---

# Notes: questions and answers

## Q: Are the expiry dates in the contract itself?

**A:** Yes. Section 2, "Term and Renewal", of every sample contract gives the start date, the expiry date and the notice period.
All 8 contracts were checked: the text matches the Postgres rows exactly.
A question about one contract, like "When does the CloudServe contract expire?", works fine in v1.

## Q: Then why can't v1 answer "Which contracts expire in the next 90 days?"

**A:** Three reasons:
- v1 doesn't know today's date, and the contract text doesn't say what today is.
- Only the top 5 or so passages come back, so it may not have seen every contract's date.
- Comparing dates across many text passages is unreliable for an LLM. A SQL `BETWEEN` is exact.

## Q: Why are the same dates also stored in Postgres?

**A:** Postgres gives exact, complete answers: one query sees every contract and filters by date.
In this demo both copies are typed by hand and agree.
In a real system the contract text is the source of truth, and the table is extracted from it, by hand or by an LLM when the contract is uploaded.
Keeping the two in sync is a real maintenance problem, and a good discussion point.

## Q: Is v1 guaranteed to fail on the "struggle" questions?

**A:** No. "Fails" is a tendency, not a guarantee.
If the retrieved passages happen to contain the right dates, v1 may give a plausible answer.
That is luck, and it can't be trusted: the answer can change between runs.
v2 answers from a database query, so the same question gives the same answer every time.
