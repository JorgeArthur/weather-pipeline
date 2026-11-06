import logging
import sys

from extract import CITIES, build_session, fetch_city
from load import load_raw, load_clean
from transform import transform_hourly

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("pipeline")


def run() -> int:
    session = build_session()
    failures = []

    for city in CITIES:
        try:
            payload = fetch_city(session, city)
            load_raw(city, payload)
            rows = transform_hourly(city, payload)
            n = load_clean(rows)
            log.info("loaded city=%s rows=%s", city, n)
        except Exception:
            log.exception("failed city=%s", city)
            failures.append(city)

    if failures:
        log.error("pipeline finished with failures: %s", failures)
        return 1
    log.info("pipeline finished successfully")
    return 0


if __name__ == "__main__":
    sys.exit(run())