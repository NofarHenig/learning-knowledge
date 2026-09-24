import os

import boto3


def get_postgres_connection_string() -> str:
    connection_string = os.getenv(
        "POSTGRES_CONNECTION_STRING"
    )

    if connection_string:
        return connection_string

    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT", "5432"))
    database = os.getenv("DB_NAME", "postgres")
    username = os.getenv("DB_USER", "postgres")
    region = os.getenv("AWS_REGION")

    if not host:
        raise ValueError(
            "DB_HOST is not configured"
        )

    if not region:
        raise ValueError(
            "AWS_REGION is not configured"
        )

    rds = boto3.client(
        "rds",
        region_name=region
    )

    token = rds.generate_db_auth_token(
        DBHostname=host,
        Port=port,
        DBUsername=username,
        Region=region
    )

    return (
        f"host={host} "
        f"port={port} "
        f"dbname={database} "
        f"user={username} "
        f"password={token} "
        f"sslmode=require"
    )