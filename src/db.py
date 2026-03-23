import os

from dotenv import load_dotenv
import psycopg




load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "lambda_lab"),
        user=os.getenv("DB_USER", "lambda_lab"),
        password=os.getenv("DB_PASSWORD", "lambda_lab"),
        autocommit=False,
    )
