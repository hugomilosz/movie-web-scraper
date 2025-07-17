import unittest
from unittest.mock import patch, Mock
from scraper import Scraper

class TestScraper(unittest.TestCase):
    """Tests the Scraper class's parsing logic using mock HTML data."""

    @patch('scraper.requests.get')
    def test_mojo_parsing(self, mock_get):
        """Test parsing key details from a saved Box Office Mojo HTML file."""
        with open('tests/sample_data/sample_mojo_page.html', 'r', encoding='utf-8') as f:
            sample_html = f.read()

        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        scraper = Scraper()
        details = scraper._scrape_movie_details_mojo("http://fake-url.com")
        
        self.assertEqual(details['distributor'], 'Warner Bros.')

    @patch('scraper.requests.get')
    def test_imdb_parsing(self, mock_get):
        """Test parsing key details from a saved IMDb HTML file."""
        with open('tests/sample_data/sample_imdb_page.html', 'r', encoding='utf-8') as f:
            sample_html = f.read()

        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        scraper = Scraper()
        details = scraper._scrape_movie_details_imdb("tt1517268")

        self.assertIn('Greta Gerwig', details['director'])
        self.assertIn('Adventure', details['genres'])

    @patch('scraper.Scraper._scrape_movie_details_imdb')
    @patch('scraper.Scraper._scrape_movie_details_mojo')
    @patch('scraper.requests.get')
    def test_scrape_yearly_movies_logic(self, mock_get, mock_mojo_details, mock_imdb_details):
        """Test the main yearly scraping loop."""
        with open('tests/sample_data/sample_yearly_page.html', 'r', encoding='utf-8') as f:
            sample_html = f.read()
        
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        mock_mojo_details.return_value = {'imdb_id': 'tt12345'}
        mock_imdb_details.return_value = {'director': 'Test Director'}

        scraper = Scraper()
        movies = scraper.scrape_yearly_movies(2023)
        
        self.assertGreater(len(movies), 9)
        self.assertEqual(movies[0]['title'], 'Barbie')