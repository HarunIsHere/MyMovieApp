from movie_storage_sql import add_movie, list_movies, delete_movie, update_movie

# Test adding a movie
add_movie("Inception", 2010, 8.8)

# Test listing movies
movies = list_movies()
print(movies)

# Test updating a movie's rating
update_movie("Inception", 9.0)
print(list_movies())

# Test deleting a movie
delete_movie("Inception")
print(list_movies())  # Should be empty if it was the only movie
