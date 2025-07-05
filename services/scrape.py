from utils.client import HTTPX_SYNC_CLIENT
import logging
from bs4 import BeautifulSoup
# import httpx
from utils.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


LIST_OF_TABLES = [
    "ndsomEntityTable",
    "oddLotEntityTable",
    "whenReIssuedEntityTable",
    "whenIssuedEntityTable"
]


def scrape_table(url: str, table_name: str) -> list[dict]:
    """
    Scrape a table from a given URL and return the data as a list of dictionaries.
    
    Args:
        url (str): The URL to scrape.
        table_name (str): The name of the table to scrape.
    
    Returns:
        list[dict]: A list of dictionaries containing the scraped data.
    """
    if table_name not in LIST_OF_TABLES:
        raise ValueError(f"Table name '{table_name}' is not in the list of valid tables: {LIST_OF_TABLES}")


    with HTTPX_SYNC_CLIENT as client:
        response = client.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve data from {url}, status code: {response.status_code}")
            raise ValueError(f"Failed to retrieve data from {url}, status code: {response.status_code}")
        
        response_content = response.text

    soup = BeautifulSoup(response_content, 'html.parser')
    table = soup.find('table', {'id': table_name})

    if table is None:
        logger.error(f"Table with id '{table_name}' not found in the HTML content.")
        raise ValueError(f"Table with id '{table_name}' not found in the HTML content.")
    
    headers = []
    th = table.find('th')

    if th is None:
        logger.error(f"No header found in the table with id '{table_name}'.")
        raise ValueError(f"No header found in the table with id '{table_name}'.")
    
    for header in table.find_all('th'):
        headers.append(header.text.strip())

    tbody = table.find('tbody')
    if tbody is None:
        logger.error(f"Table body (tbody) not found in the table with id '{table_name}'.")
        raise ValueError(f"Table body (tbody) not found in the table with id '{table_name}'.")


    rows = []
    for row in tbody.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) != len(headers):
            logger.warning(f"Row length {len(cells)} does not match header length {len(headers)}. Skipping row.")
            continue
        row_data = {headers[i]: cells[i].text.strip() for i in range(len(headers)) if headers[i]}
        rows.append(row_data)

    return rows