import os
from pathlib import Path

import requests
from robocorp import browser
from robocorp.tasks import task
from RPA.Excel.Files import Files as Excel

FILE_NAME = "challenge.xlsx"
EXCEL_URL = f"https://rpachallenge.com/assets/downloadFiles/{FILE_NAME}"
OUTPUT_DIR = Path(os.getenv("ROBOT_ARTIFACTS", "output"))

import re
from playwright.sync_api import Page, expect

@task
def my_task():
    # Step 1: Navigate to Google
    page=browser.goto("https://www.google.com")
    
    # Step 2: Agree cookies
    page.click('button:has-text("Alle ablehnen")')


    # Step 3: Search for "cute cat picture"gLFyf
    page.fill('textarea[name="q"]',"cute cat picture")  # Fill the search box
    page.press('textarea[name="q"]', "Enter")

    # page.wait_for_timeout(1000000)  # Wait for 1000 seconds before closing the browser

    # # Step 4: Wait for the page to load and ensure images are present
    page.wait_for_selector('div.dURPMd', timeout=10000)
    div = page.query_selector('div.dURPMd') 

    # # # Step 5.1: Take a screenshot of the first image
    image = div.query_selector('img')  # Query all images
    image.screenshot(path="output/cute_cat_image.png")  # Take a screenshot of the first image


    # # # Step 5.2: Take a screenshot of the third image
    images = div.query_selector_all('img')  # Query all images
    if len(images) >= 3:
        third_image = images[2]  # Select the third image (index 2)
        third_image.screenshot(path="output/cute_cat_image3.png")  # Take a screenshot of the third image
    else:
        print("Fewer than 3 images found. Cannot take a screenshot of the third image.")
    

    # Log task completion
    print("Screenshot saved as 'output/cute_cat_image.png'.")

@task
def solve_challenge():
    """
    Main task which solves the RPA challenge!

    Downloads the source data Excel file and uses Playwright to fill the entries inside
    rpachallenge.com.
    """
    browser.configure(
        browser_engine="chromium", 
        screenshot="only-on-failure", 
        headless=True 
    )
    try:
        # Reads a table from an Excel file hosted online.
        excel_file = download_file(
            EXCEL_URL, target_dir=OUTPUT_DIR, target_filename=FILE_NAME
        )
        excel = Excel()
        excel.open_workbook(excel_file)
        rows = excel.read_worksheet_as_table("Sheet1", header=True)

        # Surf the automation challenge website and fill in information from the table
        #  extracted above.
        page = browser.goto("https://rpachallenge.com/")
        page.click("button:text('Start')")
        for row in rows:
            fill_and_submit_form(row, page=page)
        element = page.locator("css=div.congratulations")
        browser.screenshot(element)
    finally:
        # A place for teardown and cleanups. (Playwright handles browser closing)
        print("Automation finished!")


def download_file(url: str, *, target_dir: Path, target_filename: str) -> Path:
    """
    Downloads a file from the given URL into a custom folder & name.

    Args:
        url: The target URL from which we'll download the file.
        target_dir: The destination directory in which we'll place the file.
        target_filename: The local file name inside which the content gets saved.

    Returns:
        Path: A Path object pointing to the downloaded file.
    """
    # Obtain the content of the file hosted online.
    response = requests.get(url)
    response.raise_for_status()  # this will raise an exception if the request fails
    # Write the content of the request response to the target file.
    target_dir.mkdir(exist_ok=True)
    local_file = target_dir / target_filename
    local_file.write_bytes(response.content)
    return local_file


def fill_and_submit_form(row: dict, *, page: browser.Page):
    """
    Fills a single form with the information of a single row from the table.

    Args:
        row: One row from the generated table out of the input Excel file.
        page: The page object over which the browser interactions are done.
    """
    field_data_map = {
        "labelFirstName": "First Name",
        "labelLastName": "Last Name",
        "labelCompanyName": "Company Name",
        "labelRole": "Role in Company",
        "labelAddress": "Address",
        "labelEmail": "Email",
        "labelPhone": "Phone Number",
    }
    for field, key in field_data_map.items():
        page.fill(f"//input[@ng-reflect-name='{field}']", str(row[key]))
    page.click("input:text('Submit')")
