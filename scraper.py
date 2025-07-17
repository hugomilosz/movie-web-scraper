import requests
import time
import random
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from config import HEADERS, BOX_OFFICE_MOJO_BASE_URL, IMDB_BASE_URL

class Scraper:
    """Handles all web scraping operations."""

    def _make_request(self, url: str) -> Optional[str]:
        """Makes an HTTP GET request with error handling."""
        try:
            time.sleep(random.uniform(1.0, 2.0))
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"  Error making request to {url}: {e}")
            return None
        
    def scrape_yearly_movies(self, year: int, top_n: Optional[int] = None, bottom_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrapes a list of movies for a given year from Box Office Mojo.
        """
        limit_str = f"top {top_n}" if top_n else "all"
        if bottom_n:
            limit_str += f" & bottom {bottom_n}"

        print(f"\n--- Scraping movie list for {year} ({limit_str}) ---")
        url = f"{BOX_OFFICE_MOJO_BASE_URL}/year/{year}/"
        html = self._make_request(url)
        if not html: return []
        
        soup = BeautifulSoup(html, 'html.parser')
        movies = []
        if not (table := soup.find('table')):
            print(f"No data table found for year {year}")
            return []
            
        all_rows = table.find_all('tr')[1:]
        
        rows_to_process = []
        if top_n:
            rows_to_process.extend(all_rows[:top_n])
        if bottom_n:
            # Add the last n rows
            rows_to_process.extend(all_rows[-bottom_n:])
        
        # If no limits were specified, process all rows
        if not top_n and not bottom_n:
            rows_to_process = all_rows
        
        processed_links = set()
        for row in rows_to_process:
            movie_details = {}
            
            cols = row.find_all('td')
            if len(cols) >= 10 and (link := cols[1].find('a', href=True)):
                # Use the link's href to prevent processing duplicates
                href = link['href']
                if href in processed_links:
                    continue
                processed_links.add(href)
                
                title = link.text.strip()
                print(f"  Processing: {title}")
                
                mojo_url = BOX_OFFICE_MOJO_BASE_URL + href
                mojo_data = self._scrape_movie_details_mojo(mojo_url)
                movie_details.update(mojo_data)
                
                if imdb_id := movie_details.get('imdb_id'):
                    imdb_details = self._scrape_movie_details_imdb(imdb_id)
                    movie_details.update(imdb_details)
                
                movie_details.update({
                    'title': title,
                    'domestic_gross': cols[7].text.strip(),
                    'release_date': cols[8].text.strip(),
                    'year': year
                })
                
                movies.append(movie_details)
        return movies

    
    def _scrape_movie_details_mojo(self, url: str) -> Dict[str, Any]:
        """Scrapes details for a single movie from its Box Office Mojo page."""
        html = self._make_request(url)
        if not html: return {}
            
        soup = BeautifulSoup(html, 'html.parser')
        details: Dict[str, Any] = {}
        
        if (imdb_link := soup.select_one('a[href*="imdb.com/title/"]')) and (match := re.search(r'title/(tt\d+)', imdb_link.get('href'))):
            details['imdb_id'] = match.group(1)

        def get_summary_detail(label_text: str) -> Optional[str]:
            if label_el := soup.find('span', string=lambda t: t and label_text in t):
                if value_el := label_el.find_next_sibling('span'):
                    raw_text = value_el.text.replace('See full company information', '').strip()
                    return raw_text.split('\n')[0].strip()
            return None

        details['distributor'] = get_summary_detail('Distributor')
        details['runtime'] = get_summary_detail('Running Time')
        
        if worldwide_el := soup.select_one('span:-soup-contains("Worldwide")'):
             if value_el := worldwide_el.find_next_sibling('span'):
                details['worldwide_gross'] = value_el.text.strip()

        return details

    def _scrape_movie_details_imdb(self, imdb_id: str) -> Dict[str, Any]:
        """Scrapes additional details for a single movie from its IMDb page."""
        url = f"{IMDB_BASE_URL}/title/{imdb_id}/"
        html = self._make_request(url)
        if not html: return {}
            
        soup = BeautifulSoup(html, 'html.parser')
        details: Dict[str, Any] = {}

        if poster_el := soup.select_one('.ipc-poster img.ipc-image'):
            details['poster_image_url'] = poster_el.get('src')
        
        if genres := soup.select('div.ipc-chip-list a.ipc-chip'):
            details['genres'] = [g.text.strip() for g in genres]
        
        director_items = soup.select('li[data-testid="title-pc-principal-credit"]')
        for item in director_items:
            if "Director" in item.get_text():
                directors = item.select("a")
                details['director'] = [d.text.strip() for d in directors if d.text.strip().lower() not in ['director', 'directors']]
                break

        if cast_els := soup.select('a[data-testid="title-cast-item__actor"]'):
            details['top_cast'] = [actor.text.strip() for actor in cast_els[:5]]

        if rating_el := soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating__score"] span'):
            details['imdb_rating'] = rating_el.text.strip()

        return details