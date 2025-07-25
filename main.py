from datetime import datetime
from scraper import Scraper
from database import DatabaseManager
from processor import process_movie_data
from config import DB_PATH

def main():
    """Main function to run the scraper."""
    scraper = Scraper()
    db_manager = DatabaseManager(DB_PATH)

    # Define the year range and range of films to scrape
    start_year = 2010
    end_year = 2020
    top_n, bottom_n = 3, 3
    
    all_raw_movies = []
    for year in range(start_year, end_year + 1):
        yearly_movies = scraper.scrape_yearly_movies(year, top_n, bottom_n)
        all_raw_movies.extend(yearly_movies)
        
    print(f"\n--- Processing {len(all_raw_movies)} movies ---")
    cleaned_movies = [process_movie_data(movie) for movie in all_raw_movies]
    
    print(f"\n--- Saving {len(cleaned_movies)} movies to database ---")
    db_manager.save_movies(cleaned_movies)
        
    print("\nScraping process complete.")

if __name__ == "__main__":
    main()