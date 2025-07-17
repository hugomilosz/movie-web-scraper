import sqlite3
from typing import List, Dict, Any
from config import DB_PATH

class DatabaseManager:
    """Manages all database operations."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._setup_database()

    def _setup_database(self) -> None:
        """Creates the SQLite database and table if they don't already exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                    imdb_id TEXT PRIMARY KEY, title TEXT, year INTEGER, release_date TEXT,
                    distributor TEXT, domestic_gross INTEGER, worldwide_gross INTEGER,
                    director TEXT, imdb_rating REAL, runtime_minutes INTEGER, poster_image_url TEXT,
                    genres TEXT, top_cast TEXT, quality_issue TEXT
                )
            ''')
            print("Database setup complete.")

    def save_movies(self, movies: List[Dict[str, Any]]) -> None:
        """Saves a list of cleaned movie data dictionaries to the SQLite database."""
        if not movies:
            print("No movies to save.")
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            saved_count = 0
            
            # Get the columns of the table
            cursor.execute("PRAGMA table_info(movies)")
            valid_keys = {row[1] for row in cursor.fetchall()}

            for movie in movies:
                if 'imdb_id' not in movie: continue
                
                # Filter the movie dictionary to only include keys that are valid columns in our defined table
                movie_to_save = {k: v for k, v in movie.items() if k in valid_keys}
                
                cols = ', '.join(movie_to_save.keys())
                placeholders = ', '.join('?' * len(movie_to_save))
                sql = f"INSERT OR REPLACE INTO movies ({cols}) VALUES ({placeholders})"
                
                try:
                    cursor.execute(sql, list(movie_to_save.values()))
                    saved_count += 1
                except sqlite3.Error as e:
                    print(f"DB Error for movie {movie.get('title')}: {e}")
            
            print(f"Successfully saved or updated {saved_count} movies to {self.db_path}")