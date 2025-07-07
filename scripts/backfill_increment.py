import logging
from services.scrape import scrape_table
from services.db_utils import insert_regular_market
from utils.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


URL = "https://www.ccilindia.com/web/ccil/rbi-nds-om1"
TABLE = "ndsomEntityTable"

RESPONSE_HEADER_MAPPING = {
    "ismt_idntr": "Security Description",
    "ttc": "Trades",
    "tta": "TTA",
    "op": "Open",
    "hi": "High",
    "lo": "Low",
    "ltp": "LTP",
    "arrow": "Arrow",
    "indicator": "Indicator",
    "lty": "LTY",
    "prev_trad_rate": "Previous Trade Rate",
    "trade_yeild": "Trade Yield",
    "mrkt_indc": "Market Indicator",
    "book_indc": "Book Indicator"
}
 
def main():
    """
    Main function to perform update.
    Scrapes data and inserts it into the database.
    """
    logger.info("Start scraping...")
    scraped_data = scrape_table(url=URL, table_name=TABLE, method='direct')
    logger.info("Scrape finished.")
    if scraped_data:
        insert_regular_market(scraped_data)
    else:
        logger.warning(f"No data scraped from {TABLE} at {URL}.")

if __name__ == "__main__":
    main()
