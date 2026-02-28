import secrets
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from core.config import READONLY_API_KEY

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verifica se a API Key é válida usando comparação de tempo constante para prevenir timing attacks."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key não fornecida. Use o header X-API-Key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Previne exception no compare_digest se len for diferente, compare_digest lida bem com isso
    # Em Python 3.10+, compare_digest suporta types mistos (None) e len distintos de forma segura
    if not secrets.compare_digest(api_key, READONLY_API_KEY):
        raise HTTPException(
            status_code=401,
            detail="API Key inválida.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return "readonly"
