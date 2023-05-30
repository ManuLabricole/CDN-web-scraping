""" custom package for webscrapping of departemental websites in France to retrieve wind projects in process of environmental authorization demand
to get list of wind projects in the process of an autorization request """

#------------------REMINDER--------------------------------------------------------------#
# think of importlib.reload(mymodule)
# %load_ext autoreload and %autoreload 2
# %reload_ext autoreload

from ast import keyword
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import numpy as np
import openpyxl
import time
from datetime import datetime
import sys
import os
import random
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

#------------get_html_text----------------------------------------------------------------#
def get_soup(url):
    """ this formule gets the html text based on a webpage url"""

    # general parameters
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'
    #Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0
    #Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0 --> found on dep's urls
    
    headers={'User-Agent':user_agent, 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}

    # loop
    try: 
        req = Request(url, headers=headers)
        html_page = urlopen(req, timeout = 180)
        soup = bs(html_page, 'lxml') #lxml, 'html.parser'

    except:
        soup = None

    return soup


#-----------get list of all hrefs in soup-----------------------------------------------------#
def get_href(html_text, dep_url, key_words):
    """ get all the url links that have eolien in it from soup"""
    
    all_url = []
    #key_words = ['eolien', 'Eolien', 'EOLIEN']

    
    for l in html_text.find_all("a"):#, href=re.compile('|'.join(key_words)))
        #time.sleep(2)
        value = l.get('href') #.lower() #make hrefs lower case
            

        suffix = '/'
        if value != None:
            if value.startswith(suffix) is True:
                url = 'https://www.'+dep_url+'.gouv.fr/'+value[1:]+''
            else:
                url = 'https://www.'+dep_url+'.gouv.fr/'+value+''
                 
        all_url.append(url)

    #make df and rename col 0 as proj_url
    all_url = pd.DataFrame(all_url)
    all_url = all_url.rename(columns={0 : 'proj_url'})

    # only select url's related to wind parcs
    select_url = all_url[all_url['proj_url'].str.contains('|'.join(key_words), case=False)]

    #exclude layout and social media name in href's
    exclude = ['layout', 'facebook', 'twitter', 'abonnement', 'referentiel', '.pdf', 'prevention']
    proj_url = select_url[~select_url['proj_url'].str.contains("|".join(exclude), case=False)]

    return proj_url

#-------------------------------------get href class---------------------------------------------#
def get_href_class(html_text, dep_url):
    """ get all the url links that have eolien in it from soup"""
    
    all_url = []
    
    for l in html_text('li', {'class':'fond'}):
        for tag in l('a'):
            value = tag.get('href')

            suffix = '/'
            if value.startswith(suffix) is True:
                url = 'https://www.'+dep_url+'.gouv.fr/'+value[1:]+''
            else:
                url = 'https://www.'+dep_url+'.gouv.fr/'+value+''
             
            all_url.append(url)

    #make df and rename col 0 as proj_url
    all_url = pd.DataFrame(all_url)
    all_url = all_url.rename(columns={0 : 'proj_url'})

    #exclude layout and social media
    #exclude = ['layout', 'facebook', 'twitter']
    #all_url = all_url[~all_url['proj_url'].str.contains("|".join(exclude))]

    return all_url

#------------------------------------GET-TABLE---------------------------------------------------#
def get_table(soup, url, dep_url, headings, proj_url=False):
    # headings is a list of strings

    # from soup find all table rows
    rows = soup.find_all('tr')
    #print(rows[1])
    #headings = []
        
    #for td in rows[0].find_all('td'):
     #   # remove any newlines and extra spaces from left and right
      #  headings.append(td.text.replace('\n', ' ').strip())
       # print(headings)

    #get all info in table
    table_data = []
    n = len(rows)
    for i in range(n):
        row = rows[i]

        r_data = [] # data for all cell's in row i
        r_data_dict = {} # r_data in dictionnary with keys from headings
        for td in row.find_all('td'):
            #try first to get pdf url for each td in row

            try:
                value = td.find('a').get('href')
                pdfs = []
                for a in td.findAll('a'):
                    value = a.get('href')
                    pdf_url = 'http://www.'+dep_url+'.gouv.fr/'+value+''
                    pdfs.append(pdf_url)
                r_data.append(pdfs)

            #if no pdf_url's, get the text in cell
            except:
                r_data.append(td.text.replace('\n', ' ').strip())
                
        r_data_dict = dict(zip(headings, r_data))
        table_data.append(r_data_dict)
    df = pd.DataFrame(table_data)

    if proj_url is False:
        df['proj_url'] = url
    else:
        pass
    df = df.iloc[1:,:]

    return df

# ---------------------------------DEF GET TABLE2 ------------------------------------------------------------
def get_table2(soup, url, dep_url, headings, url_cols): #code from Webscrapping library can't be used REPLACE
    '''Different from get_table since headings can be pre defined by user. 
    And what col numbers (index starting from 0) contain url can be pre-defined'''
    
    # from soup find all table rows
    rows = soup.find_all('tr')
    
    #get all info in table
    table_data = []
    n = len(rows)
    for i in range(1, n):
        row = rows[i]
        #print(row)

        r_data = [] # data for all cell's in row i
        r_data_dict = {} # r_data in dictionnary with keys from headings
        
        tds = row.find_all('td')
        print('row number', i)
        
        if len(tds) == len(headings):
        #some rows tr contain less td's than number of headings --> without if statement code error
            assert len(tds) == len(headings)
            for j in range(len(headings)):
                if j not in url_cols:
                    #print(j)

                    td = tds[j]
                    r_data.append(td.text.replace('\n', ' ').strip())

                else:
                    td = tds[j]

                    if len(td.find_all('a')) == 1:
                        for a in td.find_all('a'):
                            value = a.get('href')
                            td_url = 'http://www.'+dep_url+'.gouv.fr/'+value+''
                        r_data.append(td_url)
                    else:
                        urls = []
                        for a in td.find_all('a'):
                            value = a.get('href')
                            td_url = 'http://www.'+dep_url+'.gouv.fr/'+value+''
                            urls.append(td_url)
                        r_data.append(urls)
                
        r_data_dict = dict(zip(headings, r_data))
        table_data.append(r_data_dict)
    df = pd.DataFrame(table_data)

    return df

#----------------------------------------GET PROJ FROM SOUS RUBRIQUE--------------------------------------------
def get_from_sousrub(url, dep_url, dep_nr, columns):
    # columns = number of page columns with projects
    i = columns + 1

    soup = get_soup(url)
    
    data = []
    headings = ['proj_url', 'proj']
    
    #define equation for get item data with div as input 
    def get_item_data(div):
        
        item_data = []
        for a in div.find_all('a'):
            value = a.get('href')
            proj_url = 'https://www.'+dep_url+'.gouv.fr/'+value+''
            item_data.append(proj_url)

            for p in a.find_all('p'):
                proj = p.text
                item_data.append(proj)

        item_data_dict = dict(zip(headings, item_data))
        data.append(item_data_dict)

        return data


    if i == 1:
        for div in soup.find_all('div', {'class':'sous_rub'}):
            data = get_item_data(div)

    else :
        for n in range(1, i):
            for div in soup.find_all('div' , {'class':'sous_rub_'+str(n)+''}):
                data = get_item_data(div)

    df = pd.DataFrame(data)
    df['dep_nr'] = dep_nr

    return df

#---------------------------CREATE DATAFRAME WITH COLS --------------------------------------------------------#
def create_df(proj_url, dep_nr, cols): 
    ''' Create the dataframe with proj_url, dep_nr and cols. Suffix should be expressed as string
    cols to be retreived from the standard columns list in folder generic'''

    #extract proj name
    df = proj_url
    proj_name = df.apply(lambda x: x['proj_url'].rsplit('/', 1)[1], axis=1)

    #check if url ends with digits and .html if True only return name without html and digits
    try:
        df['proj'] = proj_name.apply(lambda x: re.search(r'(.*?)-a\d', str(x)).group(1))

    except:
        df['proj'] = proj_name
    
    ##add department number and required cols to df
    df['dep_nr'] = dep_nr
    df['dep_nr'] = df['dep_nr'].astype(int)
    df = pd.concat([df, pd.DataFrame(columns=cols)])

    #exclude proj names with photovolt in it
    exclude = ['photovolt']
    df = df[~df['proj'].str.contains("|".join(exclude))]

    return df

#--------------------------- ----DF TO CSV --------------------------------------------------------#

def make_csv(df, dep_nr, dep, suffix=None):
    ''' make the csv file based on df'''

    if suffix is None:
        file_saved = df.to_csv(''+dep_nr+'_'+dep+'_list_wind_proj.csv', index=False)
    else:
        file_saved = df.to_csv(''+dep_nr+'_'+dep+'_list_wind_proj_'+str(suffix)+'.csv', index=False)
        
    return file_saved

#---------------------------GET LASTUPDATE---------------------------------------------------------#
def get_date_lastupdate(url):
    '''Get date of site update besed on cols:
    - date_ouv_EP > 1/1/2020
    - proj_url'''

    # define randSleep for delay, prevent 403 Forbidden error
    #randSleep = random.randint(500, 2500)/100

    #driver = webdriver.Firefox()

    #date_ouv_EP_ = pd.to_datetime(date_ouv_EP, errors = 'coerce')
    #if date_ouv_EP > '2020-01-01':

    #driver.get(url)

    try:
        soup = get_soup(url) #bs(driver.page_source, 'lxml')
        for maj in soup.find_all('small', {'class' : 'mis_a_jour'})[0]: 
            date_ = re.search(r'(\d{2}[/]\d{2}[/]\d{4})', str(maj))[0]
            date = pd.to_datetime(date_, dayfirst=True)

        #time.sleep(randSleep)

    except:
        date = np.nan
    
    return date

#----------------------------------GET PROJ NAME AND PDF LINK FROM PAGE-----------------------------------
def get_proj_pdf_link(url, dep_url, dep_nr, cols, keywords, class_type='encadrement'):

    soup = get_soup(url)

    headings = ['proj_url', 'proj', 'pdf_url']

    data = [] #empty df for all data on page
    for div1 in soup.find_all('div', {'class': class_type}):

        for div2 in div1.find_all('div', {'class':''}):

            r_data = [] #empty list for all data in row
            for a in div2.find_all('a'):

                #append proj_url
                r_data.append(url)

                #get proj description
                descr = a.get('title')
                r_data.append(descr)
                
                #get pdf url of AP
                value = a.get('href')
                pdf_url = 'https://www.'+dep_url+'.gouv.fr/'+value+''
                r_data.append(pdf_url)
            
            r_data_dict = dict(zip(headings, r_data))
            data.append(r_data_dict)
        df_all_ap = pd.DataFrame(data) #all projects
        df_ap = df_all_ap[df_all_ap['proj'].str.contains('|'.join(keywords), case=False, na=False)]

    df_ap_ = pd.DataFrame({'proj_url': [], 'proj': [], 'dep_nr' : []})
    df_ap_['proj_url'] = df_ap['proj_url']
    df_ap_['proj'] = df_ap['proj']
    df_ap_['dep_nr'] = dep_nr

    # MAKE DF WITH STANDARD COLS 
    df_ap_ = pd.concat([df_ap_, pd.DataFrame(columns=cols)])
    df_ap_['lien_complementaire'] = df_ap['pdf_url']
    print('number of eol ap:',len(df_ap_['proj'].unique()))

    return df_ap_

#------------------------------------GET PROJ_URL WITH PAGINATION---------------------------------------
def proj_url_pagination(url, dep_url, dep_nr, cols, key_words=None):
    '''Code to get proj url's with pagination. Can be applied to a site
    with proj links on multiple pages and pagination with next. Links refer
    to a new url for each seperate project. Different AP's and pdf's listed
    on this project. 
    If site only lists wind projects, than key_words = None'''
    # DRIVER OBJECT 
    #loop to load page 10 trials
    for i in range(0,10):
        try:
            driver = webdriver.Firefox()
            driver.get(url)
            soup = bs(driver.page_source, 'lxml')
            break
        except:
            print('loading page failed')

    # GET BY URL
    driver.get(url)

    #paginate through next pages with randSleep
    randSleep = random.randint(500, 2500)/100

    data = []
    headings = ['proj_url', 'proj']
    while True:
        # grab the data
        soup = bs(driver.page_source, 'lxml')

        for lu in soup.find_all('ul'):
            for li in lu.find_all('li', {'class':'fond'}):

                r_data = []
                for a in li.find_all('a'):

                    #append proj_url)
                    value = a.get('href')
                    proj_url = 'https://www.'+dep_url+'.gouv.fr'+value+''
                    r_data.append(proj_url)

                    #get proj description is title
                    proj = a.text
                    r_data.append(proj)

                r_data_dict = dict(zip(headings, r_data))
                data.append(r_data_dict)

        # click next link
        try:
            element = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='pagination']/span[@class='next']")))
            element.click()
            time.sleep(randSleep)
        except TimeoutException:
            print('no more pages left')
            break

    df = pd.DataFrame(data)
    #df = df.drop_duplicates() # drop duplicates, each project is grabbed multiple time!!???
    print('length df all proj:', len(df))

    if key_words is None:
        df_select = df
        print('length df:', len(df))
    else:
        df_select = df[df['proj'].str.contains('|'.join(key_words), case=False, na=False)].copy()
        print('length df:', len(df_select))
        #print(df_ap_eol['proj'])

    # Make DF and CSV
    df_select['dep_nr'] = dep_nr #= pd.DataFrame({'proj_url':[], 'proj':[], 'dep_nr':[]})
    df = pd.concat([df_select, pd.DataFrame(columns=cols)])

    return df

# -------------------------------------GET PROJ URL WITH PAGINATION 2--------------------------------
def proj_url_pagination2(url, dep_url, dep_nr, cols, key_words=None):
    '''Code to get proj url's with pagination. Can be applied to a site
    with proj links on multiple pages and pagination with next. Difference with other 
    proj_url_pagination. For the pagination to stop, 
    first look for the number of pages. While loop makes sure that selenium element click stops when last
    page has been reached. If while trial < nr_pages not included selenium keeps clicking since element remains
    visible in the DOM. 
    If site only lists wind projects, than key_words = None'''

       
    # DRIVER OBJECT 
    #loop to load page 10 trials
    for i in range(0,10):
        try:
            driver = webdriver.Firefox()
            driver.get(url)
            soup = bs(driver.page_source, 'lxml')
            break
        except:
            print('loading page failed')

    # check if there are multiple pages, then get number of pages for pagination
    ul_all = soup.find_all('ul', {'class':'fr-pagination__list'})
    print('length ul_all:', len(ul_all))
    if len(ul_all) > 0:
        for ul in soup.find_all('ul', {'class':'fr-pagination__list'}):
            li_ls = ul.find_all('li')
            n = pd.to_numeric(li_ls[-3].get_text()) # third last child of li_list
    else:
        n = 1
    print('n value:', n)
    
    # GET BY URL
    driver.get(url)
    
    #print(driver.current_url)

    #paginate through next pages with randSleep
    randSleep = random.randint(500, 2500)/100

    data = []
    headings = ['proj_url', 'proj']

    # initiate j to count pagination

    j = 0
    while j < n:
        # grab the data
        soup = bs(driver.page_source, 'lxml')

        for div in soup.find_all('div', {'class':'fr-card__content'}):
            for h2 in div.find_all('h2', {'class':'fr-card__title'}):

                r_data = []
                for a in h2.find_all('a'):

                    #append proj_url)
                    value = a.get('href')
                    #print(value)
                    proj_url = 'https://www.'+dep_url+'.gouv.fr'+value+''
                    r_data.append(proj_url)

                    #get proj description is title
                    proj = a.text.strip().replace('\n', '')
                    #print(proj)
                    r_data.append(proj)

                r_data_dict = dict(zip(headings, r_data))
                data.append(r_data_dict)

        # click next link
        try:
            j = j + 1
            print(j, 'th page')
            css_selector = 'a.fr-pagination__link--next'          
            element = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
            element.click()
            time.sleep(randSleep)
        except TimeoutException:
            print('no more pages left')
            break

    df = pd.DataFrame(data)
    #df = df.drop_duplicates() # drop duplicates, each project is grabbed multiple time!!???
    print('length df all proj:', len(df))

    if df.empty is not True:
        if key_words is None:
            df_sol = df
            print('length df solar:', len(df))
        else:
            df_sol = df[df['proj'].str.contains('|'.join(key_words), case=False, na=False)].copy()
            print('length df solar:', len(df_sol))
            #print(df_ap_eol['proj'])

        # Make DF and CSV
        df_sol['dep_nr'] = dep_nr #= pd.DataFrame({'proj_url':[], 'proj':[], 'dep_nr':[]})
        df = pd.concat([df_sol, pd.DataFrame(columns=cols)])
    
    else:
        df = pd.DataFrame()

    return df

#------------------------------------------check updates--------------------------------------------
def check_updates(dep_nr, dep, comp_col, file_db=None,  url_root_update=None, db_update=False):
    '''Only for updates based on 1 column comparison.
    Check updates by comparing new proj list scraped from dep_url and proj 
    already present in BDD. Required inputs:
    df_bdd = current bdd loaded automatically
    df_dep_new = new proj from dep_url, loaded based on dep_nr and dep input
    dep_nr
    dep = dep for folder with _ seperation e.g. charente_maritime
    dep_url = dep for url with - seperation e.g. charente-maritime
    file_db = path after ROOT is after DATABASE.
    comp_col = column with unique key to use for comparison
    db_update = False as default, only check updates. If True than updates are
    integrated in bdd'
    url_root_update = dict, {url_root_old: url_root_new}'''

    # Settings
    now  = datetime.now()
    ROOT = "."
    sys.path.append(ROOT)
    ROOT_dep = ROOT+'/'+dep_nr+'_'+dep+''

    # Load bdd
    if file_db is None:
        file_db = '99_01_DB_raw/db_solar_raw.xlsx'
    else:
        file_db = file_db

    path_db_file = os.path.join(ROOT, file_db)
    df_db = pd.read_excel(path_db_file, engine='openpyxl')
    
    # url_root_update if any:
    if url_root_update == None:
        df_db = df_db
    else:
        df_db['proj_url'] = df_db['proj_url'].replace(url_root_update, regex=True)

    df_db['proj_url'] = df_db['proj_url'].str.lower()
    df_db['proj'] = df_db['proj'].str.lower()
    #only get df for appropriate dep_nr
    df_proj_db = df_db[df_db['dep_nr'] == int(str(dep_nr))]
    print('length projects in db:', len(df_proj_db))

    # Load last generated proj_list
    df_dep_new = pd.read_csv(ROOT_dep+'/'+dep_nr+'_'+dep+'_list_solar_proj.csv')
    print('length new from dep_url:', len(df_dep_new))
    # convert strings in proj and proj_url to lower
    try: 
        df_dep_new['proj'] = df_dep_new['proj'].str.lower()
    except:
        df_dep_new['proj'] = df_dep_new['proj']

    try: 
        df_dep_new['proj_url'] = df_dep_new['proj_url'].str.lower()
    except:
        df_dep_new['proj_url'] = df_dep_new['proj_url']
    try: 
        df_dep_new['projet_spv'] = df_dep_new['projet_spv'].str.lower()
    except:
        df_dep_new['projet_spv'] = df_dep_new['projet_spv']

    # Compare proj in bdd and new proj list
    inter = set(df_dep_new[comp_col]) & set(df_proj_db[comp_col])
    print('length of intersection:', len(inter))
    dif_list = set(df_dep_new[comp_col]) - set(inter) #make difference list
    print('length of projects to add:', len(dif_list))
    dif_list = pd.DataFrame({comp_col: list(dif_list)})

    # USE DIF LIST TO SELECT PROJ TO BE ADDED FROM DF_PROJ_NEW
    df_add = df_dep_new[df_dep_new[comp_col].isin(dif_list[comp_col])].copy()
    df_add[comp_col] = df_add[comp_col].str.lower()
    df_add['bdd_update'] = now
    print(df_add['proj'])
    df_db_update = df_db.append(df_add)

    print('length initial db_raw:', len(df_db))
    print('length db_raw updates:', len(df_db_update))

    # SORT DF BY DEP_NR, COMMUNE, PROJ
    df_db_update = df_db_update.sort_values(by=['dep_nr', 'proj', 'commune'], ascending = True)

    # UPDATES
    now_str = now.strftime("%Y%m%d-%H%M%S")

    # DB update
    if db_update == True:
        # 1 Write initial DB raw before update to backup
        folder_backup = '99_01_DB_raw/backup'
        path_backup = os.path.join(ROOT, folder_backup)
        df_db.to_excel(path_backup+'/db_wind_raw_'+str(now_str)+'.xlsx', engine='openpyxl', index=False)

        # 2 write df_db_update to excel
        df_db_update.to_excel(path_db_file, engine = 'openpyxl', index=False)

        # WRITE TXT FILE WITH DATE OF UPDATE AND FOR WHICH DEPARTMENT
        with open(ROOT+'/99_01_DB_raw/'+'/'+dep_nr+'_'+dep+'_update_'+str(now_str)+'.txt', 'w+') as f:
            f.write('length projects in db:'+str(len(df_proj_db))+'\n'
            'length new from dep_url:'+str(len(df_dep_new))+'\n'
            'length of intersection:'+str(len(inter))+'\n'
            'length of projects to add:'+str(len(dif_list))+'\n'
            'length initial db_raw:'+str(len(df_db))+'\n'
            'length db_raw_update:'+str(len(df_db_update))+'\n\n'
            'PROJ ADDED \n')
            for p in df_add['proj']:
                f.write(''+p+'\n')
            f.close()
    

