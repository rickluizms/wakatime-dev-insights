from typing import Any, List
from core.db import Database
from core.models import DailySummary
from src.orchestrator.schema import SCHEMA_SQL
from core.config import setup_logger

logger = setup_logger(__name__)

class WakaTimeRepository:
    def __init__(self):
        self._init_database()

    def _init_database(self) -> None:
        with Database() as db:
            db.execute_script(SCHEMA_SQL)
        logger.info("Schema do banco de dados inicializado.")

    def save_summary(self, summary: DailySummary) -> None:
        with Database() as db:
            summary_date = summary.range.date
            grand_total = summary.grand_total

            existing = db.fetch_one(
                "SELECT id FROM daily_summaries WHERE date = %s",
                (summary_date,)
            )

            if existing:
                logger.info(f"Dados para {summary_date} já existem. Atualizando...")
                db.update(
                    "daily_summaries",
                    {
                        "total_seconds": grand_total.total_seconds,
                        "digital": grand_total.digital,
                        "hours": grand_total.hours,
                        "minutes": grand_total.minutes,
                        "text": grand_total.text,
                        "ai_additions": grand_total.ai_additions,
                        "ai_deletions": grand_total.ai_deletions,
                        "human_additions": grand_total.human_additions,
                        "human_deletions": grand_total.human_deletions,
                    },
                    "date = %s",
                    (summary_date,)
                )
                tables = ["languages", "projects", "editors", "operating_systems",
                          "categories", "machines", "branches", "entities"]
                for table in tables:
                    db.delete(table, "summary_date = %s", (summary_date,))
            else:
                db.insert("daily_summaries", {
                    "date": summary_date,
                    "total_seconds": grand_total.total_seconds,
                    "digital": grand_total.digital,
                    "hours": grand_total.hours,
                    "minutes": grand_total.minutes,
                    "text": grand_total.text,
                    "ai_additions": grand_total.ai_additions,
                    "ai_deletions": grand_total.ai_deletions,
                    "human_additions": grand_total.human_additions,
                    "human_deletions": grand_total.human_deletions,
                })

            self._insert_children(db, summary_date, summary)

    def _insert_children(self, db: Database, summary_date: str, summary: DailySummary) -> None:
        def _insert_items(table: str, items: List[Any], extra_fields: List[str] = None):
            if not items:
                return
            for item in items:
                data = {
                    "summary_date": summary_date,
                    "name": item.name,
                    "total_seconds": item.total_seconds,
                    "percent": getattr(item, 'percent', 0.0),
                    "digital": getattr(item, 'digital', ""),
                    "hours": getattr(item, 'hours', 0),
                    "minutes": getattr(item, 'minutes', 0),
                }
                if extra_fields:
                    for field in extra_fields:
                        data[field] = getattr(item, field, None)
                if table == "machines":
                    data["machine_name_id"] = getattr(item, 'machine_name_id', None)
                db.insert(table, data)

        _insert_items("languages", summary.languages)
        _insert_items("projects", summary.projects, ["ai_additions", "ai_deletions", "human_additions", "human_deletions"])
        _insert_items("editors", summary.editors)
        _insert_items("operating_systems", summary.operating_systems)
        _insert_items("categories", summary.categories)
        _insert_items("machines", summary.machines)
        _insert_items("branches", summary.branches)
        _insert_items("entities", summary.entities, ["ai_additions", "ai_deletions", "human_additions", "human_deletions"])
