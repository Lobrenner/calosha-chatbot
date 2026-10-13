#.\.venv\Scripts\Activate.ps1

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

def get_group_links(group_set):
    '''Get links to groups in subchapter 7 of Title 8, California Code of Regulations'''
    lead = 'https://www.dir.ca.gov/Title8/'
    r = requests.get('https://www.dir.ca.gov/title8/sub7.html')
    time.sleep(1)
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
    time.sleep(1)
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
    time.sleep(1)
    soup3 = BeautifulSoup(r3.text, 'html.parser')
    for link in soup3.find_all('li'):
        for a in link.find_all('a'):
            url = lead + a.get('href')
            reg_set.add(url)
    return reg_set

def scrape_regulation(reg_url):
    '''scrape the content of the regulation from the website and save it as a JSON file'''
    r4 = requests.get(reg_url)
    time.sleep(1)
    soup = BeautifulSoup(r4.text, 'html.parser')
    section = soup.find('h1').string.strip()
    section = re.sub(r'\D', '', section)
    title = soup.title.string
    title = title.replace("\n", "").replace("\r", "").strip()
    first_div = soup.find('div', class_='chapter-article')
    chapter_text = first_div.get_text(strip=True, separator='\n')
    subchapter, group, article = chapter_text.split('\n', 2)
    regulation_content = soup.find_all('hr')[-1]
    content = '' 
    for item in regulation_content.next_siblings:
        content = content + item.get_text()
    content = content.strip()

    data = {
        "section": section,
        "title": title,
        "subchapter": subchapter,
        "group": group,
        "article": article,
        "content": content
    }

    name = 'data/regulations/' + section + '.json'
    if os.path.exists(name):
        return
    with open(name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# leading url for everything https://www.dir.ca.gov/Title8/
"""
First, get links to all groups, for each group get links to all articles, for each article search regulation retrieve 
"""



def main():

    processed_reg = set()
    group_set = set()
    get_group_links(group_set)
    for group in group_set:
        article_set = set()
        get_article_links(article_set, group)
        for article in article_set:
            reg_set = set()
            get_regulation_links(reg_set, article)
            for reg in reg_set:
                if reg in processed_reg:
                    print("Reg already processed")
                    continue
                print(reg)
                processed_reg.add(reg)
                try:
                    scrape_regulation(reg)
                except:
                    print("Link could not be parsed correctly")
    print("All done :)")


# christian was here
if __name__ == "__main__":
    main()