from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# =========================
# MODELOS BÁSICOS
# =========================

class TimeTotal(BaseModel):
    digital: Optional[str]
    hours: Optional[int]
    minutes: Optional[int]
    text: Optional[str]
    total_seconds: float
    ai_additions: Optional[int]
    ai_deletions: Optional[int]
    human_additions: Optional[int]
    human_deletions: Optional[int]


class SimpleStat(BaseModel):
    name: str
    total_seconds: float
    percent: Optional[float]
    digital: Optional[str]
    text: Optional[str]
    hours: Optional[int]
    minutes: Optional[int]
    seconds: Optional[int]


class ProjectStat(SimpleStat):
    ai_additions: Optional[int]
    ai_deletions: Optional[int]
    human_additions: Optional[int]
    human_deletions: Optional[int]


class EntityStat(SimpleStat):
    ai_additions: Optional[int]
    ai_deletions: Optional[int]
    human_additions: Optional[int]
    human_deletions: Optional[int]


class MachineStat(SimpleStat):
    machine_name_id: Optional[str]


class RangeInfo(BaseModel):
    date: str
    start: datetime
    end: datetime
    text: Optional[str]
    timezone: Optional[str]


# =========================
# SUMMARY DIÁRIO
# =========================

class DailySummary(BaseModel):
    grand_total: TimeTotal
    categories: Optional[List[SimpleStat]] = []
    projects: Optional[List[ProjectStat]] = []
    languages: Optional[List[SimpleStat]] = []
    editors: Optional[List[SimpleStat]] = []
    operating_systems: Optional[List[SimpleStat]] = []
    dependencies: Optional[List[SimpleStat]] = []
    machines: Optional[List[MachineStat]] = []
    branches: Optional[List[SimpleStat]] = []
    entities: Optional[List[EntityStat]] = []
    range: RangeInfo


# =========================
# TOTAIS DO PERÍODO
# =========================

class CumulativeTotal(BaseModel):
    seconds: float
    text: Optional[str]
    decimal: Optional[str]
    digital: Optional[str]


class DailyAverage(BaseModel):
    holidays: int
    days_including_holidays: int
    days_minus_holidays: int
    seconds: float
    text: Optional[str]
    seconds_including_other_language: float
    text_including_other_language: Optional[str]


# =========================
# RESPONSE PRINCIPAL
# =========================

class WakaTimeSummariesResponse(BaseModel):
    data: List[DailySummary]
    cumulative_total: CumulativeTotal
    daily_average: DailyAverage
    start: datetime
    end: datetime
