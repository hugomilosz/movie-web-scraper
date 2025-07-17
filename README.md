# Multimodal Movie Data Scraper

A Python tool for collecting and organising movie data from multiple sources. It scrapes both text (e.g. box office, cast, genres) and images (e.g. movie posters), processes the raw data, and stores it in a local SQLite database for easy querying.

***
## Key Features

* **Multimodal Data Collection**: Gathers both textual data (financials, cast, genres) and visual data (poster images) to create a multimodal dataset.
* **Multi-Source Scraping**: Collects information from Box Office Mojo and IMDb, combining the strengths of each source.
* **Dedicated Data Quality Pipeline**: A data processing module cleans, standardises, and validates the raw scraped data.
* **Structured Storage**: Saves the cleaned, structured data into a SQLite database, providing a reliable and queryable dataset.
* **Libraries**:
    * `requests` for making HTTP requests
    * `BeautifulSoup4` for HTML parsing

***
## Project Structure

The project is structured as followed:

```
movie-web-scraper/
├── config.py
├── database.py
├── main.py
├── processor.py
├── requirements.txt
├── scraper.py
└── tests/
    ├── init.py
    ├── sample_data/
    │   ├── sample_imdb_page.html
    │   └── sample_mojo_page.html
    ├── test_database.py
    └── test_processor.py
```

***
## Setup and Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hugomilosz/movie-web-scraper.git
    cd movie-web-scraper
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the scraper:**
    The `main.py` script can be altered to scrape the top and/or bottom movies from a given year.
    ```bash
    python main.py
    ```
    The cleaned data will be saved in `movies.db`.

***
## Example Output

A single record in the final `movies.db` database looks like this after being scraped and processed:

| Field | Example Value |
| :--- | :--- |
| `imdb_id` | `tt1517268` |
| `title` | `Barbie` |
| `year` | `2023` |
| `release_date` | `Jul 21` |
| `distributor` | `Warner Bros.` |
| `domestic_gross` | `636238421` |
| `worldwide_gross`| `1445638421` |
| `director` | `Greta Gerwig` |
| `imdb_rating` | `6.9` |
| `runtime_minutes`| `114` |
| `poster_image_url`| `https://m.media-amazon.com/images/M/....jpg` |
| `genres` | `Adventure, Comedy, Fantasy` |
| `top_cast` | `Margot Robbie, Ryan Gosling, Issa Rae` |
| `quality_issue` | `None` |

