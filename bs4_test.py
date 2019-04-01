from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from bs4 import UnicodeDammit
import csv
import time
import random



OUTPUT_FILE = 'F:/OneDrive/Python/HackerRank/bs4_test_log.txt'
MAIN_URL = 'https://www.craigslist.org/about/sites'
JOB_SUFFIX = 'search/sof'
JOB_SUFFIX2 = 'search/egr'


class Job():
    def __init__(self):
        self.title = ''
        self.description = ''
        self.pid = ''
        self.url = ''
        self.town = ''


def GetSoup(url):
    try:
        html = urlopen(url)
    except HTTPError:
        print(f'GetSoup Error #1 [{url}]')
        return None
    try:
        soup = BeautifulSoup(html.read(), 'html.parser')
    except AttributeError:
        print(f'GetSoup Error #2 [{url}]')
        return None
    else:
        return soup


def GetTownLinks(soup):
    town_links_dict = {}
    i = 0
    for link in soup.find_all('a'):
        i = i + 1
        url_href = ''
        url_name = ''
        if i > 7:
            if link.get('href'):
                url_href = link.get('href')
            if link.get_text():
                url_name = link.get_text()
            if url_href and url_name:
                town_links_dict.update([(url_name, url_href)])
    return town_links_dict


def LoadTownLinks():
    town_links_dict = {}
    with open('output_towns.csv', 'r') as input:
        csvreader = csv.reader(input, dialect='excel')
        for row in csvreader:
            if row:
                town = row[0]
                url = row[1]
                town_links_dict.update([(town, url)])
    print(f'{len(town_links_dict)} cities link loaded.')
    return town_links_dict


def GetJobs(url):
    jobs_list = []
    increment = 0
    lastpage = True
    soup = GetSoup(url)
    while lastpage:
        for li in soup.find_all('li', 'result-row'):
            a = li.find_all('a', 'result-title hdrlnk')
            job = Job()
            job.url = a[0].get('href')
            if job.url.find('craigslist') < 0:
                town = url[0:url.rfind('.org')+4]
                job.url = town + job.url
                job.pid = a[0].get('data-id')
                job.title = a[0].get_text()
                jobs_list.append(job)
        fl = soup.find_all('div', 'paginator buttongroup firstpage lastpage')
        l = soup.find_all('div', 'paginator buttongroup lastpage')
        #random_pause = random.randint(0, 1)
        #print('Loading job links. Pause {random_pause} sec')
        #time.sleep(random_pause)
        if fl or l:
            lastpage = False
        else:
            increment = increment + 120
            soup = GetSoup(f'{url}?s={increment}')
    print(f'{len(jobs_list)} job links loaded.')
    return jobs_list


def FillDescription(jobs, town):
    for job in jobs:
        url = job.url
        soup = GetSoup(url)
        section = soup.find(id='postingbody')
        section_text = section.get_text()
        job.description = section_text
        job.town = town
        #random_pause = random.randint(0, 1)
        #print('Job descriptions loading. Pause {random_pause} sec')
        #time.sleep(random_pause)
    print(f'{len(jobs)} job descriptions loaded.')
    return jobs


def SaveJobs(jobs):
    with open('output.csv', 'a', errors='ignore') as output:
        csvwriter = csv.writer(output, dialect='excel')
        for job in jobs:
            pid = job.pid
            url = job.url
            town = job.town
            title = job.title
            description = job.description
            csvwriter.writerow('*************************************************************')
            csvwriter.writerow([url])
            csvwriter.writerow([title, description])
            csvwriter.writerow('-------------------------------------------------------------')


def SaveTowns(town_links_dict):
    with open('output_towns.csv', 'a') as output:
        csvwriter = csv.writer(output, dialect='excel')
        for town in town_links_dict:
            csvwriter.writerow([town, town_links_dict[town]])


if __name__ == '__main__':
    #soup = GetSoup(MAIN_URL)
    #town_links_dict = GetTownLinks(soup)
    #SaveTowns(town_links_dict)
    #town_links_dict = {}
    #town_links_dict.update([('charleston', 'https://charleston.craigslist.org/')])
    town_links_dict = LoadTownLinks()
    for town in town_links_dict:
        print(f'Parse jobs in {town} : {town_links_dict[town]}')
        jobs_list = GetJobs(str(town_links_dict[town])+JOB_SUFFIX)
        FillDescription(jobs_list, town)
        SaveJobs(jobs_list)
        print(f'Jobs from {town} saved to "output.csv"')
