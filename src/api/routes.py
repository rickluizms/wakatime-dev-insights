from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from core.db import Database

from src.api.schemas import (
    DailySummaryResponse, LanguageResponse, ProjectResponse, EditorResponse,
    StatsResponse, LanguageStatsResponse, ProjectStatsResponse, HealthResponse
)
from src.api.security import verify_api_key

router = APIRouter()

from core.config import PREVIOUS_DAYS, PREVIOUS_HOURS

def get_db() -> Database:
    return Database()


@router.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health_check():
    """Verifica o status da API e do banco de dados."""
    with get_db() as db:
        tables = db.get_tables()
        return HealthResponse(
            status="healthy",
            database="connected",
            tables_count=len(tables)
        )


@router.get(
    "/summaries",
    response_model=List[DailySummaryResponse],
    tags=["Resumos Diários"]
)
async def get_summaries(
    start_date: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    limit: int = Query(30, ge=1, le=365, description="Limite de resultados"),
    role: str = Depends(verify_api_key)
):
    with get_db() as db:
        query = "SELECT * FROM daily_summaries WHERE 1=1"
        params = []
        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)
        
        query += " ORDER BY date DESC LIMIT %s"
        params.append(limit)
        
        rows = db.fetch_all(query, tuple(params))
        return [DailySummaryResponse(**row) for row in rows]


@router.get(
    "/summaries/{target_date}",
    response_model=DailySummaryResponse,
    tags=["Resumos Diários"]
)
async def get_summary_by_date(
    target_date: str,
    role: str = Depends(verify_api_key)
):
    with get_db() as db:
        row = db.fetch_one(
            "SELECT * FROM daily_summaries WHERE date = %s",
            (target_date,)
        )
        if not row:
            raise HTTPException(status_code=404, detail="Resumo não encontrado")
        return DailySummaryResponse(**row)


@router.get(
    "/languages",
    response_model=List[LanguageResponse],
    tags=["Linguagens"]
)
async def get_languages(
    start_date: Optional[str] = Query(None, description="Data inicial"),
    end_date: Optional[str] = Query(None, description="Data final"),
    limit: int = Query(100, ge=1, le=1000),
    role: str = Depends(verify_api_key)
):
    with get_db() as db:
        query = "SELECT * FROM languages WHERE 1=1"
        params = []
        if start_date:
            query += " AND summary_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND summary_date <= %s"
            params.append(end_date)
            
        query += " ORDER BY summary_date DESC, total_seconds DESC LIMIT %s"
        params.append(limit)
        
        rows = db.fetch_all(query, tuple(params))
        return [LanguageResponse(**row) for row in rows]


@router.get(
    "/languages/stats",
    response_model=List[LanguageStatsResponse],
    tags=["Linguagens"]
)
async def get_languages_stats(
    start_date: Optional[str] = Query(None, description="Data inicial"),
    end_date: Optional[str] = Query(None, description="Data final"),
    limit: int = Query(10, ge=1, le=50),
    role: str = Depends(verify_api_key)
):
    with get_db() as db:
        query = """
            SELECT 
                name,
                SUM(total_seconds) as total_seconds
            FROM languages
            WHERE 1=1
        """
        params = []
        if start_date:
            query += " AND summary_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND summary_date <= %s"
            params.append(end_date)
            
        query += " GROUP BY name ORDER BY total_seconds DESC LIMIT %s"
        params.append(limit)
        
        rows = db.fetch_all(query, tuple(params))
        total = sum(row["total_seconds"] for row in rows)
        
        return [
            LanguageStatsResponse(
                name=row["name"],
                total_seconds=row["total_seconds"],
                total_hours=int(row["total_seconds"] / 3600),
                percentage=round((row["total_seconds"] / total * 100) if total > 0 else 0, 2)
            )
            for row in rows
        ]


@router.get(
    "/projects",
    response_model=List[ProjectResponse],
    tags=["Projetos"]
)
async def get_projects(
    start_date: Optional[str] = Query(None, description="Data inicial"),
    end_date: Optional[str] = Query(None, description="Data final"),
    limit: int = Query(100, ge=1, le=1000),
    role: str = Depends(verify_api_key)
):
    with get_db() as db:
        query = "SELECT * FROM projects WHERE 1=1"
        params = []
        if start_date:
            query += " AND summary_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND summary_date <= %s"
            params.append(end_date)
            
        query += " ORDER BY summary_date DESC, total_seconds DESC LIMIT %s"
        params.append(limit)
        
        rows = db.fetch_all(query, tuple(params))
        return [ProjectResponse(**row) for row in rows]


@router.get(
    "/projects/stats",
    response_model=List[ProjectStatsResponse],
    tags=["Projetos"]
)
async def get_projects_stats(
    start_date: Optional[str] = Query(None, description="Data inicial"),
    end_date: Optional[str] = Query(None, description="Data final"),
    limit: int = Query(10, ge=1, le=50),
    role: str = Depends(verify_api_key)
):
    with get_db() as db:
        query = """
            SELECT 
                name,
                SUM(total_seconds) as total_seconds,
                SUM(COALESCE(ai_additions, 0)) as ai_additions,
                SUM(COALESCE(ai_deletions, 0)) as ai_deletions,
                SUM(COALESCE(human_additions, 0)) as human_additions,
                SUM(COALESCE(human_deletions, 0)) as human_deletions
            FROM projects
            WHERE 1=1
        """
        params = []
        if start_date:
            query += " AND summary_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND summary_date <= %s"
            params.append(end_date)
            
        query += " GROUP BY name ORDER BY total_seconds DESC LIMIT %s"
        params.append(limit)
        
        rows = db.fetch_all(query, tuple(params))
        total = sum(row["total_seconds"] for row in rows)
        
        return [
            ProjectStatsResponse(
                name=row["name"],
                total_seconds=row["total_seconds"],
                total_hours=int(row["total_seconds"] / 3600),
                percentage=round((row["total_seconds"] / total * 100) if total > 0 else 0, 2),
                ai_additions=row["ai_additions"],
                ai_deletions=row["ai_deletions"],
                human_additions=row["human_additions"],
                human_deletions=row["human_deletions"]
            )
            for row in rows
        ]


@router.get(
    "/editors",
    response_model=List[EditorResponse],
    tags=["Editores"]
)
async def get_editors(
    start_date: Optional[str] = Query(None, description="Data inicial"),
    end_date: Optional[str] = Query(None, description="Data final"),
    limit: int = Query(100, ge=1, le=1000),
    role: str = Depends(verify_api_key)
):
    with get_db() as db:
        query = "SELECT * FROM editors WHERE 1=1"
        params = []
        if start_date:
            query += " AND summary_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND summary_date <= %s"
            params.append(end_date)
            
        query += " ORDER BY summary_date DESC, total_seconds DESC LIMIT %s"
        params.append(limit)
        
        rows = db.fetch_all(query, tuple(params))
        return [EditorResponse(**row) for row in rows]


@router.get(
    "/stats",
    response_model=StatsResponse,
    tags=["Estatísticas"]
)
async def get_overall_stats(
    start_date: Optional[str] = Query(None, description="Data inicial"),
    end_date: Optional[str] = Query(None, description="Data final"),
    role: str = Depends(verify_api_key)
):
    with get_db() as db:
        summary_query = """
            SELECT 
                COUNT(*) as total_days,
                SUM(total_seconds) as total_seconds
            FROM daily_summaries
            WHERE 1=1
        """
        params = []
        if start_date:
            summary_query += " AND date >= %s"
            params.append(start_date)
        if end_date:
            summary_query += " AND date <= %s"
            params.append(end_date)
            
        summary = db.fetch_one(summary_query, tuple(params))
        
        total_days = int(summary["total_days"]) + PREVIOUS_DAYS if summary["total_days"] else PREVIOUS_DAYS
        total_seconds = summary["total_seconds"] + (PREVIOUS_HOURS * 3600) if summary["total_seconds"] else (PREVIOUS_HOURS * 3600)
        
        lang_query = "SELECT name, SUM(total_seconds) as total FROM languages WHERE 1=1"
        if start_date: lang_query += " AND summary_date >= %s"
        if end_date: lang_query += " AND summary_date <= %s"
        lang_query += " GROUP BY name ORDER BY total DESC LIMIT 1"
        top_lang = db.fetch_one(lang_query, tuple(params))
        
        proj_query = "SELECT name, SUM(total_seconds) as total FROM projects WHERE 1=1"
        if start_date: proj_query += " AND summary_date >= %s"
        if end_date: proj_query += " AND summary_date <= %s"
        proj_query += " GROUP BY name ORDER BY total DESC LIMIT 1"
        top_proj = db.fetch_one(proj_query, tuple(params))
        
        editor_query = "SELECT name, SUM(total_seconds) as total FROM editors WHERE 1=1"
        if start_date: editor_query += " AND summary_date >= %s"
        if end_date: editor_query += " AND summary_date <= %s"
        editor_query += " GROUP BY name ORDER BY total DESC LIMIT 1"
        top_editor = db.fetch_one(editor_query, tuple(params))
        
        return StatsResponse(
            total_days=total_days,
            total_seconds=total_seconds,
            total_hours=int(total_seconds / 3600),
            average_seconds_per_day=round(total_seconds / total_days, 2) if total_days > 0 else 0,
            average_hours_per_day=round(total_seconds / 3600 / total_days, 2) if total_days > 0 else 0,
            top_language=top_lang["name"] if top_lang else None,
            top_project=top_proj["name"] if top_proj else None,
            top_editor=top_editor["name"] if top_editor else None,
        )
