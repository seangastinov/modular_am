import logging
from services.scrape import scrape_table
from services.db_utils import insert_regular_market
from utils.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

URL = "https://www.ccilindia.com/web/ccil/rbi-nds-om1"
TABLE = "ndsomEntityTable"

def main():
    """
    Main function to perform update.
    Scrapes data and inserts it into the database.
    """
    logger.info("Start scraping...")
    scraped_data = scrape_table(url=URL, table_name=TABLE)
    logger.info("Scrape finished.")
    if scraped_data:
        insert_regular_market(scraped_data)
    else:
        logger.warning(f"No data scraped from {TABLE} at {URL}.")

if __name__ == "__main__":
    main()