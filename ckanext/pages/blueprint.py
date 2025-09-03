from flask import Blueprint, Response, stream_with_context, jsonify

import ckanext.pages.utils as utils
import logging
import ckan.plugins.toolkit as tk
from ckan import model

log = logging.getLogger(__name__)

pages = Blueprint('pages', __name__)


def index():
    return utils.pages_list_pages('page')

def show(page):
    return utils.pages_show(page, page_type='page')


def pages_edit(page=None, data=None, errors=None, error_summary=None):
    return utils.pages_edit(page, data, errors, error_summary, 'page')


def pages_delete(page):
    return utils.pages_delete(page, page_type='pages')


def upload():
    return utils.pages_upload()


def blog_index():
    return utils.pages_list_pages('blog')


def blog_show(page):
    return utils.pages_show(page, page_type='blog')


def blog_edit(page=None, data=None, errors=None, error_summary=None):
    return utils.pages_edit(page, data, errors, error_summary, 'blog')


def blog_delete(page):
    return utils.pages_delete(page, page_type='blog')


def org_show(id, page=None):
    return utils.group_show(id, 'organization', page)


def org_delete(id, page):
    return utils.group_delete(id, 'organization', page)


def org_edit(id, page=None, data=None, errors=None, error_summary=None):
    return utils.group_edit(id, 'organization', page, data, errors, error_summary)


def group_show(id, page=None):
    return utils.group_show(id, 'group', page)


def group_delete(id, page):
    return utils.group_delete(id, 'group', page)


def group_edit(id, page=None, data=None, errors=None, error_summary=None):
    return utils.group_edit(id, 'group', page, data, errors, error_summary)



def sitesearch():
    request = tk.request
    config = tk.config
    get_action = tk.get_action
    errors = {}
    data = {}

    if request.method == "POST":
        return tk.render('site_search/site_search.html', extra_vars={
            'data': {},
            'errors': {},
        })

    else:
        if request.args.get('q', None):
            data['q'] = request.args.get('q', None).replace(',', ' ')
            log.info("Found query: {}".format(data['q']))

            # Get sorting option from query string
            sort = request.args.get('sort', 'relevance')

            # Define allowed sorting options (safe whitelist!)
            sort_options = {
                'relevance': "title @@ '{q}' DESC",
                'title_asc': "title ASC",
                'title_desc': "title DESC",
                'date_newest': "publish_date DESC",
                'date_oldest': "publish_date ASC"
            }

            order_clause = sort_options.get(sort, sort_options['relevance'])

            query = f"""
                SELECT id, name, title, page_type, publish_date, private, content
                FROM ckanext_pages
                WHERE private = 'False'
                AND (content @@ '{{q}}' OR title @@ '{{q}}')
                ORDER BY {order_clause};
            """

            try:
                q = model.Session.execute(query.format(q=data['q'])).fetchall()
                results = [list(row) for row in q]
                return tk.render('site_search/site_search.html', extra_vars={
                    'data': q,
                    'errors': {},
                    'q': data['q'],
                    'sort': sort,
                })
            except Exception as e:
                log.info(e)
                return tk.render('site_search/site_search.html', extra_vars={
                    'data': {e},
                    'errors': {e},
                })
        return tk.render('site_search/site_search.html', extra_vars={
            'data': {},
            'errors': {},
        })


pages.add_url_rule("/site_search/", view_func=sitesearch, methods=["GET", "POST"])
pages.add_url_rule("/pages", view_func=index, endpoint="pages_index")
pages.add_url_rule("/pages/<page>", view_func=show)
pages.add_url_rule("/pages_edit", view_func=pages_edit, endpoint='new', methods=['GET', 'POST'])
pages.add_url_rule("/pages_edit/", view_func=pages_edit, endpoint='new', methods=['GET', 'POST'])
pages.add_url_rule("/pages_edit/<page>", view_func=pages_edit, endpoint='edit', methods=['GET', 'POST'])
pages.add_url_rule("/pages_delete/<page>", view_func=pages_delete, endpoint='delete', methods=['GET', 'POST'])

pages.add_url_rule("/pages_upload", view_func=upload, methods=['POST'])


pages.add_url_rule("/blog", view_func=blog_index)
pages.add_url_rule("/blog/<page>", view_func=blog_show)
pages.add_url_rule("/blog_edit", view_func=blog_edit, endpoint='blog_new', methods=['GET', 'POST'])
pages.add_url_rule("/blog_edit/", view_func=blog_edit, endpoint='blog_new', methods=['GET', 'POST'])
pages.add_url_rule("/blog_edit/<page>", view_func=blog_edit, endpoint='blog_edit', methods=['GET', 'POST'])
pages.add_url_rule("/blog_delete/<page>", view_func=blog_delete, endpoint='blog_delete', methods=['GET', 'POST'])


pages.add_url_rule("/organization/pages/<id>", view_func=org_show, endpoint='organization_pages_index')
pages.add_url_rule("/organization/pages/<id>/<page>", view_func=org_show, endpoint='organization_pages_show')
pages.add_url_rule("/organization/pages_edit/<id>", view_func=org_edit,
                   endpoint='organization_pages_new', methods=['GET', 'POST'])
pages.add_url_rule("/organization/pages_edit/<id>/", view_func=org_edit,
                   endpoint='organization_pages_new', methods=['GET', 'POST'])
pages.add_url_rule("/organization/pages_edit/<id>/<page>", view_func=org_edit,
                   endpoint='organization_pages_edit', methods=['GET', 'POST'])
pages.add_url_rule("/organization/pages_delete/<id>/<page>", view_func=org_delete,
                   endpoint='organization_pages_delete', methods=['GET', 'POST'])

pages.add_url_rule("/group/pages/<id>", view_func=group_show, endpoint='group_pages_index')
pages.add_url_rule("/group/pages/<id>/<page>", view_func=group_show, endpoint='group_pages_show')
pages.add_url_rule("/group/pages_edit/<id>", view_func=group_edit, endpoint='group_pages_new', methods=['GET', 'POST'])
pages.add_url_rule("/group/pages_edit/<id>/", view_func=group_edit, endpoint='group_pages_new', methods=['GET', 'POST'])
pages.add_url_rule("/group/pages_edit/<id>/<page>", view_func=group_edit,
                   endpoint='group_pages_edit', methods=['GET', 'POST'])
pages.add_url_rule("/group/pages_delete/<id>/<page>", view_func=group_delete,
                   endpoint='group_pages_delete', methods=['GET', 'POST'])