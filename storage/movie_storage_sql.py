import os
import urllib.parse
import urllib.request
import json
from sqlalchemy import create_engine, text

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # project root
DB_PATH = os.path.join(BASE_DIR, "data", "movies.db")
DB_URL = f"sqlite:///{DB_PATH}"

# Create the engine
engine = create_engine(DB_URL, echo=False)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """))
    connection.execute(text("""
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
    """))
    connection.commit()


class MovieStorageError(Exception):
    """Base class for storage related errors."""


class MovieNotFoundError(MovieStorageError):
    """Raised when a movie does not exist in the database."""


class MovieAlreadyExistsError(MovieStorageError):
    """Raised when adding a movie that already exists."""


def list_users():
    """Return list of (id, name) sorted by name."""
    with engine.connect() as connection:
        rows = connection.execute(text("SELECT id, name FROM users ORDER BY name")).fetchall()
    return [(r[0], r[1]) for r in rows]


def create_user(name):
    """Create user if not exists. Returns user_id."""
    name = name.strip()
    with engine.connect() as connection:
        connection.execute(text("INSERT OR IGNORE INTO users (name) VALUES (:name)"), {"name": name})
        connection.commit()
        row = connection.execute(text("SELECT id FROM users WHERE name = :name"), {"name": name}).fetchone()
    return int(row[0])


def get_user_id(name):
    """Return user_id for name, or None."""
    with engine.connect() as connection:
        row = connection.execute(text("SELECT id FROM users WHERE name = :name"), {"name": name}).fetchone()
    return int(row[0]) if row else None


def list_movies(user_id):
    """Return movies dict for one user."""
    with engine.connect() as connection:
        rows = connection.execute(text("""
            SELECT title, year, rating, poster, imdb_id, country, note
            FROM movies
            WHERE user_id = :uid
            ORDER BY title
        """), {"uid": user_id}).fetchall()

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
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                    INSERT INTO movies (user_id, title, year, rating, poster, imdb_id, country, note)
                    VALUES (:user_id, :title, :year, :rating, :poster, :imdb_id, :country, :note)
                """),
                {
                    "user_id": user_id,
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster": poster or "",
                    "imdb_id": imdb_id or "",
                    "country": country or "",
                    "note": "",
                },
            )
            connection.commit()
        except Exception as e:
            # Unique per user: UNIQUE(user_id, title)
            if "UNIQUE constraint failed" in str(e):
                raise MovieAlreadyExistsError(
                    f"Movie '{title}' already exists for this user."
                ) from e
            raise


def delete_movie(user_id, title):
    """Delete a movie for a user."""
    with engine.connect() as connection:
        result = connection.execute(
            text("DELETE FROM movies WHERE user_id = :user_id AND title = :title"),
            {"user_id": user_id, "title": title},
        )
        connection.commit()

        if result.rowcount == 0:
            raise MovieNotFoundError(f"Movie '{title}' not found for this user.")


def update_movie(user_id, title, rating=None, note=None):
    """
    Update a movie's rating and/or note for a user.
    Pass rating=None to keep rating unchanged.
    Pass note=None to keep note unchanged.
    """
    if rating is None and note is None:
        return  # nothing to do

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

    with engine.connect() as connection:
        result = connection.execute(text(sql), params)
        connection.commit()

        if result.rowcount == 0:
            raise MovieNotFoundError(f"Movie '{title}' not found for this user.")
