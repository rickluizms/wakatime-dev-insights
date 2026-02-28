"""
Módulo de conexão e operações com banco de dados PostgreSQL.
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()


class Database:
    """
    Classe para gerenciar conexões e operações com banco de dados PostgreSQL.
    
    Exemplo de uso:
        db = Database()  # Usa DATABASE_URL do .env
        db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT)")
        db.insert("users", {"name": "João"})
        users = db.fetch_all("SELECT * FROM users")
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Inicializa a conexão com o banco de dados.
        
        Args:
            database_url: URL de conexão PostgreSQL. Se não fornecida,
                         usa a variável de ambiente DATABASE_URL.
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL não fornecida. Passe como argumento ou "
                "defina a variável de ambiente DATABASE_URL no .env"
            )
        
        self._connection = None
    
    @property
    def connection(self):
        """Retorna a conexão ativa ou cria uma nova."""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(self.database_url)
        return self._connection
    
    def close(self) -> None:
        """Fecha a conexão com o banco de dados."""
        if self._connection is not None and not self._connection.closed:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """
        Context manager para obter um cursor do banco de dados.
        Garante commit em caso de sucesso e rollback em caso de erro.
        
        Args:
            dict_cursor: Se True, retorna resultados como dicionários.
        """
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = self.connection.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()
    
    def execute(self, query: str, params: Tuple = ()) -> None:
        """
        Executa uma query SQL.
        
        Args:
            query: Query SQL a ser executada.
            params: Parâmetros para a query (previne SQL injection).
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """
        Executa uma query SQL múltiplas vezes com diferentes parâmetros.
        
        Args:
            query: Query SQL a ser executada.
            params_list: Lista de tuplas com parâmetros.
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
    
    def execute_script(self, script: str) -> None:
        """
        Executa um script SQL com múltiplas instruções.
        
        Args:
            script: Script SQL completo (separado por ; )
        """
        with self.get_cursor() as cursor:
            cursor.execute(script)
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Executa uma query e retorna um único registro.
        
        Args:
            query: Query SQL SELECT.
            params: Parâmetros para a query.
            
        Returns:
            Dicionário com o registro ou None se não encontrado.
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Executa uma query e retorna todos os registros.
        
        Args:
            query: Query SQL SELECT.
            params: Parâmetros para a query.
            
        Returns:
            Lista de dicionários com os registros.
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Insere um registro em uma tabela.
        """
        from psycopg2 import sql
        
        columns = data.keys()
        
        # Constrói query de forma segura contra SQL Injection de nomes de tabelas/colunas
        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING id").format(
            table=sql.Identifier(table),
            fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
            values=sql.SQL(", ").join(sql.Placeholder() * len(data))
        )
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, tuple(data.values()))
                result = cursor.fetchone()
                return result["id"] if result else None
        except psycopg2.errors.UndefinedColumn:
            # Tabela não tem coluna 'id', faz insert sem RETURNING
            query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
                table=sql.Identifier(table),
                fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
                values=sql.SQL(", ").join(sql.Placeholder() * len(data))
            )
            with self.get_cursor() as cursor:
                cursor.execute(query, tuple(data.values()))
                return None
    
    def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """
        Insere múltiplos registros em uma tabela.
        """
        if not data_list:
            return 0
            
        from psycopg2 import sql
        
        columns = data_list[0].keys()
        
        # Constrói query de forma segura contra SQL Injection
        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
            table=sql.Identifier(table),
            fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
            values=sql.SQL(", ").join(sql.Placeholder() * len(data_list[0]))
        )
        
        with self.get_cursor() as cursor:
            cursor.executemany(query, [tuple(d.values()) for d in data_list])
            return cursor.rowcount
    
    def update(
        self, 
        table: str, 
        data: Dict[str, Any], 
        where: str, 
        where_params: Tuple = ()
    ) -> int:
        """
        Atualiza registros em uma tabela.
        """
        from psycopg2 import sql
        
        # Constrói a cláusula SET "coluna = %s" de forma segura
        set_items = []
        for key in data.keys():
            set_items.append(sql.SQL("{key} = %s").format(key=sql.Identifier(key)))
            
        set_clause = sql.SQL(", ").join(set_items)
        
        # NOTA: O 'where' é assumido como sendo parametrizado corretamente chamando a função
        # Em uma implementação perfeita ele também usaria sql.SQL, mas devido à sua natureza 
        # mista (ex: "id = %s AND date >= %s"), nós focamos aqui em proteger o nome da tabela
        # e as chaves do dicionário 'data' que vêm dinamicamente.
        
        query = sql.SQL("UPDATE {table} SET {set_clause} WHERE {where}").format(
            table=sql.Identifier(table),
            set_clause=set_clause,
            where=sql.SQL(where) 
        )
        
        params = tuple(data.values()) + where_params
        
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def delete(self, table: str, where: str, where_params: Tuple = ()) -> int:
        """
        Deleta registros de uma tabela.
        """
        from psycopg2 import sql
        
        query = sql.SQL("DELETE FROM {table} WHERE {where}").format(
            table=sql.Identifier(table),
            where=sql.SQL(where)
        )
        
        with self.get_cursor() as cursor:
            cursor.execute(query, where_params)
            return cursor.rowcount
    
    def table_exists(self, table_name: str) -> bool:
        """
        Verifica se uma tabela existe no banco de dados.
        
        Args:
            table_name: Nome da tabela.
            
        Returns:
            True se a tabela existe, False caso contrário.
        """
        result = self.fetch_one(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = %s
            """,
            (table_name,)
        )
        return result is not None
    
    def get_tables(self) -> List[str]:
        """
        Retorna lista de todas as tabelas do banco de dados.
        
        Returns:
            Lista com os nomes das tabelas.
        """
        rows = self.fetch_all(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
            """
        )
        return [row["table_name"] for row in rows]
    
    def __enter__(self) -> "Database":
        """Suporte para uso com 'with' statement."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Fecha a conexão ao sair do contexto."""
        self.close()
    
    def __del__(self) -> None:
        """Garante que a conexão seja fechada ao destruir o objeto."""
        self.close()
