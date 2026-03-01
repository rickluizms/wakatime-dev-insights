import os
import logging
from dotenv import load_dotenv

load_dotenv()

# ── GLOBAL ────────────────────────────────────────────────────────
API_TOKEN = os.getenv("WAKATIME_API_TOKEN", "")
EXECUTION_TIME = os.getenv("EXECUTION_TIME", "03:15")
RUN_SCHEDULED = os.getenv("RUN_SCHEDULED", "false").lower() == "true"

PREVIOUS_DAYS = int(os.getenv("PREVIOUS_DAYS", "0"))
PREVIOUS_HOURS = int(os.getenv("PREVIOUS_HOURS", "0"))

READONLY_API_KEY = os.getenv("API_KEY_READONLY")

if not READONLY_API_KEY:
    raise ValueError("API_KEY_READONLY não configurada no .env. Proteja sua API especificando uma chave.")

# ── SMTP ────────────────────────────────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER if SMTP_USER else "")
DEVELOPER_NAME = os.getenv("DEVELOPER_NAME", "Desenvolvedor")
DEVELOPER_MAIL = os.getenv("DEVELOPER_MAIL", "[EMAIL_ADDRESS]")
ENABLE_EMAIL_INSIGHTS = os.getenv("ENABLE_EMAIL_INSIGHTS", "true").lower() == "true"

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        
        file_handler = logging.FileHandler("orchestrator.log")
        file_handler.setFormatter(formatter)
        
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger
