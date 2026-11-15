import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# LOG_DIR = Path.home() / ".mcp-logs"          # or an env var / absolute path
LOG_DIR = Path(__file__).resolve().parent / "mcp-logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logging(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

     # Prevent duplicate handlers
    if logger.handlers:
        return logger
    fmt = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(filename)s: %(funcName)s: %(message)s"
    )


    # 1. Rotating file: survives restarts, doesn't grow forever
    fh = RotatingFileHandler(
        LOG_DIR / "shared-logging.log",
        maxBytes=5_000_000,   # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # 2. stderr: still useful in Inspector / Claude Desktop's own logs
    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger

# logger = setup_logging()