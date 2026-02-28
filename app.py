"""
Ponto de entrada da API.
"""
import sys
import os
import uvicorn

# Adiciona o diretório atual ao path para garantir que imports locais funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.main import app

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
