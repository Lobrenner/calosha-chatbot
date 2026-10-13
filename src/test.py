
import requests
from bs4 import BeautifulSoup, Tag
import json
import time
import re
import os
from pathlib import Path
from urllib.parse import urlparse


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
    """Scrape a regulation or appendix and save it as JSON."""

    r4 = requests.get(reg_url, timeout=30)
    r4.raise_for_status()
    time.sleep(1)

    soup = BeautifulSoup(r4.text, 'html.parser')

    appendix_heading = soup.find('h5')
    is_appendix = (
        appendix_heading is not None
        and appendix_heading.get_text(strip=True).lower().startswith('appendix')
    )

    if is_appendix:
        # Appendix metadata
        appendix = appendix_heading.get_text(strip=True)

        hierarchy = soup.find('h1').get_text(separator='\n', strip=True)
        subchapter, group, article = hierarchy.split('\n', 2)

        # Use source URL as a unique filename
        filename = Path(urlparse(reg_url).path).stem + '.json'

        section = None
        title = appendix

    else:
        # Regular regulation metadata
        section = soup.find('h1').get_text(strip=True)
        section = re.sub(r'\D', '', section)

        title = soup.title.get_text(strip=True)
        first_div = soup.find('div', class_='chapter-article')
        chapter_text = first_div.get_text(strip=True, separator='\n')
        subchapter, group, article = chapter_text.split('\n', 2)

        filename = section + '.json'

    # Extract content
    regulation_content = soup.find_all('hr')[-1]
    paragraphs = []

    for item in regulation_content.next_siblings:
        if not isinstance(item, Tag):
            continue

        text = item.get_text(separator=' ', strip=True)

        # Stop at amendment history
        if text.upper() == 'HISTORY':
            break

        # Stop at back-navigation link
        link = item.find('a')
        if link and 'go back' in link.get_text(' ', strip=True).lower():
            break

        if text:
            if item.name == 'pre':
                text = item.get_text().strip()
            paragraphs.append(text)

    content = '\n\n'.join(paragraphs)

    data = {
        "document_type": "appendix" if is_appendix else "regulation",
        "section": section,
        "title": title,
        "subchapter": subchapter,
        "group": group,
        "article": article,
        "content": content,
        "source_url": reg_url
    }

    if is_appendix:
        data["appendix"] = appendix

    path = Path('data/test') / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        return

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    scrape_regulation("https://www.dir.ca.gov/Title8/3302.html")
    processed_reg = set()
    reg_set = set()
    get_regulation_links(reg_set, "https://www.dir.ca.gov/Title8/sb7g2a7.html")
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
    
    
if __name__ == "__main__":
    main()