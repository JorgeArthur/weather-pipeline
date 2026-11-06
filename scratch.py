import sys
sys.path.insert(0, "src")

from extract import build_session, fetch_city
from load import load_raw

data = fetch_city(build_session(), "london")
load_raw("london", data)
print("load_raw finished without error")
