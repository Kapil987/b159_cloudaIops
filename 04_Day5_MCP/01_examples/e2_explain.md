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

```
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
