import os
import html
import statistics as st
import random as rd
import matplotlib.pyplot as plt  # pylint: disable=import-error
import json
import urllib.parse
import urllib.request
from storage import movie_storage_sql as storage


OMDB_API_KEY = "3bec4110"
OMDB_BASE_URL = "http://www.omdbapi.com/"

# ANSI color codes may be treated as plain text if you use run button in codio,
# instead run in Terminal please

RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"


def fetch_movie_from_omdb(title):
    """
    Fetch movie data from OMDb by title.
    Returns dict with keys: title, year, rating, poster
    Raises RuntimeError on OMDb errors and ConnectionError on network errors.
    """
    params = {"apikey": OMDB_API_KEY, "t": title}
    url = f"{OMDB_BASE_URL}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise ConnectionError(f"OMDb connection failed: {e}") from e

    if data.get("Response") != "True":
        raise RuntimeError(data.get("Error", "Movie not found"))

    api_title = data.get("Title", "").strip()

    year_raw = (data.get("Year") or "").strip()
    year_digits = "".join(ch for ch in year_raw if ch.isdigit())
    year = int(year_digits[:4]) if len(year_digits) >= 4 else 0

    rating_raw = (data.get("imdbRating") or "").strip()
    try:
        rating = float(rating_raw) if rating_raw != "N/A" else 0.0
    except ValueError:
        rating = 0.0

    poster = (data.get("Poster") or "").strip()
    if not poster or poster == "N/A":
        poster = ""

    return {"title": api_title, "year": year, "rating": rating, "poster": poster}


def prompt_non_empty(prompt_text):
    """Prompt until the user enters a non-empty string (after stripping)."""
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print(f'{RED}Invalid input. Please enter a non-empty value.{RESET}')


def prompt_float(prompt_text, min_value=None, max_value=None):
    """Prompt until the user enters a valid float (optionally within range)."""
    while True:
        raw = input(prompt_text).strip()
        try:
            value = float(raw)
        except ValueError:
            print(f'{RED}Invalid number. Please try again.{RESET}')
            continue

        if min_value is not None and value < min_value:
            print(f'{RED}Value must be at least {min_value}.{RESET}')
            continue
        if max_value is not None and value > max_value:
            print(f'{RED}Value must be at most {max_value}.{RESET}')
            continue

        return value


def prompt_int(prompt_text, min_value=None, max_value=None):
    """Prompt until the user enters a valid int (optionally within range)."""
    while True:
        raw = input(prompt_text).strip()
        try:
            value = int(raw)
        except ValueError:
            print(f'{RED}Invalid number. Please enter a whole number.{RESET}')
            continue

        if min_value is not None and value < min_value:
            print(f'{RED}Value must be at least {min_value}.{RESET}')
            continue
        if max_value is not None and value > max_value:
            print(f'{RED}Value must be at most {max_value}.{RESET}')
            continue

        return value


def prompt_optional_float(prompt_text, min_value=None, max_value=None):
    """Prompt for a float; blank means None."""
    while True:
        raw = input(prompt_text).strip()
        if raw == "":
            return None
        try:
            value = float(raw)
        except ValueError:
            print(f'{RED}Invalid number. Please try again (or leave blank).{RESET}')
            continue

        if min_value is not None and value < min_value:
            print(f'{RED}Value must be at least {min_value} (or leave blank).{RESET}')
            continue
        if max_value is not None and value > max_value:
            print(f'{RED}Value must be at most {max_value} (or leave blank).{RESET}')
            continue

        return value


def prompt_optional_int(prompt_text, min_value=None, max_value=None):
    """Prompt for an int; blank means None."""
    while True:
        raw = input(prompt_text).strip()
        if raw == "":
            return None
        try:
            value = int(raw)
        except ValueError:
            print(f'{RED}Invalid number. Please enter a whole number (or leave blank).{RESET}')
            continue

        if min_value is not None and value < min_value:
            print(f'{RED}Value must be at least {min_value} (or leave blank).{RESET}')
            continue
        if max_value is not None and value > max_value:
            print(f'{RED}Value must be at most {max_value} (or leave blank).{RESET}')
            continue

        return value


def print_movies(movies):
    """Print movies (title + year + rating)."""
    print(f'\n{BOLD}{len(movies)} movies in total\n------------------{RESET}')
    for title, data in movies.items():
        print(f'{title} ({data["year"]}): {data["rating"]:.1f} | Poster: {data["poster"]}')


def add_movie_f():
    """Add a movie by title only (fetch from OMDb, store in SQL)."""
    title_input = prompt_non_empty(f"{YELLOW}Enter movie title: {RESET}")

    try:
        movie = fetch_movie_from_omdb(title_input)
    except ConnectionError as e:
        print(f"{RED}{e}{RESET}")
        return
    except RuntimeError as e:
        print(f"{RED}OMDb error: {e}{RESET}")
        return

    movies = storage.list_movies()
    if movie["title"] in movies:
        print(f'{RED}Error: "{movie["title"]}" already exists in database.{RESET}')
        return

    try:
        storage.add_movie(movie["title"], movie["year"], movie["rating"], movie["poster"])
        print(f'Added "{movie["title"]}" with rating {movie["rating"]:.1f} ({movie["year"]})')
    except storage.MovieAlreadyExistsError as e:
        print(f"{RED}{e}{RESET}")
    except Exception as e:
        print(f"{RED}Database error: {e}{RESET}")


def resolve_title(movies, user_input):
    """Return the stored movie title matching user_input, or None (case-insensitive + suggestions)."""
    if not movies:
        return None

    key = user_input.strip().lower()

    # 1) Exact match (case-insensitive)
    title_map = {t.lower(): t for t in movies.keys()}
    if key in title_map:
        return title_map[key]

    # 2) Substring match (if exactly one hit, accept it)
    substring_hits = [t for t in movies.keys() if key in t.lower()]
    if len(substring_hits) == 1:
        return substring_hits[0]

    # 3) Suggestions (prints) and return None
    similar = custom_get_close_matches(key, movies.keys(), cutoff=0.5)
    if similar:
        print(f'\nMovie "{user_input}" not found. Did you mean:')
        for s in similar:
            print(f" - {s}")
    return None


def delete_movie():
    """Delete a movie from the SQL database (case-insensitive + suggestions)."""
    movies = storage.list_movies()
    if not movies:
        print(f'{RED}No movies in database.{RESET}')
        return

    typed = prompt_non_empty(f"{YELLOW}Enter movie title to delete: {RESET}")
    title = resolve_title(movies, typed)

    if title:
        try:
            storage.delete_movie(title)
            print(f'Deleted "{title}"')
        except storage.MovieNotFoundError as e:
            print(f"{RED}{e}{RESET}")
        except Exception as e:
            print(f"{RED}Database error: {e}{RESET}")
    else:
        print(f'{RED}Error: "{typed}" not found in database.{RESET}')


def update_movie():
    """Update a movie rating in the SQL database (case-insensitive + suggestions)."""
    movies = storage.list_movies()
    if not movies:
        print(f'{RED}No movies in database.{RESET}')
        return

    typed = prompt_non_empty(f"{YELLOW}Enter movie title to update: {RESET}")
    title = resolve_title(movies, typed)

    if not title:
        print(f'{RED}Error: "{typed}" not found.{RESET}')
        return

    new_rating = prompt_float(
        f'{YELLOW}Enter new rating (1-10): {RESET}',
        1.0,
        10.0
    )
    try:
        storage.update_movie(title, new_rating)
        print(f'Updated "{title}" to {new_rating:.1f}')
    except storage.MovieNotFoundError as e:
        print(f"{RED}{e}{RESET}")
    except Exception as e:
        print(f"{RED}Database error: {e}{RESET}")


def stats(movies):
    """Print statistics (average, median, best, worst)."""
    if not movies:
        print(f'{RED}No movies in database.{RESET}')
        return

    ratings = [data["rating"] for data in movies.values()]
    average_rating = st.mean(ratings)
    median_rating = st.median(ratings)

    best_val = max(ratings)
    worst_val = min(ratings)

    best_movies = [title for title, data in movies.items() if data["rating"] == best_val]
    worst_movies = [title for title, data in movies.items() if data["rating"] == worst_val]

    print("\n--- Stats ---")
    print(f"Average rating: {average_rating:.1f}")
    print(f"Median rating: {median_rating:.1f}")
    print(f"Best movie(s): {', '.join(best_movies)} ({best_val:.1f})")
    print(f"Worst movie(s): {', '.join(worst_movies)} ({worst_val:.1f})")


def random_movie(movies):
    """Print a random movie."""
    if not movies:
        print(f'{RED}No movies in database.{RESET}')
        return

    title, data = rd.choice(list(movies.items()))
    print(f'Random choice: {title} ({data["year"]}): {data["rating"]:.1f}')


def similarity_ratio(word_a, word_b):
    """Return similarity ratio between two strings (0..1)."""
    word_a, word_b = word_a.lower(), word_b.lower()
    matches = 0
    a_used = [False] * len(word_a)
    b_used = [False] * len(word_b)

    for i, char_a in enumerate(word_a):
        for j, char_b in enumerate(word_b):
            if not a_used[i] and not b_used[j] and char_a == char_b:
                matches += 1
                a_used[i] = True
                b_used[j] = True
                break

    return (2 * matches) / (len(word_a) + len(word_b)) if (word_a and word_b) else 0


def custom_get_close_matches(word, possibilities, max_results=3, cutoff=0.5):
    """Return top-N close matches above cutoff."""
    scored = []
    for possibility in possibilities:
        ratio = similarity_ratio(word, possibility)
        if ratio >= cutoff:
            scored.append((ratio, possibility))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [possibility for _, possibility in scored[:max_results]]


def search_movie(movies):
    """Search movies by substring; suggest close matches if none found."""
    if not movies:
        print(f'{RED}No movies in database.{RESET}')
        return

    query = prompt_non_empty(f'{YELLOW}Enter part of movie name: {RESET}').lower()
    found = False

    for title, data in movies.items():
        if query in title.lower():
            print(f'{title} ({data["year"]}): {data["rating"]:.1f}')
            found = True

    if not found:
        similar = custom_get_close_matches(query, movies.keys(), cutoff=0.5)
        if similar:
            print(f'\nMovie "{query}" not found. Did you mean:')
            for suggestion in similar:
                print(
                    f' - {suggestion} ({movies[suggestion]["year"]}): '
                    f'{movies[suggestion]["rating"]:.1f}'
                )
        else:
            print(f'{RED}No similar movies found.{RESET}')


def movies_sorted(movies):
    """Sort by rating (descending) and print."""
    if not movies:
        print(f'{RED}No movies in database.{RESET}')
        return

    print(f"\n{BOLD}Sorted by rating (descending):{RESET}\n")
    for title, data in sorted(movies.items(), key=lambda x: x[1]["rating"], reverse=True):
        print(f'{title} ({data["year"]}): {data["rating"]:.1f}')


def movies_sorted_by_year(movies):
    """List movies in chronological order (by year)."""
    if not movies:
        print(f'{RED}No movies in database.{RESET}')
        return

    while True:
        order = input(
            f'{YELLOW}Show latest movies first? (y=Yes, n=No): {RESET}'
        ).strip().lower()

        if order in {"y", "n"}:
            reverse = (order == "y")
            break

        print(f'{RED}Invalid input. Please enter y or n.{RESET}')

    print(f"\n{BOLD}Sorted by year:{RESET}\n")
    for title, data in sorted(movies.items(), key=lambda x: x[1]["year"], reverse=reverse):
        print(f'{title} ({data["year"]}): {data["rating"]:.1f}')


def filter_movies(movies):
    """Filter movies by optional minimum rating, start year, end year."""
    if not movies:
        print(f'{RED}No movies in database.{RESET}')
        return

    min_rating = prompt_optional_float(
        f"{YELLOW}Enter minimum rating (leave blank for no minimum rating): {RESET}",
        1.0,
        10.0,
    )
    start_year = prompt_optional_int(
        f"{YELLOW}Enter start year (leave blank for no start year): {RESET}",
        1800,
        2100,
    )
    end_year = prompt_optional_int(
        f"{YELLOW}Enter end year (leave blank for no end year): {RESET}",
        1800,
        2100,
    )

    filtered = []
    for title, data in movies.items():
        rating = data["rating"]
        year = data["year"]

        if min_rating is not None and rating < min_rating:
            continue
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue

        filtered.append((title, year, rating))

    print("\nFiltered Movies:")
    if not filtered:
        print(f'{RED}No movies match your criteria.{RESET}')
        return

    # Optional: stable readable output (chronological)
    filtered.sort(key=lambda x: x[1])

    for title, year, rating in filtered:
        print(f"{title} ({year}): {rating:.1f}")


def create_histogram(movies):
    """Create and save a histogram PNG of ratings."""
    if not movies:
        print(f'{RED}No movies in database.{RESET}')
        return

    filename = prompt_non_empty(
        f'{YELLOW}Enter filename to save histogram (without extension): {RESET}'
    )

    ratings = [data["rating"] for data in movies.values()]
    plt.hist(ratings, bins=range(1, 12), edgecolor="black", color="skyblue")
    plt.title("Movie Ratings Histogram")
    plt.xlabel("Rating")
    plt.ylabel("Count")
    plt.savefig(f"{filename}.png")
    plt.close()
    print(f"Histogram saved as {filename}.png")


def generate_website():
    """Generate _static/index.html from _static/index_template.html."""
    movies = storage.list_movies()

    base_dir = os.path.dirname(__file__)
    template_path = os.path.join(base_dir, "_static", "index_template.html")
    output_path = os.path.join(base_dir, "_static", "index.html")

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    items = []
    for title, data in movies.items():
        safe_title = html.escape(title)
        year = data.get("year", "")
        poster = (data.get("poster") or "").strip()

        if not poster or poster == "N/A" or not poster.startswith(("http://", "https://")):
            img_tag = '<div class="movie-poster"></div>'
        else:
            img_tag = (
                f'<img class="movie-poster" '
                f'src="{html.escape(poster)}" '
                f'alt="{safe_title} poster" '
                f'onerror="this.outerHTML=\'<div class=&quot;movie-poster&quot;></div>\';" />'
            )

        items.append(
            f"""<li>
    <div class="movie">
        {img_tag}
        <div class="movie-title">{safe_title}</div>
        <div class="movie-year">{year}</div>
    </div>
</li>"""
        )

    movie_grid_html = "\n".join(items)

    html_out = template.replace("__TEMPLATE_TITLE__", "My Movie App")
    html_out = html_out.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    print("Website was generated successfully.")


def main():
    """Menu-driven movies database - SQL storage."""
    menu = {
        0: "Exit",
        1: "List movies",
        2: "Add movie",
        3: "Delete movie",
        4: "Update movie",
        5: "Stats",
        6: "Random movie",
        7: "Search movie",
        8: "Movies sorted by rating",
        9: "Create Rating Histogram",
        10: "Movies sorted by year",
        11: "Filter movies",
        12: "Generate website"
    }

    actions = {
        1: lambda: print_movies(storage.list_movies()),
        2: add_movie_f,
        3: delete_movie,
        4: update_movie,
        5: lambda: stats(storage.list_movies()),
        6: lambda: random_movie(storage.list_movies()),
        7: lambda: search_movie(storage.list_movies()),
        8: lambda: movies_sorted(storage.list_movies()),
        9: lambda: create_histogram(storage.list_movies()),
        10: lambda: movies_sorted_by_year(storage.list_movies()),
        11: lambda: filter_movies(storage.list_movies()),
        12: generate_website
    }

    while True:
        print(f'\n{BOLD}{CYAN}********** My Movies Database **********{RESET}\n')
        for i, operation in menu.items():
            print(f'{BOLD}{CYAN}{i}. {operation}{RESET}')

        try:
            choice = int(input(f"{YELLOW}\nEnter choice (0-12): {RESET}"))
        except ValueError:
            print(f"{RED}Invalid input.{RESET} Try again (0-12)")
            continue

        if choice == 0:
            print("Bye!")
            break

        action = actions.get(choice)
        if action is None:
            print(f"{RED}Invalid input.{RESET} Try again (0-11)")
            continue

        action()
        input(f"{YELLOW}\nPress Enter to continue...{RESET}")


if __name__ == "__main__":
    main()
