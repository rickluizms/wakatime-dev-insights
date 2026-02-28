import pytest
import datetime
from core.api import WakaTimeAPI, WakaTimeAPIError
from core.models import WakaTimeSummariesResponse

def test_api_initialization():
    api = WakaTimeAPI("test-token")
    assert api.api_token == "test-token"
    assert api._session.auth is not None

def test_api_context_manager():
    with WakaTimeAPI("test-token") as api:
        assert api.api_token == "test-token"
    # Sessão deve estar fechada (Mock interno do requests não fecha estritamente a porta de socket
    # mas o método close() do requests.Session() é invocado)

def test_get_summaries_for_date_success(mocker):
    # Mock do requests.Session.get para não acessar a internet de verdade
    mock_get = mocker.patch("requests.Session.get")
    
    # Criamos um Payload Fake
    fake_response_data = {
        "start": "2026-02-27T00:00:00Z",
        "end": "2026-02-27T23:59:59Z",
        "cumulative_total": {"seconds": 3600, "text": "1 hr", "decimal": "1.0", "digital": "1:00"},
        "daily_average": {"holidays": 0, "days_including_holidays": 1, "days_minus_holidays": 1, "seconds": 3600, "text": "1 hr", "seconds_including_other_language": 3600, "text_including_other_language": "1 hr"},
        "data": [
            {
                "grand_total": {"total_seconds": 3600, "digital": "1:00", "hours": 1, "minutes": 0, "text": "1 hr", "ai_additions": 0, "ai_deletions": 0, "human_additions": 0, "human_deletions": 0},
                "range": {"date": "2026-02-27", "start": "2026-02-27T00:00:00Z", "end": "2026-02-27T23:59:59Z", "text": "Today", "timezone": "UTC"},
                "languages": [{"name": "Python", "total_seconds": 1800, "percent": 50, "digital": "0:30", "text": "30 mins", "hours": 0, "minutes": 30, "seconds": 0}],
                "projects": [{"name": "DevInsights", "total_seconds": 3600, "percent": 100, "digital": "1:00", "text": "1 hr", "hours": 1, "minutes": 0, "seconds": 0, "ai_additions": 0, "ai_deletions": 0, "human_additions": 0, "human_deletions": 0}]
            }
        ]
    }
    
    # Configuramos o retorno do Mock
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = fake_response_data
    
    with WakaTimeAPI("token") as api:
        summary = api.get_summaries_for_date(datetime.date(2026, 2, 27))
        
    assert summary is not None
    assert summary.range.date == "2026-02-27"
    assert summary.grand_total.total_seconds == 3600.0
    assert summary.languages[0].name == "Python"
    assert summary.projects[0].name == "DevInsights"

def test_get_summaries_for_date_error(mocker):
    mock_get = mocker.patch("requests.Session.get")
    # Forçar erro HTTP 401 Unauthorized
    import requests
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error")
    
    with WakaTimeAPI("token") as api:
        with pytest.raises(WakaTimeAPIError) as exc:
            api.get_summaries_for_date(datetime.date(2026, 2, 27))
            
    assert "401 Client Error" in str(exc.value)
