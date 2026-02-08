import os
from sqlalchemy import create_engine, text

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # project root
DB_PATH = os.path.join(BASE_DIR, "data", "movies.db")
DB_URL = f"sqlite:///{DB_PATH}"

# Create the engine
engine = create_engine(DB_URL, echo=False)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT NOT NULL
        )
    """))
    connection.commit()


class MovieStorageError(Exception):
    """Base class for storage related errors."""


class MovieNotFoundError(MovieStorageError):
    """Raised when a movie does not exist in the database."""


class MovieAlreadyExistsError(MovieStorageError):
    """Raised when adding a movie that already exists."""


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating, poster FROM movies")
        )
        movies = result.fetchall()

    return {
        row[0]: {"year": row[1], "rating": row[2], "poster": row[3]}
        for row in movies
    }


def add_movie(title, year, rating, poster):
    """Add a new movie to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                    INSERT INTO movies (title, year, rating, poster)
                    VALUES (:title, :year, :rating, :poster)
                """),
                {"title": title, "year": year, "rating": rating, "poster": poster},
            )
            connection.commit()
        except Exception as e:
            # SQLite duplicate unique title contains this
            if "UNIQUE constraint failed" in str(e):
                raise MovieAlreadyExistsError(f"Movie '{title}' already exists.") from e
            raise


def delete_movie(title):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("DELETE FROM movies WHERE title = :title"),
            {"title": title}
        )
        connection.commit()

        if result.rowcount == 0:
            raise MovieNotFoundError(f"Movie '{title}' not found.")


def update_movie(title, rating):
    """Update a movie's rating in the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("UPDATE movies SET rating = :rating WHERE title = :title"),
            {"title": title, "rating": rating}
        )
        connection.commit()

        if result.rowcount == 0:
            raise MovieNotFoundError(f"Movie '{title}' not found.")
