from scraper import Scraper
from processor import process_movie_data
import yaml

def format_and_save_as_yaml(movie_data: list, output_path: str):
    """
    Formats the cleaned movie data to match the needed format.
    """
    formatted_movies = []
    for movie in movie_data:
        if movie.get('title') and movie.get('year') and movie.get('domestic_gross') is not None and movie.get('worldwide_gross') is not None:
            formatted_movies.append({
                'title': movie['title'],
                'year': movie['year'],
                'worldwideGross': movie['worldwide_gross'],
                'domesticGross': movie['domestic_gross']
            })

    # Construct Unity YAML structure
    final_yaml_structure = {
        'MonoBehaviour': {
            'm_ObjectHideFlags': 0,
            'm_CorrespondingSourceObject': {'fileID': 0},
            'm_PrefabInstance': {'fileID': 0},
            'm_PrefabAsset': {'fileID': 0},
            'm_GameObject': {'fileID': 0},
            'm_Enabled': 1,
            'm_EditorHideFlags': 0,
            'm_Script': {'fileID': 11500000, 'guid': '4b6b9ca2db27f429fb816ca88b10e14a', 'type': 3},
            'm_Name': 'MainMovieDB',
            'm_EditorClassIdentifier': '',
            'movies': formatted_movies
        }
    }

    # Write the data to YAML
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("%YAML 1.1\n")
            f.write("%TAG !u! tag:unity3d.com,2011:\n")
            f.write("--- !u!114 &11400000\n")
            yaml.dump(final_yaml_structure, f, sort_keys=False, indent=2)
        print(f"Saved data to {output_path}")
    except Exception as e:
        print(f"\nError saving YAML file: {e}")


def run_scrape_and_format():
    print("Starting scraping")

    scraper = Scraper()
    start_year = 1990
    end_year = 2024
    top_movies_count = 10

    all_raw_movies = []
    for year in range(start_year, end_year + 1):
        yearly_movies = scraper.scrape_yearly_movies(year=year, top_n=top_movies_count)
        all_raw_movies.extend(yearly_movies)

    if not all_raw_movies:
        print("No movies were found across the specified years. Exiting.")
        return

    # Clean the data
    print(f"\n--- Processing a total of {len(all_raw_movies)} movies ---")
    cleaned_movies = [process_movie_data(movie) for movie in all_raw_movies]

    output_filename = 'MainMovieDB.asset'
    format_and_save_as_yaml(cleaned_movies, output_filename)

if __name__ == "__main__":
    run_scrape_and_format()