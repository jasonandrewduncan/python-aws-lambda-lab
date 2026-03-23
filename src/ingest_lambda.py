import csv
import json
import logging
from datetime import datetime
from pathlib import Path

from db import get_connection


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGGER = logging.getLogger(__name__)


def parse_timestamp(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def load_orders(conn):
    file_path = DATA_DIR / "sample_orders.csv"
    rows = []

    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for record in reader:
            rows.append((
                record["order_id"],
                parse_timestamp(record["order_ts"]),
                record["order_date"] or None,
                record["customer_id"],
                record["customer_name"],
                record["segment"],
                record["region"],
                record["channel"],
                int(record["line_no"]) if record["line_no"] else None,
                record["product_id"],
                record["product_name"],
                record["product_category"],
                int(record["quantity"]) if record["quantity"] else None,
                record["unit_price"] or None,
                record["line_total"] or None,
                record["currency"],
                file_path.name,
            ))

    sql = """
        INSERT INTO staging_orders (
            order_id, order_ts, order_date, customer_id, customer_name, segment,
            region, channel, line_no, product_id, product_name, product_category,
            quantity, unit_price, line_total, currency, source_file
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
    """

    with conn.cursor() as cur:
        cur.executemany(sql, rows)

    return len(rows)


def load_events(conn):
    file_path = DATA_DIR / "sample_events.json"
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    rows = []

    for record in payload:
        rows.append((
            record.get("event_id"),
            parse_timestamp(record.get("event_ts")),
            record.get("event_type"),
            record.get("customer_id"),
            record.get("session_id"),
            record.get("source"),
            json.dumps(record.get("properties", {})),
            file_path.name,
        ))

    sql = """
        INSERT INTO staging_events (
            event_id, event_ts, event_type, customer_id, session_id,
            source, properties, source_file
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
    """

    with conn.cursor() as cur:
        cur.executemany(sql, rows)

    return len(rows)


def load_logs(conn):
    file_path = DATA_DIR / "sample_logs.jsonl"
    rows = []

    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            rows.append((
                record.get("timestamp"),
                record.get("service"),
                record.get("level"),
                record.get("message"),
                record.get("order_id"),
                record.get("customer_id"),
                record.get("latency_ms"),
                json.dumps(record.get("metadata", {})),
                file_path.name,
            ))

    sql = """
        INSERT INTO staging_logs (
            log_ts, service, level, message, order_id, customer_id,
            latency_ms, metadata, source_file
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
    """

    with conn.cursor() as cur:
        cur.executemany(sql, rows)

    return len(rows)


def handler(event, context):
    try:
        with get_connection() as conn:
            orders_loaded = load_orders(conn)
            events_loaded = load_events(conn)
            logs_loaded = load_logs(conn)
            conn.commit()

        LOGGER.info(
            "Ingestion completed: orders=%s events=%s logs=%s",
            orders_loaded,
            events_loaded,
            logs_loaded,
        )
    except Exception:
        LOGGER.exception("Ingestion failed")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    handler({}, None)
