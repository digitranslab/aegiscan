import json
import logging
import os
from logging.config import fileConfig

import alembic_postgresql_enum  # noqa: F401
import boto3
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context
from aegiscan.db import schemas  # noqa: F401

AEGISCAN__DB_URI = os.getenv("AEGISCAN__DB_URI")
if not AEGISCAN__DB_URI:
    username = os.getenv("AEGISCAN__DB_USER", "postgres")
    host = os.getenv("AEGISCAN__DB_ENDPOINT")
    port = os.getenv("AEGISCAN__DB_PORT", 5432)
    database = os.getenv("AEGISCAN__DB_NAME", "postgres")

    # Check if in AWS environment
    if os.getenv("AEGISCAN__DB_PASS__ARN"):
        logging.info("Fetching database password from AWS Secrets Manager")
        session = boto3.Session()
        client = session.client("secretsmanager")
        response = client.get_secret_value(SecretId=os.getenv("AEGISCAN__DB_PASS__ARN"))
        password = json.loads(response["SecretString"])["password"]
    else:
        logging.info("Fetching database password from environment variable")
        password = os.getenv("AEGISCAN__DB_PASS")

    AEGISCAN__DB_URI = (
        f"postgresql+psycopg://{username}:{password}@{host}:{port!s}/{database}"
    )


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=AEGISCAN__DB_URI,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        configuration=config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=AEGISCAN__DB_URI,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
