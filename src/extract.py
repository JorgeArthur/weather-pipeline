import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger(__name__)

CITIES = {
    "london":   (51.5072, -0.1276),
    "tokyo":    (35.6762, 139.6503),
    "new_york": (40.7128, -74.0060),
    "sao_paulo": (-23.5505, -46.6333),
}

URL = "https://api.open-meteo.com/v1/forecast"

def build_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=3, backoff_factor=2,
                  status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s

def fetch_city(session: requests.Session, city: str) -> dict:
    lat, lon = CITIES[city]
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation,wind_speed_10m",
        "past_days": 1,
        "forecast_days": 1,
        "timezone": "UTC",
    }
    resp = session.get(URL, params=params, timeout=30)
    resp.raise_for_status()
    log.info("fetched city=%s status=%s", city, resp.status_code)
    return resp.json()