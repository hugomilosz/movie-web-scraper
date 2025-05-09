import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import re
from datetime import datetime

class MovieScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.box_office_mojo_base_url = "https://www.boxofficemojo.com"
        self.imdb_base_url = "https://www.imdb.com"
        
    def _make_request(self, url):
        """Make a request with error handling and random delay to be respectful."""
        try:
            # Add a random delay between requests to avoid overloading the server
            time.sleep(random.uniform(1, 3))
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None
    
    def scrape_box_office_yearly(self, year):
        """Scrape top movies from Box Office Mojo for a specific year."""
        url = f"{self.box_office_mojo_base_url}/year/{year}"
        html = self._make_request(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        movies = []
        
        # Find the main table containing movie data
        table = soup.find('table')
        if not table:
            print(f"No table found for year {year}")
            return []
            
        rows = table.find_all('tr')
        # Skip header row
        for row in rows[1:3]:
            cols = row.find_all('td')
            if len(cols) >= 10:  # Ensure we have enough columns
                movie_link = cols[1].find('a')
                if movie_link:
                    title = movie_link.text.strip()
                    movie_url = movie_link.get('href')
                    gross = cols[7].text.strip()
                    release_date = cols[8].text.strip()
                    
                    # Get additional details from the movie's page
                    movie_details = self.scrape_movie_details(self.box_office_mojo_base_url + movie_url)
                    
                    movie_data = {
                        'title': title,
                        'domestic_gross': gross,
                        'release_date': release_date,
                        'year': year,
                        **movie_details
                    }

                    # Calculate domestic vs worldwide ratio
                    if 'domestic_gross' in movie_data and 'worldwide_gross' in movie_data:
                        try:
                            domestic = int(re.sub(r'[^\d]', '', movie_data['domestic_gross']))
                            worldwide = int(re.sub(r'[^\d]', '', movie_data['worldwide_gross']))
                            if worldwide > 0:
                                movie_data['domestic_vs_worldwide_ratio'] = round(domestic / worldwide, 2)
                            else:
                                movie_data['domestic_vs_worldwide_ratio'] = None
                        except:
                            movie_data['domestic_vs_worldwide_ratio'] = None
                    
                    movies.append(movie_data)
                    print(f"Scraped: {title}")
        
        return movies
    
    def scrape_movie_details(self, url):
        """Scrape detailed information for a specific movie from Box Office Mojo."""
        html = self._make_request(url)
        if not html:
            return {}
            
        soup = BeautifulSoup(html, 'html.parser')
        details = {}
        
        # Get IMDB ID for further scraping
        imdb_link = soup.select_one('a[href*="imdb.com/title/"]')
        if imdb_link:
            imdb_url = imdb_link.get('href')
            imdb_id_match = re.search(r'title/(tt\d+)', imdb_url)
            if imdb_id_match:
                details['imdb_id'] = imdb_id_match.group(1)
                
        # Extract budget if available
        budget_element = soup.select_one('span:-soup-contains("Budget")')
        if budget_element and budget_element.find_next('span'):
            budget_text = budget_element.find_next('span').text.strip()
            details['budget'] = budget_text
            
        # Extract worldwide gross
        worldwide_element = soup.select_one('span:-soup-contains("Worldwide")')
        if worldwide_element and worldwide_element.find_next('span'):
            worldwide_text = worldwide_element.find_next('span').text.strip()
            details['worldwide_gross'] = worldwide_text
            
        # Extract distributor
        distributor_element = soup.select_one('span:-soup-contains("Distributor")')
        if distributor_element and distributor_element.find_next('span'):
            distributor = distributor_element.find_next('span').text.strip()
            details['distributor'] = distributor

        # Extract opening weekend gross
        # # Extract opening weekend gross and number of theaters
        # opening_element = soup.select_one('span:-soup-contains("Opening")')
        # if opening_element and opening_element.find_next('span'):
        #     opening_detail = opening_element.find_next('span')
        #     if opening_detail:
        #         opening_text = opening_detail.text.strip()
                
        #         # Debugging print to see the raw opening text
        #         print("Opening Detail:", opening_text)
                    
        #     # Match the gross value (e.g. "$162,022,044")
        #     gross_match = re.search(r'\$([\d,]+)', opening_text)
        #     if gross_match:
        #         details['opening_weekend_gross'] = gross_match.group(0)  # Gross value only
            
        #     # Match the theater count (e.g. "4,243 theaters")
        #     theater_match = re.search(r'([\d,]+)\s+theaters', opening_text)
        #     if theater_match:
        #         details['opening_weekend_theaters'] = theater_match.group(1)  # Number of theaters
        
        # Get additional details from IMDB if we have an ID
        if 'imdb_id' in details:
            imdb_details = self.scrape_imdb_details(details['imdb_id'])
            details.update(imdb_details)
            
        return details
    
    def scrape_imdb_details(self, imdb_id):
        """Scrape additional movie details from IMDB."""
        url = f"{self.imdb_base_url}/title/{imdb_id}"
        html = self._make_request(url)
        if not html:
            return {}
            
        soup = BeautifulSoup(html, 'html.parser')
        details = {}
        
        # Extract genre
        genre_elements = soup.select('div.ipc-chip-list a.ipc-chip')
        if genre_elements:
            details['genres'] = [genre.text.strip() for genre in genre_elements]
            
        # Extract director(s)
        director_section = soup.select_one('li[data-testid="title-pc-principal-credit"]:has(a[href*="/name/"])')
        if director_section:
            directors = director_section.select('a[href*="/name/"]')
            if directors:
                details['director'] = ', '.join([d.text.strip() for d in directors])

                
        # Extract top cast
        cast_elements = soup.select('a[data-testid="title-cast-item__actor"]')
        if cast_elements:
            details['top_cast'] = [actor.text.strip() for actor in cast_elements[:5]]
            
        # Extract rating
        rating_element = soup.select_one('span[data-testid="hero-rating-bar__aggregate-rating__score"]')
        if rating_element:
            details['imdb_rating'] = rating_element.text.strip()
            
        # Extract runtime
        runtime_element = soup.select_one('li[data-testid="title-techspec_runtime"]')
        if runtime_element:
            runtime_content = runtime_element.find('div', class_='ipc-metadata-list-item__content')
            if runtime_content:
                details['runtime'] = runtime_content.text.strip()

            
        return details
    
    def save_to_csv(self, movies, filename):
        """Save scraped movie data to a CSV file."""
        if not movies:
            print("No movies to save.")
            return
            
        # Get all possible keys from all movie dictionaries
        fieldnames = set()
        for movie in movies:
            fieldnames.update(movie.keys())
            
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(movies)
        
        print(f"Saved {len(movies)} movies to {filename}")

def main():
    scraper = MovieScraper()
    
    # Scrape movies from the last 10 years
    all_movies = []
    current_year = datetime.now().year
    
    for year in range(current_year - 2, current_year + 1):
        print(f"Scraping movies from {year}...")
        year_movies = scraper.scrape_box_office_yearly(year)
        all_movies.extend(year_movies)
        
        # Save after each year as a checkpoint
        scraper.save_to_csv(year_movies, f"movies_{year}.csv")
        
    # Save all movies to a combined file
    scraper.save_to_csv(all_movies, "all_movies.csv")
    
if __name__ == "__main__":
    main()