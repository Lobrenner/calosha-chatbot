#.\.venv\Scripts\Activate.ps1

import requests
from bs4 import BeautifulSoup
import json


def get_group_links():
    '''Get links to groups in subchapter 7 of Title 8, California Code of Regulations'''
    
    r = requests.get('https://www.dir.ca.gov/title8/sub7.html')
    soup = BeautifulSoup(r.text, 'html.parser')
    for link in soup.find_all('strong'):
        for a in link.find_all('a'):
            print(a.get('href'))

def get_article_links():
    '''Get links to Articles'''

    r2 = requests.get('https://www.dir.ca.gov/title8/sb7g2.html')
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    for link in soup2.find_all('strong'):
        for a in link.find_all('a'):
            print(a.get('href'))

def get_regulation_links():
    '''Get links to regulations'''

    r3 = requests.get('https://www.dir.ca.gov/Title8/sb7g2a8.html')
    soup3 = BeautifulSoup(r3.text, 'html.parser')
    for link in soup3.find_all('li'):
        for a in link.find_all('a'):
            print(a.get('href'))

def scrape_regulation():
    '''scrape the content of the regulation from the website and save it as a JSON file'''

    r = requests.get ('https://www.dir.ca.gov/title8/3314.html')
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.title.string
    title = title.replace("\n", "").replace("\r", "").strip()
    first_div = soup.find('div', class_='chapter-article')
    chapter_text = first_div.get_text(strip=True, separator='\n')
    subchapter, group, article = chapter_text.split('\n', 2)
    regulation_content = soup.find('div', class_='co_contentBlock co_section')
    content = regulation_content.get_text(strip=True, separator='\n')

    data = {
        "section": "3314",
        "title": title,
        "subchapter": subchapter,
        "group": group,
        "article": article,
        "content": content
    }

    with open('data/regulations/3314.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)