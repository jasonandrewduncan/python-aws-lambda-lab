CREATE TABLE IF NOT EXISTS staging_orders (
    order_id TEXT,
    order_ts TIMESTAMP NULL,
    order_date DATE NULL,
    customer_id TEXT,
    customer_name TEXT,
    segment TEXT,
    region TEXT,
    channel TEXT,
    line_no INTEGER,
    product_id TEXT,
    product_name TEXT,
    product_category TEXT,
    quantity INTEGER,
    unit_price NUMERIC(12,2),
    line_total NUMERIC(12,2),
    currency TEXT,
    source_file TEXT,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging_events (
    event_id TEXT,
    event_ts TIMESTAMP NULL,
    event_type TEXT,
    customer_id TEXT,
    session_id TEXT,
    source TEXT,
    properties JSONB,
    source_file TEXT,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging_logs (
    log_ts TIMESTAMPTZ NULL,
    service TEXT,
    level TEXT,
    message TEXT,
    order_id TEXT,
    customer_id TEXT,
    latency_ms INTEGER,
    metadata JSONB,
    source_file TEXT,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    order_ts TIMESTAMP NOT NULL,
    order_date DATE NOT NULL,
    customer_id TEXT,
    customer_name TEXT,
    segment TEXT,
    region TEXT,
    channel TEXT,
    item_count INTEGER NOT NULL,
    units_sold INTEGER NOT NULL,
    order_total NUMERIC(12,2) NOT NULL,
    currency TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_sales_summary (
    sales_date DATE PRIMARY KEY,
    orders_count INTEGER NOT NULL,
    units_sold INTEGER NOT NULL,
    gross_sales NUMERIC(12,2) NOT NULL,
    avg_order_value NUMERIC(12,2) NOT NULL,
    refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_staging_orders_order_id ON staging_orders(order_id);
CREATE INDEX IF NOT EXISTS idx_staging_orders_order_date ON staging_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
