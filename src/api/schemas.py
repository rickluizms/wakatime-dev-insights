from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel

class DailySummaryResponse(BaseModel):
    id: int
    date: str
    total_seconds: float
    digital: Optional[str]
    hours: Optional[int]
    minutes: Optional[int]
    text: Optional[str]
    ai_additions: Optional[int]
    ai_deletions: Optional[int]
    human_additions: Optional[int]
    human_deletions: Optional[int]
    created_at: Optional[Union[str, datetime]]

class LanguageResponse(BaseModel):
    id: int
    summary_date: str
    name: str
    total_seconds: float
    percent: Optional[float]
    digital: Optional[str]
    hours: Optional[int]
    minutes: Optional[int]

class ProjectResponse(BaseModel):
    id: int
    summary_date: str
    name: str
    total_seconds: float
    percent: Optional[float]
    digital: Optional[str]
    hours: Optional[int]
    minutes: Optional[int]
    ai_additions: Optional[int]
    ai_deletions: Optional[int]
    human_additions: Optional[int]
    human_deletions: Optional[int]

class EditorResponse(BaseModel):
    id: int
    summary_date: str
    name: str
    total_seconds: float
    percent: Optional[float]
    digital: Optional[str]
    hours: Optional[int]
    minutes: Optional[int]

class StatsResponse(BaseModel):
    total_days: int
    total_seconds: float
    total_hours: int
    average_seconds_per_day: float
    average_hours_per_day: float
    top_language: Optional[str]
    top_project: Optional[str]
    top_editor: Optional[str]

class LanguageStatsResponse(BaseModel):
    name: str
    total_seconds: float
    total_hours: int
    percentage: float

class ProjectStatsResponse(BaseModel):
    name: str
    total_seconds: float
    total_hours: int
    percentage: float
    ai_additions: int
    ai_deletions: int
    human_additions: int
    human_deletions: int

class HealthResponse(BaseModel):
    status: str
    database: str
    tables_count: int
