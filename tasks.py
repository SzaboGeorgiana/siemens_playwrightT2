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
