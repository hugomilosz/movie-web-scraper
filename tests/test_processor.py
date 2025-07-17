import unittest
from processor import process_movie_data
from tests.sample_data.sample_raw_movie import SAMPLE_RAW_MOVIE, SAMPLE_ANOMALOUS_MOVIE

class TestProcessor(unittest.TestCase):
    """Tests the data processing and cleaning functions."""

    def setUp(self):
        self.processed_movie = process_movie_data(SAMPLE_RAW_MOVIE)
        self.processed_anomalous_movie = process_movie_data(SAMPLE_ANOMALOUS_MOVIE)

    def test_currency_cleaning(self):
        """Test if currency strings are correctly converted to integers."""
        self.assertEqual(self.processed_movie['domestic_gross'], 100000000)
        self.assertEqual(self.processed_movie['worldwide_gross'], 250000000)

    def test_runtime_cleaning(self):
        """Test if runtime string is correctly converted to total minutes."""
        # 1 hr 54 min == 114 minutes
        self.assertEqual(self.processed_movie['runtime_minutes'], 114)

    def test_list_to_string_conversion(self):
        """Test if lists (like genres and directors) are joined into a string."""
        self.assertEqual(self.processed_movie['director'], 'First Director, Second Director')
        self.assertEqual(self.processed_movie['genres'], 'Action, Adventure')

    def test_quality_issue_validation(self):
        """Test if the quality issue flag is correctly set for anomalous data."""
        self.assertIsNone(self.processed_movie['quality_issue'])
        self.assertIsNotNone(self.processed_anomalous_movie['quality_issue'])
        self.assertIn('Anomalous gross', self.processed_anomalous_movie['quality_issue'])

    def test_missing_runtime(self):
        """Test that runtime_minutes is None when runtime is missing."""
        movie_data = {'runtime': None}
        processed_data = process_movie_data(movie_data)
        self.assertIsNone(processed_data.get('runtime_minutes'))

    def test_missing_optional_data(self):
        """Test processing a movie with many missing fields."""
        raw_movie = {
            'imdb_id': 'tt9999999',
            'title': 'Minimal Movie'
        }
        processed_data = process_movie_data(raw_movie)
        
        # Assert that the optional fields are None
        self.assertEqual(processed_data['title'], 'Minimal Movie')
        self.assertIsNone(processed_data.get('runtime_minutes'))
        self.assertIsNone(processed_data.get('imdb_rating'))

if __name__ == '__main__':
    unittest.main()