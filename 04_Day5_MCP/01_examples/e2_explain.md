## **1. What does this line mean?**

```
ticket_id = f"TICKET-{len(_tickets) + 1:04d}"
```

Let's break it down.

| Expression      | Meaning                                         |
| --------------- | ----------------------------------------------- |
| `f"..."`        | Python f-string                                 |
| `len(_tickets)` | Number of tickets currently stored              |
| `+ 1`           | Generate the next number                        |
| `:04d`          | Format as a 4-digit integer, padding with zeros |
| `TICKET-`       | Fixed text prefix                               |

### **Example execution**

Initially:

```
_tickets = {}
```

**First tool invocation**

len(\_tickets)

**0**

0 + 1

**1**

# **TICKET-0001**

**Second tool invocation**

len(\_tickets)

**1**

# **TICKET-0002**

**Third tool invocation**

len(\_tickets)

**2**

# **TICKET-0003**

### **What does&#x20;**`:04d`**&#x20;do?**

Try these examples:

```python
print(f"{1:04d}")     # 0001print(f"{12:04d}")    # 0012print(f"{123:04d}")   # 0123print(f"{1234:04d}")  # 1234print(f"{12345:04d}") # 12345
```

It means minimum width of four digits, not maximum width.

## **3. One important limitation**

Our example uses:

```
_tickets: dict[str, TicketDraft] = {}
```

This is an in-memory dictionary, not a database.

- Restart Python → all tickets disappear.
- Multiple workers → each worker has its own dictionary.
- Concurrent requests → this ID-generation approach is not safe for production.

For this learning exercise, it is perfectly fine.

```txt
e2-mcp-server/
├── pyproject.toml
├── .env                      # LOG_LEVEL, LOG_DIR, etc. (optional)
├── logs/                     # created at runtime, add to .gitignore
└── src/
    └── ticket_server/
        ├── __init__.py
        ├── main.py           # entry point: configures logging, runs server
        ├── logging_config.py # setup_logging() lives here
        ├── models.py         # TicketDraft, TicketResult
        ├── tools.py          # create_ticket and other tools
        └── storage.py        # in-memory DB (later: real API client)
```


`__init__.py` tells Python that a directory should be treated as a **Python package** (with some nuances in modern Python).

It is commonly placed in directories containing Python modules.

### **1. Example directory structure**

```
my_project/
│
├── main.py
└── ticket_server/
    ├── __init__.py
    ├── tools.py
    └── models.py
```

Because `ticket_server` has `__init__.py`, you can import its modules like this:

```
from ticket_server.tools import create_ticketfrom ticket_server.models import TicketDraft
```

## Logging
A `handler` in Python logging is an object that decides where a log message should be sent. Think of a `logger` as a message producer and `handlers` as destinations for those messages.

`fh.setFormatter(fmt)` tells the file handler **how to format each log message before writing it to the log file**.

### **1. What does&#x20;**`fmt`**&#x20;do?**

You defined:

```
fmt = logging.Formatter( "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
```

This defines the log format.

For example, a log message:

```
logger.info("Creating ServiceNow incident")
```

Will look like:

```
2026-11-15 12:44:10,123 [INFO] e2-structured-tool: Creating ServiceNow incident
```

### **2. What does&#x20;**`fh.setFormatter(fmt)`**&#x20;do?**

```python
fh = RotatingFileHandler(LOG_DIR / "e2-structured-tool.log", maxBytes=5_000_000,backupCount=3,encoding="utf8",)
fh.setFormatter(fmt)
logger.addHandler(fh)
```

- `RotatingFileHandler` decides **where to write logs** and when to rotate files.
- `setFormatter(fmt)` decides **how each log entry should look**.
- `addHandler(fh)` attaches that handler to your logger.

### **3. What about the stderr handler?**

```
sh = logging.StreamHandler(sys.stderr)sh.setFormatter(fmt)logger.addHandler(sh)
```

This creates another output destination.

Your logger now sends the same formatted message to two destinations:

```txt
logger.info("Incident created")
          |
          v
        Logger
          |
     +----+----+
     |         |
     v         v
File Handler  Stream Handler
     |         |
     v         v
 .log file   stderr

```
### **4. Why use both?**

| Handler               | Purpose                                               |
| --------------------- | ----------------------------------------------------- |
| RotatingFileHandler   | Keeps persistent logs even after the MCP server stops |
| StreamHandler(stderr) | Shows logs in MCP Inspector or the host's stderr logs |

**One important MCP detail:** For an MCP server using STDIO transport, avoid logging to `stdout`. The MCP protocol uses stdout for communication. Logging to `stderr` is safe.

In short: `setFormatter()` controls the appearance of logs, while the handler controls where those logs go.