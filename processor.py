import re
from typing import Optional, Dict, Any

def _clean_currency(text_value: Optional[str]) -> Optional[int]:
    if not text_value or not isinstance(text_value, str): return None
    try:
        return int(re.sub(r'[^\d]', '', text_value))
    except (ValueError, TypeError):
        return None

def _clean_runtime(text_value: Optional[str]) -> Optional[int]:
    """Converts a runtime string (e.g., "1 hr 54 min") into total minutes."""
    if not text_value: return None
    h_match = re.search(r'(\d+)\s+hr', text_value)
    m_match = re.search(r'(\d+)\s+min', text_value)
    hours = int(h_match.group(1)) if h_match else 0
    minutes = int(m_match.group(1)) if m_match else 0
    total_minutes = (hours * 60) + minutes
    return total_minutes if total_minutes > 0 else None

def process_movie_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Cleans and validates the data in a raw movie dictionary."""
    cleaned_data = raw_data.copy()

    cleaned_data['domestic_gross'] = _clean_currency(raw_data.get('domestic_gross'))
    cleaned_data['worldwide_gross'] = _clean_currency(raw_data.get('worldwide_gross'))
    cleaned_data['runtime_minutes'] = _clean_runtime(raw_data.get('runtime'))
    cleaned_data.pop('runtime', None)

    if rating := raw_data.get('imdb_rating'):
        cleaned_data['imdb_rating'] = float(rating.split('/')[0])
    
    # Covert list-based fields to comma-separated strings
    for key in ['genres', 'top_cast', 'director']:
        if key in cleaned_data and isinstance(cleaned_data[key], list):
            cleaned_data[key] = ', '.join(cleaned_data[key])
    
    # Perform anomalous data check
    cleaned_data['quality_issue'] = None
    if (d := cleaned_data.get('domestic_gross')) and (w := cleaned_data.get('worldwide_gross')) and d > w:
        cleaned_data['quality_issue'] = 'Anomalous gross: domestic > worldwide'

    return cleaned_data