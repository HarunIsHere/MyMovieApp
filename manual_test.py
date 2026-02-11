"""
Manual sanity check for storage functions.

Run:
    python3 manual_test.py
"""

from storage.movie_storage_sql import (
    add_movie,
    create_user,
    delete_movie,
    list_movies,
    update_movie,
)


def main():
    """Run a basic manual test of add/list/update/delete storage functions."""
    user_id = create_user("manual_test_user")

    title = "Inception"
    year = 2010
    rating = 8.8

    poster = ""
    imdb_id = ""
    country = ""

    # Test adding a movie
    add_movie(user_id, title, year, rating, poster, imdb_id, country)
    print(f"Movie '{title}' added successfully.")

    # Test listing movies
    movies = list_movies(user_id)
    print(movies)

    # Test updating a movie's rating
    update_movie(user_id, title, rating=9.0)
    print(f"Movie '{title}' updated successfully.")
    print(list_movies(user_id))

    # Test deleting a movie
    delete_movie(user_id, title)
    print(f"Movie '{title}' deleted successfully.")
    print(list_movies(user_id))  # Should be empty if it was the only movie


if __name__ == "__main__":
    main()
