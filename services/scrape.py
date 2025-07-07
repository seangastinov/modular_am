import json
import logging
from bs4 import BeautifulSoup
from utils.logging import setup_logging
from playwright.sync_api import sync_playwright
from utils.client import HTTPX_SYNC_CLIENT

setup_logging()
logger = logging.getLogger(__name__)

# Map table names to their corresponding AJAX endpoints
TABLE_ENDPOINTS = {
    "ndsomEntityTable": "ndsom",
    "oddLotEntityTable": "oddLot",
    "whenIssuedEntityTable": "whenNewIssued",
    "whenReIssuedEntityTable": "whenReIssued"
}
TABLE_TAB_MAPPING = {
    "ndsomEntityTable": {"tab_href": "#tabs1", "js_function": "updateTable()"},
    "oddLotEntityTable": {"tab_href": "#tabs2", "js_function": "oddLotUpdateTable()"},
    "whenReIssuedEntityTable": {"tab_href": "#tabs3", "js_function": "whenReIssuedUpdateTable()"},
    "whenIssuedEntityTable": {"tab_href": "#tabs4", "js_function": "whenIssuedUpdateTable()"}
}


def extract_table_data(content: str, table_name: str) -> list[dict]:
    """
    Extract data from the current page of a table.
    
    Args:
        page: Playwright page object
        table_name (str): The name of the table to extract data from
    
    Returns:
        list[dict]: List of dictionaries containing row data
    """
    soup = BeautifulSoup(content, 'html.parser')

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

def scrape_table_with_browser(url: str, table_name: str, max_wait_time: int = 30) -> list[dict]:
    """
    Scrape table data by waiting for dynamic content to load.
    
    Args:
        url (str): The URL to scrape
        table_name (str): The name of the table to scrape
        max_wait_time (int): Maximum time to wait for content to load
    
    Returns:
        list[dict]: A list of dictionaries containing the scraped data
    """
    if table_name not in TABLE_ENDPOINTS:
        raise ValueError(f"Table name '{table_name}' is not in the list of valid tables: {TABLE_ENDPOINTS.keys()}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state('networkidle')

        tab_info = TABLE_TAB_MAPPING[table_name]
        logger.info(f"Clicking tab for table '{table_name}': {tab_info['tab_href']}")
        
        # Find and click the tab
        tab_selector = f"a[href='{tab_info['tab_href']}']"
        tab_element = page.wait_for_selector(tab_selector)
        
        if tab_element:
            tab_element.click()
            logger.info(f"Clicked tab: {tab_info['tab_href']}")

            try:
                page.wait_for_selector(f"#{table_name} tbody tr", timeout=1000)
                logger.info(f"Table '{table_name}' loaded successfully")
            except Exception as e:
                logger.warning(f"Table rows not found immediately, continuing anyway: {e}")

        else:
            logger.error(f"Could not find tab with selector: {tab_selector}")
            browser.close()
            return []
        
        all_data = []
        page_number = 1
        
        while True:
            logger.info(f"Scraping page {page_number}")
            
            # Get current page data
            page_data = extract_table_data(page.content(), table_name)
            all_data.extend(page_data)
            
            # Check if there's a next page
            next_button = page.query_selector(f"#{table_name}_next")
            if next_button and not next_button.get_attribute('class') or 'disabled' not in next_button.get_attribute('class'):
                next_button.click()
                page.wait_for_timeout(1000)  # Wait for page to load 1 seconds
                page_number += 1
            else:
                break
        
        browser.close()
        return all_data
 

def scrape_table_direct(url: str, table_name: str) -> list[dict]:
    """
    Scrape table data directly from AJAX endpoints.
    
    Args:
        url (str): The base URL
        table_name (str): The name of the table to scrape
    
    Returns:
        list[dict]: A list of dictionaries containing the scraped data
    """
    if table_name not in TABLE_ENDPOINTS:
        raise ValueError(f"Table name '{table_name}' is not in the list of valid tables: {TABLE_ENDPOINTS.keys()}")
    
    resource_id = TABLE_ENDPOINTS[table_name]
    
    # Construct the AJAX URL based on the JavaScript code
    ajax_url = f"{url}?p_p_id=com_ccil_ndsom_entire_CCILNdsOM_EntirePortlet_INSTANCE_zavb&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id={resource_id}&p_p_cacheability=cacheLevelPage"
    
    with HTTPX_SYNC_CLIENT as client:
        response = client.post(ajax_url, data={})
        if response.status_code != 200:
            logger.error(f"Failed to retrieve data from {url}, status code: {response.status_code}")
            raise ValueError(f"Failed to retrieve data from {url}, status code: {response.status_code}")
        
        data = response.json()
        try:
            table_data = json.loads(data['result1'])
            return table_data
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {e} type: {type(e)}")    
            return []
        
def scrape_table(url: str, table_name: str, method: str = 'direct') -> list[dict]:
    if method == 'direct':
        return scrape_table_direct(url, table_name)
    elif method == 'headless_browser':
        return scrape_table_with_browser(url, table_name)
    else:
        raise ValueError("Method must be 'ajax' or 'headless_browser'")