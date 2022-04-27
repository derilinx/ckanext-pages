from bs4 import BeautifulSoup
from unicodedata import normalize

PLACEHOLDER_IMG = '/img/dgilogows.png'


def get_post_image(content):
    soup = BeautifulSoup(content)
    if soup:
        if soup.find_all('img'):
            img_link = soup.find_all('img')[0].get('src')
            return img_link
        else:
            return PLACEHOLDER_IMG
    else:
        return PLACEHOLDER_IMG


def get_first_p(content):
    soup = BeautifulSoup(content, 'html.parser')
    if soup:
        print soup
        if soup.find_all('p'):
            return soup.find_all('p')[1]
        else:
            return ''


def get_soup_text(content):
    soup = BeautifulSoup(content, 'html.parser')
    blacklist = [
        'style',
        'script'
    ]

    text_elements = [t.strip() for t in soup.find_all(text=True) if t.parent.name not in blacklist and len(t) > 5]
    return text_elements


def get_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    if soup:
        if soup.find_all('img'):
            output = soup
            soup.find_all('img')[0].decompose()
            return output
        else:
            return soup
