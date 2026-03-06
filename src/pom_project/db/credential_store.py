from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoginCredentials:
    username: str
    password: str


class CredentialStore:
    """Simple SQLite-backed store for test login credentials."""

    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)

    def init_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS login_credentials (
                    credential_key TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def upsert_credentials(self, credential_key: str, credentials: LoginCredentials) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO login_credentials (credential_key, username, password)
                VALUES (?, ?, ?)
                ON CONFLICT(credential_key)
                DO UPDATE SET username = excluded.username, password = excluded.password
                """,
                (credential_key, credentials.username, credentials.password),
            )
            connection.commit()

    def get_credentials(self, credential_key: str) -> LoginCredentials:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT username, password
                FROM login_credentials
                WHERE credential_key = ?
                """,
                (credential_key,),
            ).fetchone()

        if row is None:
            raise KeyError(f"Credential key not found: {credential_key}")

        return LoginCredentials(username=row[0], password=row[1])
