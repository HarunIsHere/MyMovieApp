# test_omdb_api.py
import requests

API_KEY = "3bec4110"

def main():
    url = "http://www.omdbapi.com/"
    params = {"apikey": API_KEY, "t": "Titanic"}

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    if data.get("Response") == "True":
        print("✅ API access works.")
        print(f"Title: {data.get('Title')}")
        print(f"Year: {data.get('Year')}")
        print(f"IMDb rating: {data.get('imdbRating')}")
    else:
        print("❌ API call failed:", data.get("Error"))
        print("Full response:", data)

if __name__ == "__main__":
    main()