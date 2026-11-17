from bs4 import BeautifulSoup

from ckan.plugins import toolkit as tk


def _soup(content):
    # Pages can have empty or NULL content
    return BeautifulSoup(content or '', 'html.parser')


def get_placeholder_img():
    '''URL of the image to show for pages without one, or None'''
    return tk.config.get('ckanext.pages.placeholder_img') or None


def get_post_image(content):
    '''URL of the first image in the content, or the placeholder image'''
    img = _soup(content).find('img')
    if img and img.get('src'):
        return img['src']
    return get_placeholder_img()


def get_first_p(content):
    return _soup(content).find('p') or ''


def get_soup_text(content):
    blacklist = [
        'style',
        'script'
    ]

    return [t.strip() for t in _soup(content).find_all(string=True)
            if t.parent.name not in blacklist and len(t) > 5]


def get_content(content):
    '''The content without its first image'''
    soup = _soup(content)
    img = soup.find('img')
    if img:
        img.decompose()
    return soup
