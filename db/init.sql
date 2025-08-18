CREATE TABLE IF NOT EXISTS company_tickers(
    id SERIAL PRIMARY KEY,
    sector VARCHAR(128),
    industry VARCHAR(128),
    ticker_symbol VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(128),
    currency VARCHAR(10)
)

CREATE TABLE IF NOT EXISTS company_facts(
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES company_tickers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    value NUMERIC,
    statement_type VARCHAR(32),
    key_factor VARCHAR(128),
    form_type VARCHAR(32)
)