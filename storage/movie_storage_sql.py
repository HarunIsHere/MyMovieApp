"""
SQLite storage layer for the Movie App (users + movies tables).

Public API (used by movies.py):
- list_users()
- create_user(name)
- get_user_id(name)
- list_movies(user_id)
- add_movie(user_id, title, year, rating, poster, imdb_id, country)
- delete_movie(user_id, title)
- update_movie(user_id, title, rating=None, note=None)
"""

import os

from sqlalchemy import create_engine, text

# project root
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "movies.db")
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, echo=False)


def _ensure_data_dir() -> None:
    """Ensure the data directory exists so SQLite can create the DB file."""
    data_dir = os.path.dirname(DB_PATH)
    os.makedirs(data_dir, exist_ok=True)


def _init_db() -> None:
    """Create tables if they do not exist."""
    create_users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """
    create_movies_sql = """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT,
            imdb_id TEXT,
            country TEXT,
            note TEXT,
            UNIQUE(user_id, title),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """

    with engine.begin() as connection:
        connection.execute(text(create_users_sql))
        connection.execute(text(create_movies_sql))


_ensure_data_dir()
_init_db()


class MovieStorageError(Exception):
    """Base class for storage related errors."""


class MovieNotFoundError(MovieStorageError):
    """Raised when a movie does not exist in the database."""


class MovieAlreadyExistsError(MovieStorageError):
    """Raised when adding a movie that already exists."""


def list_users():
    """Return list of (id, name) sorted by name."""
    with engine.connect() as connection:
        rows = connection.execute(
            text("SELECT id, name FROM users ORDER BY name")
        ).fetchall()
    return [(r[0], r[1]) for r in rows]


def create_user(name):
    """Create user if not exists. Returns user_id."""
    name = name.strip()
    with engine.begin() as connection:
        connection.execute(
            text("INSERT OR IGNORE INTO users (name) VALUES (:name)"),
            {"name": name},
        )
        row = connection.execute(
            text("SELECT id FROM users WHERE name = :name"),
            {"name": name},
        ).fetchone()

    return int(row[0])


def get_user_id(name):
    """Return user_id for name, or None."""
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT id FROM users WHERE name = :name"),
            {"name": name},
        ).fetchone()
    return int(row[0]) if row else None


def list_movies(user_id):
    """Return movies dict for one user."""
    sql = """
        SELECT title, year, rating, poster, imdb_id, country, note
        FROM movies
        WHERE user_id = :uid
        ORDER BY title
    """
    with engine.connect() as connection:
        rows = connection.execute(text(sql), {"uid": user_id}).fetchall()

    return {
        r[0]: {
            "year": r[1],
            "rating": r[2],
            "poster": r[3] or "",
            "imdb_id": r[4] or "",
            "country": r[5] or "",
            "note": r[6] or "",
        }
        for r in rows
    }


def add_movie(user_id, title, year, rating, poster, imdb_id, country):
    """Add a new movie for a user."""
    sql = """
        INSERT INTO movies (
            user_id, title, year, rating, poster, imdb_id, country, note
        )
        VALUES (
            :user_id, :title, :year, :rating, :poster, :imdb_id, :country, :note
        )
    """
    params = {
        "user_id": user_id,
        "title": title,
        "year": year,
        "rating": rating,
        "poster": poster or "",
        "imdb_id": imdb_id or "",
        "country": country or "",
        "note": "",
    }

    try:
        with engine.begin() as connection:
            connection.execute(text(sql), params)
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise MovieAlreadyExistsError(
                f"Movie '{title}' already exists for this user."
            ) from exc
        raise


def delete_movie(user_id, title):
    """Delete a movie for a user."""
    with engine.begin() as connection:
        result = connection.execute(
            text("DELETE FROM movies WHERE user_id = :user_id AND title = :title"),
            {"user_id": user_id, "title": title},
        )

    if result.rowcount == 0:
        raise MovieNotFoundError(f"Movie '{title}' not found for this user.")


def update_movie(user_id, title, rating=None, note=None):
    """
    Update a movie's rating and/or note for a user.

    Pass rating=None to keep rating unchanged.
    Pass note=None to keep note unchanged.
    """
    if rating is None and note is None:
        return

    set_parts = []
    params = {"user_id": user_id, "title": title}

    if rating is not None:
        set_parts.append("rating = :rating")
        params["rating"] = rating

    if note is not None:
        set_parts.append("note = :note")
        params["note"] = note

    sql = f"""
        UPDATE movies
        SET {", ".join(set_parts)}
        WHERE user_id = :user_id AND title = :title
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql), params)

    if result.rowcount == 0:
        raise MovieNotFoundError(f"Movie '{title}' not found for this user.")
