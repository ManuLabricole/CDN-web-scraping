# First we import the libraries
import requests
import bs4
import pandas as pd
import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def print_sep():
    print("")
    print("--------------------------------------------------------------------------------------------")
    print("--------------------------------------------------------------------------------------------")
    print("")

# The goal of selenium is to automate the browser
# Here we have to handle the pagination
# we will use the selenium library to do so


# Then we need to install the webdriver
# The webdriver is a tool that allows us to automate the browser
# We will use the Chrome webdriver


options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
driver.get('https://pagination.js.org/')
# driver.maximize_window()

# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


# STEP I - CLICK ON THE NEXT BUTTON
# We want to click on the next button which contains ">" in the html code
def click_next():
    next_btn = driver.find_element(By.XPATH, "//a[text()='›']")
    next_btn.click()


# WORK ON THE FIRST TABLE - GET THE NUMBER OF PAGES
all_list_elements = driver.find_elements(
    By.XPATH, '//*[@id="demo1"]/div[2]/div/ul/li')

print_sep()
print(
    f"There are --> {len(all_list_elements)} <-- elements in [@id='demo1']/div[2]/div/ul/li"
)

# Then we want to find the number of pages, so in the html code we will target the second last element of the list
# (last is next button, second to last is the last page)
number_of_pages = int(all_list_elements[-2].text)
print_sep()
print(f"There are --> {number_of_pages} <-- pages")

# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

# No we want to catch all the elements in the ul list for each page
# The pagination is a ul, and each li give access to another ul where we want to catch the data


def print_all_elements(num):

    # Locate all elements on the current page of the pagination element
    page_elements = driver.find_elements(
        By.XPATH, '//*[@id="demo1"]/div[1]/ul/li')
    print_sep()
    print(f"Page {num+1}")
    for li in page_elements:
        text_content = li.get_attribute('innerHTML')

        # Print the text content to the console
        print("")
        print("--------------------------------------------")
        print(text_content)
        print("--------------------------------------------")


def loop_through_pages():

    for i in range(number_of_pages):
        click_next()
        time.sleep(0.25)
        print_sep()
        print("NEXT PAGE")
        print_all_elements(i)

    print("")
    print(" -------------------------------- END OF LOOP -------------------------------- ")


# RUN THE LOOP THROUGH PAGES FUNCTION AND PRINT THE CONTENT OF THE FIRST ELEMENT
loop_through_pages()


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

# Now we want to catch the data in the table

data = []