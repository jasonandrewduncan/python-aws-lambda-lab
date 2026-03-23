import logging

from db import get_connection


LOGGER = logging.getLogger(__name__)


def load_summary(cur):
    cur.execute(
        """
        INSERT INTO daily_sales_summary (
            sales_date,
            orders_count,
            units_sold,
            gross_sales,
            avg_order_value,
            refreshed_at
        )
        SELECT
            o.order_date AS sales_date,
            COUNT(*) AS orders_count,
            COALESCE(SUM(o.units_sold), 0) AS units_sold,
            COALESCE(SUM(o.order_total), 0) AS gross_sales,
            ROUND(COALESCE(AVG(o.order_total), 0), 2) AS avg_order_value,
            CURRENT_TIMESTAMP
        FROM orders o
        GROUP BY o.order_date
        ON CONFLICT (sales_date) DO UPDATE SET
            orders_count = EXCLUDED.orders_count,
            units_sold = EXCLUDED.units_sold,
            gross_sales = EXCLUDED.gross_sales,
            avg_order_value = EXCLUDED.avg_order_value,
            refreshed_at = CURRENT_TIMESTAMP
        """
    )


def handler(event, context):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                load_summary(cur)

                cur.execute("SELECT COUNT(*) FROM daily_sales_summary")
                summary_days = cur.fetchone()[0]

                cur.execute(
                    """
                    SELECT sales_date, orders_count, gross_sales, avg_order_value
                    FROM daily_sales_summary
                    ORDER BY sales_date DESC
                    LIMIT 1
                    """
                )
                latest_row = cur.fetchone()

            conn.commit()

        if latest_row:
            LOGGER.info(
                "Load summary completed: summary_days=%s latest_date=%s latest_gross_sales=%s",
                summary_days,
                latest_row[0],
                latest_row[2],
            )
        else:
            LOGGER.info("Load summary completed: summary_days=%s", summary_days)
    except Exception:
        LOGGER.exception("Load summary failed")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    handler({}, None)