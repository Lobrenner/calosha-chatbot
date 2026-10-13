
import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os


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
    regulation_content = soup.find_all('hr')[-1] #soup.find('div', class_='co_contentBlock co_section')
    content = '' #regulation_content.get_text(strip=True, separator='\n')
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

    name = 'data/test/' + section + '.json'
    if os.path.exists(name):
        return
    with open(name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    scrape_regulation("https://www.dir.ca.gov/Title8/sb7g15a105apa.html")
    
if __name__ == "__main__":
    main()