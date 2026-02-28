import pytest
from core.db import Database
from psycopg2 import sql

def test_database_initialization(mocker):
    # Mock do psycopg2.connect
    mock_connect = mocker.patch("psycopg2.connect")
    
    db = Database("postgresql://fake:password@localhost/testdb")
    
    # Verifica que não conecta ao iniciar
    mock_connect.assert_not_called()
    
    # Acessar a propriedade connection deve conectar
    conn = db.connection
    mock_connect.assert_called_once_with("postgresql://fake:password@localhost/testdb")
    assert conn == mock_connect.return_value

def test_database_context_manager(mocker):
    # Patch psycopg2.connect 
    mock_connect = mocker.patch("core.db.psycopg2.connect")
    
    # precisamos garantir que mock_connect.return_value (connection mock) tem a propriedade closed falsy pra classe fechar
    mock_conn = mock_connect.return_value
    mock_conn.closed = False
    
    with Database("fake_url") as db:
        assert db.database_url == "fake_url"
        # Force connection initialization
        c = db.connection
        
    mock_conn.close.assert_called_once()

def test_execute_and_fetch(mocker):
    mock_connect = mocker.patch("psycopg2.connect")
    mock_cursor = mock_connect.return_value.cursor.return_value
    
    db = Database("fake_url")
    
    # Mock do fetchall
    mock_cursor.fetchall.return_value = [{"id": 1, "name": "Python"}]
    
    result = db.fetch_all("SELECT * FROM test", ())
    
    mock_cursor.execute.assert_called_with("SELECT * FROM test", ())
    assert result == [{"id": 1, "name": "Python"}]

def test_insert_security(mocker):
    mock_connect = mocker.patch("psycopg2.connect")
    mock_cursor = mock_connect.return_value.cursor.return_value
    
    # Mock do row RETURNING
    mock_cursor.fetchone.return_value = {"id": 10}
    
    db = Database("fake_url")
    data = {"name": "Python", "total_seconds": 3600}
    
    res_id = db.insert("languages", data)
    
    # Garante que insert() usa execute() corretamente com dict_values tuple
    assert res_id == 10
    args, kwargs = mock_cursor.execute.call_args
    assert args[1] == ("Python", 3600)
