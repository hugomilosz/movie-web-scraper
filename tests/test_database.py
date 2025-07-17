import unittest
import os
import sqlite3
from database import DatabaseManager
from processor import process_movie_data
from tests.sample_data.sample_raw_movie import SAMPLE_RAW_MOVIE

class TestDatabase(unittest.TestCase):
    """Tests the database management functions."""

    def setUp(self):
        """Set up a temporary test database before each test."""
        self.test_db_path = "test_movies.db"
        self.db_manager = DatabaseManager(db_path=self.test_db_path)

    def tearDown(self):
        """Remove the test database after each test."""
        os.remove(self.test_db_path)

    def test_save_and_retrieve_movie(self):
        """Test saving a movie to the database and retrieving it."""
        cleaned_movie = process_movie_data(SAMPLE_RAW_MOVIE)
        self.db_manager.save_movies([cleaned_movie])

        # Retrieve data directly from test db to verify
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, runtime_minutes FROM movies WHERE imdb_id = ?", (cleaned_movie['imdb_id'],))
            result = cursor.fetchone()

        # Assert the retrieved data is correct
        self.assertIsNotNone(result)
        self.assertEqual(result[0], cleaned_movie['title'])
        self.assertEqual(result[1], 114)

    def test_saving_no_movies(self):
        """Test that the save_movies function handles an empty list."""
        self.db_manager.save_movies([])

if __name__ == '__main__':
    unittest.main()