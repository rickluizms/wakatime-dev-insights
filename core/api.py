"""
Módulo de integração com a API do WakaTime.
"""

import os
from datetime import date, datetime, timedelta
from typing import List, Optional, Union
from pydantic import ValidationError

import requests
from requests.auth import HTTPBasicAuth

from core.models import WakaTimeSummariesResponse, DailySummary


class WakaTimeAPIError(Exception):
    """Exceção customizada para erros da API do WakaTime."""
    pass


class WakaTimeAPI:
    """
    Cliente para a API do WakaTime.
    
    Gerencia autenticação e requisições para obter dados de produtividade.
    Projetado para ser utilizado por um orquestrador em execuções cronológicas.
    
    Exemplo de uso:
        api = WakaTimeAPI(api_token="seu_token")
        summaries = api.get_summaries(start="2026-01-01", end="2026-01-15")
    """
    
    BASE_URL = "https://wakatime.com/api/v1"
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Inicializa o cliente da API do WakaTime.
        
        Args:
            api_token: Token de API do WakaTime. Se não fornecido,
                      tenta obter da variável de ambiente WAKATIME_API_TOKEN.
        """
        self.api_token = api_token or os.getenv("WAKATIME_API_TOKEN")
        
        if not self.api_token:
            raise WakaTimeAPIError(
                "Token de API não fornecido. Passe como argumento ou "
                "defina a variável de ambiente WAKATIME_API_TOKEN."
            )
        
        self._session = requests.Session()
        self._session.auth = HTTPBasicAuth(self.api_token, "")
        self._session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _request(
        self, 
        endpoint: str, 
        params: Optional[dict] = None
    ) -> dict:
        """
        Realiza uma requisição GET para a API.
        
        Args:
            endpoint: Endpoint da API (ex: "/users/current/summaries").
            params: Parâmetros de query string.
            
        Returns:
            Resposta JSON da API.
            
        Raises:
            WakaTimeAPIError: Se a requisição falhar.
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self._session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "N/A"
            raise WakaTimeAPIError(
                f"Erro HTTP {status_code} ao acessar {endpoint}: {e}"
            )
        except requests.exceptions.RequestException as e:
            raise WakaTimeAPIError(f"Erro de conexão: {e}")
    
    @staticmethod
    def _format_date(d: Union[str, date, datetime]) -> str:
        """Converte uma data para o formato YYYY-MM-DD."""
        if isinstance(d, str):
            return d
        return d.strftime("%Y-%m-%d")
    
    def get_summaries(
        self,
        start: Union[str, date, datetime],
        end: Union[str, date, datetime],
        project: Optional[str] = None,
        branches: Optional[str] = None,
        timeout: Optional[int] = None,
        writes_only: bool = False
    ) -> WakaTimeSummariesResponse:
        """
        Obtém resumos de atividade para um período.
        
        Args:
            start: Data inicial (YYYY-MM-DD ou objeto date/datetime).
            end: Data final (YYYY-MM-DD ou objeto date/datetime).
            project: Filtrar por projeto específico.
            branches: Filtrar por branches específicas.
            timeout: Timeout da requisição em segundos.
            writes_only: Se True, retorna apenas tempo de escrita.
            
        Returns:
            WakaTimeSummariesResponse com os dados do período.
        """
        params = {
            "start": self._format_date(start),
            "end": self._format_date(end),
        }
        
        if project:
            params["project"] = project
        if branches:
            params["branches"] = branches
        if timeout:
            params["timeout"] = timeout
        if writes_only:
            params["writes_only"] = "true"
        
        data = self._request("/users/current/summaries", params=params)
        return WakaTimeSummariesResponse(**data)
    
    def get_summaries_for_date(
        self,
        target_date: Union[str, date, datetime]
    ) -> DailySummary:
        """
        Obtém o resumo de atividade para uma data específica.
        
        Args:
            target_date: Data alvo (YYYY-MM-DD ou objeto date/datetime).
            
        Returns:
            DailySummary com os dados do dia.
        """
        formatted_date = self._format_date(target_date)
        response = self.get_summaries(start=formatted_date, end=formatted_date)
        
        if not response.data:
            raise WakaTimeAPIError(f"Nenhum dado encontrado para {formatted_date}")
        
        return response.data[0]
    
    def get_today_summary(self) -> DailySummary:
        """
        Obtém o resumo de atividade do dia atual.
        
        Returns:
            DailySummary com os dados de hoje.
        """
        return self.get_summaries_for_date(date.today())
    
    def get_yesterday_summary(self) -> DailySummary:
        """
        Obtém o resumo de atividade do dia anterior.
        
        Returns:
            DailySummary com os dados de ontem.
        """
        yesterday = date.today() - timedelta(days=1)
        return self.get_summaries_for_date(yesterday)
    
    def get_week_summaries(self) -> WakaTimeSummariesResponse:
        """
        Obtém resumos dos últimos 7 dias.
        
        Returns:
            WakaTimeSummariesResponse com dados da semana.
        """
        end = date.today()
        start = end - timedelta(days=6)
        return self.get_summaries(start=start, end=end)
    
    def get_month_summaries(self) -> WakaTimeSummariesResponse:
        """
        Obtém resumos dos últimos 30 dias.
        
        Returns:
            WakaTimeSummariesResponse com dados do mês.
        """
        end = date.today()
        start = end - timedelta(days=29)
        return self.get_summaries(start=start, end=end)
    
    def get_daily_summaries_list(
        self,
        start: Union[str, date, datetime],
        end: Union[str, date, datetime]
    ) -> List[DailySummary]:
        """
        Obtém lista de resumos diários para um período.
        Útil para processamento individual de cada dia.
        
        Args:
            start: Data inicial.
            end: Data final.
            
        Returns:
            Lista de DailySummary para cada dia do período.
        """
        response = self.get_summaries(start=start, end=end)
        return response.data
    
    def get_user_info(self) -> dict:
        """
        Obtém informações do usuário atual.
        
        Returns:
            Dicionário com dados do usuário.
        """
        data = self._request("/users/current")
        return data.get("data", {})
    
    def is_authenticated(self) -> bool:
        """
        Verifica se o token de API é válido.
        
        Returns:
            True se autenticado, False caso contrário.
        """
        try:
            self.get_user_info()
            return True
        except WakaTimeAPIError:
            return False
    
    def close(self) -> None:
        """Fecha a sessão HTTP."""
        self._session.close()
    
    def __enter__(self) -> "WakaTimeAPI":
        """Suporte para uso com 'with' statement."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Fecha a sessão ao sair do contexto."""
        self.close()
