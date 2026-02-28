import pytest
import datetime
from src.orchestrator.orchestrator import WakaTimeOrchestrator
from core.api import WakaTimeAPIError
from core.models import WakaTimeSummariesResponse

def test_extract_and_save_success(mocker):
    # Mock das entidades que o Orquestrador consome
    mock_api = mocker.patch("src.orchestrator.orchestrator.WakaTimeAPI")
    mock_api_instance = mock_api.return_value.__enter__.return_value
    
    # Criamos um mock de "DailySummary" válido retornado pela API MOCKED
    mock_summary = mocker.MagicMock()
    mock_summary.grand_total.total_seconds = 7200 # 2 horas
    mock_api_instance.get_summaries_for_date.return_value = mock_summary
    
    mock_repo = mocker.patch("src.orchestrator.orchestrator.WakaTimeRepository")
    mock_repo_instance = mock_repo.return_value
    
    mock_email = mocker.patch("src.orchestrator.orchestrator.EmailSender")
    
    # Mock config flags (assume-se que conftest já preenche as os.environ mas config global carrega antes, 
    # por garantia, mockamos a variável no módulo)
    mocker.patch("src.orchestrator.orchestrator.ENABLE_EMAIL_INSIGHTS", True)
    
    orchestrator = WakaTimeOrchestrator("fake-token")
    # Substituir os sub-componentes pelo mock
    orchestrator.repo = mock_repo_instance
    # O email_sender instanciado já é mock (patch)
    
    target = datetime.date(2026, 2, 27)
    
    # Testar fluxo extrair e salvar
    result = orchestrator.extract_and_save(target)
    
    # Validações
    assert result is True
    # Verificamos se pegou a info baseada na data alvo
    mock_api_instance.get_summaries_for_date.assert_called_once_with(target)
    # Verificamos se o repo mandou salvar enviando o obj de summary
    mock_repo_instance.save_summary.assert_called_once_with(mock_summary)
    
def test_extract_and_save_api_error(mocker):
    # Mock the API so it raises an Error
    mock_api = mocker.patch("src.orchestrator.orchestrator.WakaTimeAPI")
    mock_api_instance = mock_api.return_value.__enter__.return_value
    mock_api_instance.get_summaries_for_date.side_effect = WakaTimeAPIError("API rate limit exceeded")
    
    mock_repo = mocker.patch("src.orchestrator.orchestrator.WakaTimeRepository")
    mock_repo_instance = mock_repo.return_value
    
    orchestrator = WakaTimeOrchestrator("fake-token")
    orchestrator.repo = mock_repo_instance
    
    result = orchestrator.extract_and_save(datetime.date(2026, 2, 27))
    
    # Verifica que o fluxo de erro foi bem sucedido em "falhar silenciosamente" retornando False
    assert result is False
    # Garante que repo saving NÃO FOI CHAMADO
    mock_repo_instance.save_summary.assert_not_called()

def test_backfill(mocker):
    # Precisamos mockar o WakaTimeRepository para evitar inicialização da DB real/SQLite
    mock_repo = mocker.patch("src.orchestrator.orchestrator.WakaTimeRepository")
    mock_api = mocker.patch("src.orchestrator.orchestrator.WakaTimeAPI")
    
    orchestrator = WakaTimeOrchestrator("fake-token")
    orchestrator.repo = mock_repo.return_value
    
    # Mock do próprio extract_and_save para testar loop no backfill
    mocker.patch.object(orchestrator, "extract_and_save", return_value=True)
    
    start_date = datetime.date(2026, 2, 25)
    end_date = datetime.date(2026, 2, 27)
    
    # Desativa time.sleep no backfill para agilizar o teste
    mocker.patch("src.orchestrator.orchestrator.time.sleep")
    
    success_count = orchestrator.backfill(start_date, end_date)
    
    # 25, 26, 27 = 3 dias
    assert success_count == 3
    assert orchestrator.extract_and_save.call_count == 3
