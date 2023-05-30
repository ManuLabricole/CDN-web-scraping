# First we import the libraries
import requests
import bs4
import pandas as pd
import requests
import subprocess
import os


def print_sep():
    print("")
    print("--------------------------------------------------------------------------------------------")
    print("--------------------------------------------------------------------------------------------")
    print("")


def check_status(res):
    print("-------------------------------------------------------------------------------------------")
    print("")
    print("Request.....")
    if res.status_code == 200:
        print(f"Request was successful with status code {res.status_code}")
        return True
    elif res.status_code == 404:
        print(f"Page not found with status code {res.status_code}")
    elif res.status_code == 403:
        print(f"Access denied with status code {res.status_code}")
    elif res.status_code == 500:
        print(f"Internal server error with status code {res.status_code}")
    else:
        print("Status code: ", res.status_code)

    print("")
    print("-------------------------------------------------------------------------------------------")

    return False


def get_soup(isValid, page):
    if isValid:
        soup = bs4.BeautifulSoup(page.content, 'html.parser')

    return soup


def download_csv_link(href, name):
    print_sep()
    # Check if the link ends with ".csv"
    if href.endswith(".csv"):
        # Download the CSV file
        response = requests.get(href, stream=True)

        # Extract the file name from the href link
        file_name = os.path.basename(name)

        # Get the total file size in bytes
        total_size = int(response.headers.get('Content-Length', 0))
        bytes_downloaded = 0

        # Save the file to your directory
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    file.write(chunk)
                    bytes_downloaded += len(chunk)

                    # Calculate the percentage of the operation
                    percentage = (bytes_downloaded / total_size) * 100

                    # Clear the previous line and print the loader
                    print('\r[{}{}] {:.2f}%'.format('#' * int(percentage / 10),
                          ' ' * (10 - int(percentage / 10)), percentage), end='')

        print('\nDownload complete!')
        print_sep()


# Then we define the url we want to scrap
url = "https://data.metropolegrenoble.fr/ckan/dataset/points-d-apports-volontaire/resource/9be5666b-f050-4584-b87e-e937e5be080a"

# Send a GET request to the URL
response = requests.get(url)

# Then we get the html code of the page using the method text
soup = get_soup(check_status(response), response)

csv_element = soup.find_all("p", class_="muted ellipsis")
# Now we ant to target the href attribute of the a tag
href = csv_element[0].find("a")["href"]

name = "PAV.csv"
download_csv_link(href, name)

if name in os.listdir():
    print("File downloaded successfully!")
    subprocess.run(['open', '-a', 'Numbers', name])

print_sep()
# Get the size of the downloaded file in megabytes
file_size_gb = os.path.getsize(name) / (1024 * 1024 * 1024)
print('Downloaded file size: {:.4f} GB'.format(file_size_gb))
print_sep()
