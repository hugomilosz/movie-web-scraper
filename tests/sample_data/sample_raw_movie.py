# A sample of raw data
SAMPLE_RAW_MOVIE = {
    'imdb_id': 'tt1234567',
    'title': 'Test Movie',
    'domestic_gross': '$100,000,000',
    'worldwide_gross': '$250,000,000',
    'runtime': '1 hr 54 min',
    'director': ['First Director', 'Second Director'],
    'genres': ['Action', 'Adventure'],
    'imdb_rating': '8.5/10'
}

# A sample with a data quality issue for testing validation
SAMPLE_ANOMALOUS_MOVIE = {
    'imdb_id': 'tt7654321',
    'title': 'Anomalous Test Movie',
    'domestic_gross': '$300,000,000', # Higher than worldwide
    'worldwide_gross': '$250,000,000',
    'runtime': '2 hr 5 min'
}