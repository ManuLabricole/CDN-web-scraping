
# First we import the libraries


# The objective is to scrap the url : https://www.insee.fr/fr/statistiques/5229313#graphique-figure1
# The tricky part is that we want to find contained in a second url in this page

# First we import the libraries
import requests
import bs4
import pandas as pd
import requests
import subprocess

# Then we define the url we want to scrap
url = "https://www.insee.fr/fr/statistiques/5229313#graphique-figure1"
base_url = url.split("#")[0]

page = requests.get(url)

# Send a GET request to the URL
response = requests.get(url)


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


def get_element_by_class(results, class_name):
    el = results.find_all(class_=class_name)
    return el


def displayOnglets(onglets):
    if len(onglets) == 0:
        print("No onglets found")
        return

    for i, onglet in enumerate(onglets):
        print_sep()
        print(f"ONGLET NUMBER {i}")
        print("-----------------")
        print(onglet, end="\n"*2)


def get_href(onglets):
    hrefs = []
    for onglet in onglets:
        href = onglet.find("a").get("href")
        hrefs.append(href)

    try:
        tableau_url = [url for url in hrefs if 'tableau' in url]
        if len(tableau_url) == 0:
            raise Exception("No tableau url found")
        elif len(tableau_url) > 1:
            raise Exception("Too many tableau url found")
        else:
            print_sep()
            print("Tableau url found")
            print(tableau_url[0])
            print_sep()
            return tableau_url[0]

    except Exception as e:
        print_sep()
        print(e)
        print_sep()

        return hrefs


def get_new_url(base_url, href):
    if type(href) == list:
        return [base_url + url for url in href]
    else:
        return base_url + href


def get_df(tableau):
    try:
        df = pd.read_html(str(tableau))[0]
        print(pd.read_html(str(tableau)))
        print_sep()
        print("Dataframe created")
        print(df)
        print_sep()
        return df
    except Exception as e:
        print_sep()
        print(e)
        print_sep()
        return None


def save(df, name, open):
    df.to_csv(name, index=False)
    print_sep()
    print("Dataframe saved")
    print_sep()

    if open == True:
        subprocess.run(['open', '-a', 'Numbers', name])


# PART 0 - CHECK THE STATUS OF THE REQUEST
soup = get_soup(check_status(response), page)

# PART I - FIND THE TABLEAU URL
onglets = get_element_by_class(soup, "onglet")
# displayOnglets(onglets)
href = get_href(onglets)

# PART II - SCRAP THE TABLEAU URL
# Now that we find the URL where the tableau is, we can scrap it
newUrl = get_new_url(base_url, href)
page = requests.get(newUrl)
isVlid = check_status(page)
soup = get_soup(isVlid, page)

# PART III - GET THE TABLEAU FROM THE URL AND PUT IT IN A DATAFRAME
tableau = soup.find(id="produit-tableau-figure1")
df = get_df(tableau)
save(df, "tableau.csv", True)

# END OF THE SCRIPT
