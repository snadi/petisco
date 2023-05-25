from __future__ import annotations

import os
from typing import TypeVar

from sqlalchemy import select

from examples.persistence.models.sql_user import SqlUser
from petisco.extra.sqlalchemy import SqlDatabase, SqliteConnection

T = TypeVar("T")

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DATABASE_NAME = "my-database"
DATABASE_FILENAME = "sqlite.db"
SERVER_NAME = "sqlite"

sql_database = SqlDatabase(
    name=DATABASE_NAME,
    connection=SqliteConnection.create(SERVER_NAME, DATABASE_FILENAME),
)
sql_database.initialize()
session_scope = sql_database.get_session_scope()

with session_scope() as session:

    stmt = select(SqlUser)
    users = session.execute(stmt).all()
    print(f"{users=}")

    session.add(SqlUser(name="Alice", age="3"))
    session.add(SqlUser(name="Bob", age="10"))
    session.commit()

    stmt = select(SqlUser).where(SqlUser.name == "Alice")
    user = session.execute(stmt).first()
    print(user)

    stmt = select(SqlUser)
    users = session.execute(stmt).all()
    print(f"{users=}")
