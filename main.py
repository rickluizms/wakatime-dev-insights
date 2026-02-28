"""
Ponto de entrada do Orquestrador WakaTime.
"""
import sys
import os

# Adiciona o diretório atual ao path para garantir que imports locais funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import API_TOKEN, RUN_SCHEDULED, setup_logger
from src.orchestrator.orchestrator import WakaTimeOrchestrator

logger = setup_logger(__name__)

def main():
    if not API_TOKEN:
        logger.error("WAKATIME_API_TOKEN não definido")
        return
    
    orchestrator = WakaTimeOrchestrator(api_token=API_TOKEN)
    
    if RUN_SCHEDULED:
        orchestrator.run_scheduled()
    else:
        orchestrator.run_once()

if __name__ == "__main__":
    main()
