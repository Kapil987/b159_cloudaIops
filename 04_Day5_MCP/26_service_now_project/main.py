from __future__ import annotations
import os
import uvicorn
from dotenv import load_dotenv
load_dotenv()

def main() -> None:
    SERVICENOW_INSTANCE=os.getenv("SERVICENOW_INSTANCE")
    print(f"ServiceNow Instance: {SERVICENOW_INSTANCE}")
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
