
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import json
import time
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse


DATA_FOLDER = Path("data/regulations")
ARTICLE_URL = "https://www.dir.ca.gov/Title8/sb7g2a7.html"


def get_soup(url):
    """Request a webpage and parse its HTML."""
    time.sleep(1)

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    # Parse the original bytes so BeautifulSoup can detect
    # the encoding, including encodings specified in HTML.
    return BeautifulSoup(response.content, "html.parser")


def get_regulation_links(reg_set, article_url):
    """Get regulation links from an article index."""
    soup = get_soup(article_url)

    for li in soup.find_all("li"):
        for a in li.find_all("a", href=True):
            href = a["href"]
            url = urljoin(article_url, href)

            # Ignore navigation and non-HTML links.
            if "go back" in a.get_text(" ", strip=True).lower():
                continue

            if url == article_url:
                continue

            if not urlparse(url).path.lower().endswith(".html"):
                continue

            if not urlparse(url).path.lower().startswith("/title8/"):
                continue

            reg_set.add(url)

    return reg_set



def extract_content(soup):
    """Extract regulation text while preserving basic formatting."""

    separators = soup.find_all("hr")

    if not separators:
        raise ValueError("No content separator found")

    start = separators[-1]

    paragraphs = []
    current = []

    def finish_paragraph():
        if current:
            text = " ".join(current).strip()
            if text:
                paragraphs.append(text)
            current.clear()

    for item in start.next_elements:

        if isinstance(item, Tag):

            # Stop at the actual navigation link,
            # not its potentially oversized parent.
            if item.name == "a":
                link_text = item.get_text(" ", strip=True).lower()
                if "go back" in link_text:
                    break

            # Preserve paragraph boundaries.
            if item.name in ("p", "br", "tr", "pre"):
                finish_paragraph()

            # Handle modern DIR paragraph containers.
            classes = item.get("class", [])
            if "co_paragraph" in classes:
                finish_paragraph()

            # Separate table cells.
            if item.name in ("td", "th"):
                if current:
                    current.append("|")

        elif isinstance(item, NavigableString):

            text = " ".join(str(item).split())

            if not text:
                continue

            # Stop at amendment history.
            if text.upper() == "HISTORY":
                finish_paragraph()
                break

            current.append(text)

    finish_paragraph()

    return "\n\n".join(paragraphs).strip()

def scrape_regulation(reg_url):
    """Scrape one regulation or appendix into a JSON file."""

    # URL-based filenames support regulations and appendices.
    filename = Path(urlparse(reg_url).path).stem + ".json"
    path = DATA_FOLDER / filename

    if path.exists():
        return "skipped"

    soup = get_soup(reg_url)

    # Look for appendix headings regardless of heading tag.
    appendix_heading = None

    for heading in soup.find_all(["h1", "h5"]):
        heading_text = heading.get_text(" ", strip=True)

        if re.match(r"^Appendix\s+[A-Z]\b", heading_text, re.I):
            appendix_heading = heading
            break

    is_appendix = appendix_heading is not None

    title = soup.title.get_text(" ", strip=True)

    # Extract hierarchy.
    hierarchy = soup.find("div", class_="chapter-article")

    if hierarchy:
        lines = hierarchy.get_text("\n", strip=True).splitlines()
    else:
        # Fallback for older appendix layouts.
        heading = soup.find("h1")
        lines = heading.get_text("\n", strip=True).splitlines()

    lines = [line.strip() for line in lines if line.strip()]

    if len(lines) < 3:
        raise ValueError("Could not extract regulatory hierarchy")

    subchapter, group, article = lines[:3]

    if is_appendix:
        section = None
        appendix = appendix_heading.get_text(" ", strip=True)
    else:
        heading = soup.find("h1")

        if heading is None:
            raise ValueError("Regulation heading not found")

        heading_text = heading.get_text(" ", strip=True)
        match = re.search(
            r"§\s*(\d+(?:\.\d+)?[A-Za-z]?)",
            heading_text
        )

        # Standard regulation URLs also provide the section.
        if match:
            section = match.group(1)
        elif re.fullmatch(r"\d+(?:\.\d+)?[A-Za-z]?", path.stem):
            section = path.stem
        else:
            raise ValueError("Could not identify section number")

    content = extract_content(soup)

    # Don't silently save an empty regulation.
    if not content:
        raise ValueError("No regulatory content extracted")

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

    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return "saved"


def main():
    reg_set = set()
    processed_reg = set()

    saved = 0
    skipped = 0
    failed = []

    get_regulation_links(reg_set, ARTICLE_URL)

    for reg in sorted(reg_set):
        if reg in processed_reg:
            continue

        try:
            result = scrape_regulation(reg)

            if result == "saved":
                saved += 1
                print(f"Saved: {reg}")
            else:
                skipped += 1
                print(f"Skipped existing: {reg}")

            processed_reg.add(reg)

        except Exception as error:
            print(f"FAILED: {reg}")
            print(f"{type(error).__name__}: {error}")
            failed.append(reg)

    print("\nAll done :)")
    print(f"Saved: {saved}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed URLs:")
        for url in failed:
            print(url)


if __name__ == "__main__":
    main()
