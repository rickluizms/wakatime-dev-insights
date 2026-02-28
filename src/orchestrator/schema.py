SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS daily_summaries (
    id SERIAL PRIMARY KEY,
    date TEXT UNIQUE NOT NULL,
    total_seconds REAL NOT NULL,
    digital TEXT,
    hours INTEGER,
    minutes INTEGER,
    text TEXT,
    ai_additions INTEGER,
    ai_deletions INTEGER,
    human_additions INTEGER,
    human_deletions INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS languages (
    id SERIAL PRIMARY KEY,
    summary_date TEXT NOT NULL,
    name TEXT NOT NULL,
    total_seconds REAL NOT NULL,
    percent REAL,
    digital TEXT,
    hours INTEGER,
    minutes INTEGER,
    UNIQUE(summary_date, name)
);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    summary_date TEXT NOT NULL,
    name TEXT NOT NULL,
    total_seconds REAL NOT NULL,
    percent REAL,
    digital TEXT,
    hours INTEGER,
    minutes INTEGER,
    ai_additions INTEGER,
    ai_deletions INTEGER,
    human_additions INTEGER,
    human_deletions INTEGER,
    UNIQUE(summary_date, name)
);

CREATE TABLE IF NOT EXISTS editors (
    id SERIAL PRIMARY KEY,
    summary_date TEXT NOT NULL,
    name TEXT NOT NULL,
    total_seconds REAL NOT NULL,
    percent REAL,
    digital TEXT,
    hours INTEGER,
    minutes INTEGER,
    UNIQUE(summary_date, name)
);

CREATE TABLE IF NOT EXISTS operating_systems (
    id SERIAL PRIMARY KEY,
    summary_date TEXT NOT NULL,
    name TEXT NOT NULL,
    total_seconds REAL NOT NULL,
    percent REAL,
    digital TEXT,
    hours INTEGER,
    minutes INTEGER,
    UNIQUE(summary_date, name)
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    summary_date TEXT NOT NULL,
    name TEXT NOT NULL,
    total_seconds REAL NOT NULL,
    percent REAL,
    digital TEXT,
    hours INTEGER,
    minutes INTEGER,
    UNIQUE(summary_date, name)
);

CREATE TABLE IF NOT EXISTS machines (
    id SERIAL PRIMARY KEY,
    summary_date TEXT NOT NULL,
    name TEXT NOT NULL,
    machine_name_id TEXT,
    total_seconds REAL NOT NULL,
    percent REAL,
    digital TEXT,
    hours INTEGER,
    minutes INTEGER,
    UNIQUE(summary_date, name)
);

CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    summary_date TEXT NOT NULL,
    name TEXT NOT NULL,
    total_seconds REAL NOT NULL,
    percent REAL,
    digital TEXT,
    hours INTEGER,
    minutes INTEGER,
    UNIQUE(summary_date, name)
);

CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    summary_date TEXT NOT NULL,
    name TEXT NOT NULL,
    total_seconds REAL NOT NULL,
    percent REAL,
    digital TEXT,
    hours INTEGER,
    minutes INTEGER,
    ai_additions INTEGER,
    ai_deletions INTEGER,
    human_additions INTEGER,
    human_deletions INTEGER,
    UNIQUE(summary_date, name)
);

CREATE INDEX IF NOT EXISTS idx_languages_date ON languages(summary_date);
CREATE INDEX IF NOT EXISTS idx_projects_date ON projects(summary_date);
CREATE INDEX IF NOT EXISTS idx_editors_date ON editors(summary_date);
CREATE INDEX IF NOT EXISTS idx_daily_summaries_date ON daily_summaries(date);
"""
