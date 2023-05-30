# We will follow the tutorial from https://realpython.com/beautiful-soup-web-scraper-python/
# The goal is to scrape the webstite https://realpython.github.io/fake-jobs/
# We will get the title, location, and date of the job offers

# We use the library BeautifulSoup to parse the html code of the website
# We will also use the library requests to get the html code of the website

# First we import the libraries
import requests
import bs4
import pandas as pd

import requests
URL = "https://realpython.github.io/fake-jobs/"
page = requests.get(URL)


def print_sep():
    print("")
    print("--------------------------------------------------------------------------------------------")
    print("--------------------------------------------------------------------------------------------")
    print("")
# print(page.text)

# We can see that the html code is very long and not very readable
# Fortunately the website has clear classname


# class="title is-5" contains the title of the job posting.
# class="subtitle is-6 company" contains the name of the company that offers the position.
# class="location" contains the location where you’d be working.

# We will use the library BeautifulSoup to parse the html code of the website
# Using the method prettify() we can see the html code in a more readable way
soup = bs4.BeautifulSoup(page.content, 'html.parser')
# print(soup.prettify())

# We will now target a specific ID of the html code to get the job offers only
# id="ResultsContainer"

results_id = soup.find(id="ResultsContainer")
# print(results_id.prettify())

# Now we want to target the specific class of the html code to get the job offers only
# As every job offer is in a div with the class="card-content" we will use this class


def get_elements_by_class(results, class_name):
    el = results.find_all(class_=class_name)
    return el


def print_elements(elements):

    for i, job_element in enumerate(elements):
        # print_sep()
        # print("JOB ELEMENTS")
        # print(job_element, end="\n"*2)
        print_sep()
        print(f"JOB NUMBER {i}")
        print("-----------------")
        print("JOB TITLE")
        # print(job_element.find(class_="title is-5").text.strip())
        # Or we can use the method get_text()
        print("-->", job_element.find("h2", class_="title is-5").get_text())
        print("JOB LOCATION")
        print("-->", job_element.find("p", class_="location").text.strip())
        print("COMPANY NAME")
        print("-->", job_element.find("h3",
              class_="subtitle is-6 company").text.strip())

    return None


def get_specific_jobs(elements, kw, toPrint):
    # using the method find_all() we can get all the elements that contain the keyword
    # Unfortunately the method find_all() is case sensitive
    # It will not find the keyword if it is not written exactly the same way
    specific_jobs = elements.find_all("h2", string=kw)

    # Instead we can use the method find_all() with the argument string and a lambda function to make it case insensitive
    specific_jobs = elements.find_all(
        "h2", string=lambda text: kw in text.lower())

    if toPrint == True:
        for job in specific_jobs:
            print_sep()
            print(f"job containing --> {kw} <-- {job}")

    return specific_jobs


job_elements = get_elements_by_class(results_id, "card-content")

print_sep()
print(f"WE HAVE --> {len(job_elements)} <-- job offers")
print_sep()

print_elements(job_elements)

python_jobs = get_specific_jobs(results_id, "python", toPrint=False)

python_job_elements = [
    h2_element.parent.parent.parent for h2_element in python_jobs
]

print("")
print("----------------------------------------------------------")
print("---------------------- PYTHON JOBS ---------------------- ")
print("----------------------------------------------------------")
print("")
for i, job_element in enumerate(python_job_elements):
    print_sep()
    print(f"PYTHON JOB NUMBER --> {i}")
    title_element = job_element.find("h2", class_="title")
    company_element = job_element.find("h3", class_="company")
    location_element = job_element.find("p", class_="location")

    # To acces the date is a bit more complicated as it is not in a specific class
    # to do so we will use the method find_all() with the argument string and a lambda function
    date = job_element.find("time")
    link = job_element.find_all("a", class_="card-footer-item")[1]["href"]
    print("TITLE ------> ", title_element.text.strip())
    print("COMPANY ----> ", company_element.text.strip())
    print("LOCATION ---> ", location_element.text.strip())
    print("DATE -------> ", date.text.strip())
    print("LINK -------> ", link)
