import psycopg2
from psycopg2.extras import DictCursor
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Create processing_logs table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS processing_logs (
                    id SERIAL PRIMARY KEY,
                    source_type VARCHAR(50),
                    file_name VARCHAR(255),
                    records_processed INTEGER,
                    success_count INTEGER,
                    failure_count INTEGER,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create webhook_responses table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS webhook_responses (
                    id SERIAL PRIMARY KEY,
                    lead_id VARCHAR(255),
                    payload JSONB,
                    response_code INTEGER,
                    response_body TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()

    def log_processing(self, source_type, file_name, records_processed, success_count, failure_count):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO processing_logs 
                (source_type, file_name, records_processed, success_count, failure_count)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (source_type, file_name, records_processed, success_count, failure_count))
            self.conn.commit()
            return cur.fetchone()[0]

    def log_webhook_response(self, lead_id, payload, response_code, response_body):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO webhook_responses 
                (lead_id, payload, response_code, response_body)
                VALUES (%s, %s, %s, %s)
            """, (lead_id, payload, response_code, response_body))
            self.conn.commit()
