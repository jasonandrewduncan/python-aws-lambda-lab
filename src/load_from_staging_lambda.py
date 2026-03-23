import logging

from db import get_connection


LOGGER = logging.getLogger(__name__)


def load_from_staging(cur):
    cur.execute(
        """
        INSERT INTO orders (
            order_id,
            order_ts,
            order_date,
            customer_id,
            customer_name,
            segment,
            region,
            channel,
            item_count,
            units_sold,
            order_total,
            currency
        )
        SELECT
            so.order_id,
            MIN(so.order_ts) AS order_ts,
            MIN(so.order_date) AS order_date,
            MIN(so.customer_id) AS customer_id,
            MIN(so.customer_name) AS customer_name,
            MIN(so.segment) AS segment,
            MIN(so.region) AS region,
            MIN(so.channel) AS channel,
            COUNT(*) AS item_count,
            COALESCE(SUM(so.quantity), 0) AS units_sold,
            COALESCE(SUM(so.line_total), 0) AS order_total,
            MIN(so.currency) AS currency
        FROM staging_orders so
        WHERE so.order_id IS NOT NULL
          AND so.order_id <> ''
          AND so.order_ts IS NOT NULL
          AND so.order_date IS NOT NULL
        GROUP BY so.order_id
        ON CONFLICT (order_id) DO UPDATE SET
            order_ts = EXCLUDED.order_ts,
            order_date = EXCLUDED.order_date,
            customer_id = EXCLUDED.customer_id,
            customer_name = EXCLUDED.customer_name,
            segment = EXCLUDED.segment,
            region = EXCLUDED.region,
            channel = EXCLUDED.channel,
            item_count = EXCLUDED.item_count,
            units_sold = EXCLUDED.units_sold,
            order_total = EXCLUDED.order_total,
            currency = EXCLUDED.currency
        """
    )


def handler(event, context):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                load_from_staging(cur)

                cur.execute("SELECT COUNT(*) FROM orders")
                orders_count = cur.fetchone()[0]

            conn.commit()

        LOGGER.info("Load staging completed: orders=%s", orders_count)
    except Exception:
        LOGGER.exception("Load staging failed")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    handler({}, None)