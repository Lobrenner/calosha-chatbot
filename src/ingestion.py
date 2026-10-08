#.\.venv\Scripts\Activate.ps1

import requests
from bs4 import BeautifulSoup
import json
import time

def get_group_links(group_set):
    '''Get links to groups in subchapter 7 of Title 8, California Code of Regulations'''
    lead = 'https://www.dir.ca.gov/Title8/'
    r = requests.get('https://www.dir.ca.gov/title8/sub7.html')
    soup = BeautifulSoup(r.text, 'html.parser')
    for link in soup.find_all('strong'):
        for a in link.find_all('a'):
            url = lead + a.get('href')
            group_set.add(url)
    return group_set

def get_article_links(article_set, group_url):
    '''Get links to Articles'''
    lead = 'https://www.dir.ca.gov/Title8/'
    r2 = requests.get(group_url)
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    for link in soup2.find_all('strong'):
        for a in link.find_all('a'):
            url = lead + a.get('href')
            article_set.add(url)
    return article_set

def get_regulation_links(reg_set, article_url):
    '''Get links to regulations'''
    lead = 'https://www.dir.ca.gov/Title8/'
    r3 = requests.get(article_url)
    soup3 = BeautifulSoup(r3.text, 'html.parser')
    for link in soup3.find_all('li'):
        for a in link.find_all('a'):
            url = lead + a.get('href')
            reg_set.add(url)
    return reg_set

def scrape_regulation(reg_url):
    '''scrape the content of the regulation from the website and save it as a JSON file'''
    r = requests.get(reg_url)
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


# leading url for everything https://www.dir.ca.gov/Title8/
"""
First, get links to all groups, for each group get links to all articles, for each article search regulation retrieve 
"""
def main():
    group_set = set()
    get_group_links(group_set)
    for group in group_set:
        article_set = set()
        get_article_links(article_set, group)
        print(group)
        for article in article_set:
            reg_set = set()
            get_regulation_links(reg_set, article)
            print(article)
            for reg in reg_set:
                print(reg)









if __name__ == "__main__":
    main()