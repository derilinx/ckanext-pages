from bs4 import BeautifulSoup
from unicodedata import normalize
from ckan.plugins import toolkit as tk
import ckan.plugins.toolkit as toolkit
import ckan.plugins as p
from ckanext.pages.utils import  parse_json_or_return_original 

PLACEHOLDER_IMG = tk.config.get('ckanext.pages.placeholder_img', None)


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
        if soup.find_all('p'):
            return soup.find_all('p')[0]
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


def get_lang_to_json():
    locales = tk.h.get_available_locales()
    languages_arr = [{'short_name': f"{locale.language}_{locale.territory}" if locale.territory else locale.language, 'display_name': f"{locale.get_display_name()}"} for locale in locales]
    return languages_arr

def get_lang_from_dict_fallback(dict):
    dict = parse_json_or_return_original(dict)
    return dict.get(tk.h.lang()) or next((dict.get(lang["short_name"]) for lang in get_lang_to_json() if lang["short_name"] in dict), None)

def superset_dashboards():
    if 'superset' in tk.aslist(tk.config.get('ckan.plugins')):
        return [
            { 'title': dashboard['title'], 'url': dashboard['url'] + '?standalone=2' }
            for dashboard in tk.h.superset_dashboard_list()['public']
        ]
    return []

def clean_img_tags(content):
    if not content:
        return ''

    soup = BeautifulSoup(content, 'html.parser')
    for img in soup.find_all('img'):
        if 'style' in img.attrs:
            del img.attrs['style']

        classes = img.get('class', [])
        if 'img-fluid' not in classes:
            classes.append('img-fluid')
        img['class'] = classes

    return str(soup)

