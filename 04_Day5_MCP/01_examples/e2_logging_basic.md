# Python Logging Levels

Python has 5 standard logging levels (plus `NOTSET`).

| Level | Value | When to use |
| :--- | :---: | :--- |
| **DEBUG** | 10 | Detailed diagnostic information for debugging. |
| **INFO** | 20 | Normal application events, e.g. server started, ticket created. |
| **WARNING** | 30 | Something unexpected, but the application can continue. |
| **ERROR** | 40 | An operation failed, but the application may continue. |
| **CRITICAL** | 50 | A serious failure that may prevent the application from continuing. |

---

## How Log Levels Work

> **Important:** A higher configured log level means fewer messages are logged. Python logging levels act as thresholds. A message is logged when its level is greater than or equal to the configured level.

### Examples:
* **`logger.setLevel(logging.DEBUG)`**  
  All levels are logged because `DEBUG` is the lowest level.
* **`logger.setLevel(logging.WARNING)`**  
  Only `WARNING`, `ERROR`, and `CRITICAL` are logged. `DEBUG` and `INFO` are skipped.

---

## Quick Reference Matrix

| Configured Level | DEBUG | INFO | WARNING | ERROR | CRITICAL |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **DEBUG** | Yes | Yes | Yes | Yes | Yes |
| **INFO** | No | Yes | Yes | Yes | Yes |
| **WARNING** | No | No | Yes | Yes | Yes |
| **ERROR** | No | No | No | Yes | Yes |
| **CRITICAL** | No | No | No | No | Yes |

---

## Code Example

```python
logger.debug("Request payload received")
logger.info("Ticket created successfully")
logger.warning("ServiceNow response is slow")
logger.error("Failed to create ticket")
logger.critical("Database connection unavailable")