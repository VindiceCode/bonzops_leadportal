import os

# Database configuration
DB_CONFIG = {
    "host": os.environ["PGHOST"],
    "database": os.environ["PGDATABASE"],
    "user": os.environ["PGUSER"],
    "password": os.environ["PGPASSWORD"],
    "port": os.environ["PGPORT"],
}

# Bonzo webhook configuration
BONZO_WEBHOOK_URL = os.environ["CLIENT_SECRET_WEBHOOK_URL"]

# Field mappings for normalization
NORMALIZED_FIELDS = [
    "first_name",
    "last_name",
    "email",
    "phone",
    "address",
    "city",
    "state",
    "zip",
    "credit_score",
    "mortgage_balance",
    "mortgage_payment",
    "mortgage_rate",
]
