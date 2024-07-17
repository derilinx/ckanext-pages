import datetime
import uuid
import json

from six import text_type
import sqlalchemy as sa
from sqlalchemy.orm import class_mapper

try:
    from sqlalchemy.engine import Row
except ImportError:
    try:
        from sqlalchemy.engine.result import RowProxy as Row
    except ImportError:
        from sqlalchemy.engine.base import RowProxy as Row

from ckan import model
from ckan.model.domain_object import DomainObject

from ckanext.pages.utils import parse_json_or_return_original

pages_table = None


def make_uuid():
    return text_type(uuid.uuid4())


def init_db():
    if pages_table is None:
        define_tables()

    if not pages_table.exists():
        pages_table.create()


class Page(DomainObject):

    @classmethod
    def get(cls, **kw):
        '''Finds a single entity in the register.'''
        query = model.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()

    @classmethod
    def pages(cls, **kw):
        '''Finds all the pages filtering by a data dict'''
        order = kw.pop('order', False)
        order_publish_date = kw.pop('order_publish_date', False)

        query = model.Session.query(cls).autoflush(False)
        query = query.filter_by(**kw)
        query = query.order_by(cls.featured.desc())
        if order:
            query = query.order_by(sa.cast(cls.order, sa.Integer)).filter(cls.order != '')
        elif order_publish_date:
            query = query.order_by(cls.publish_date.desc()).filter(cls.publish_date != None)  # noqa: E711
        else:
            query = query.order_by(cls.created.desc())
        return query.all()

    def set_title(self, title, lang='default'):
        '''Sets the title for the specified language.'''
        if not self.title:
            self.title = {}
        self.title[lang] = title

    def get_title(self, lang='default'):
        '''Gets the title for the specified language.'''
        return self.title.get(lang, self.title.get('default', ''))

    def set_content(self, content, lang='default'):
        '''Sets the content for the specified language.'''
        if not self.content:
            self.content = {}
        self.content[lang] = content

    def get_content(self, lang='default'):
        '''Gets the content for the specified language.'''
        return self.content.get(lang, self.content.get('default', ''))


def define_tables():
    sql_upgrade_03 = ("ALTER TABLE ckanext_pages add column featured boolean DEFAULT 'f';",
                      "CREATE UNIQUE INDEX ckanext_pages_id_idx on ckanext_pages(id);",
                      "CREATE UNIQUE INDEX ckanext_pages_name_idx on ckanext_pages(name);")

    conn = model.Session.connection()
    try:
        for statement in sql_upgrade_03:
            conn.execute(statement)
    except sa.exc.ProgrammingError:
        pass
    model.Session.commit()

    types = sa.types
    global pages_table
    pages_table = sa.Table('ckanext_pages', model.meta.metadata,
                           sa.Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
                           sa.Column('title', types.JSON, default=lambda: {}),
                           sa.Column('name', types.UnicodeText, default=u''),
                           sa.Column('content', types.JSON, default=lambda: {}),
                           sa.Column('lang', types.UnicodeText, default=u''),
                           sa.Column('order', types.UnicodeText, default=u''),
                           sa.Column('private', types.Boolean, default=True),
                           sa.Column('group_id', types.UnicodeText, default=None),
                           sa.Column('user_id', types.UnicodeText, default=u''),
                           sa.Column('publish_date', types.DateTime),
                           sa.Column('page_type', types.UnicodeText),
                           sa.Column('created', types.DateTime, default=datetime.datetime.utcnow),
                           sa.Column('modified', types.DateTime, default=datetime.datetime.utcnow),
                           sa.Column('extras', types.UnicodeText, default=u'{}'),
                           sa.Column('featured', types.Boolean, default=False),
                           extend_existing=True
                           )

    model.meta.mapper(
        Page,
        pages_table,
    )


def table_dictize(obj, context, **kw):
    '''Get any model object and represent it as a dict'''
    result_dict = {}

    if isinstance(obj, Row):
        fields = obj.keys()
    else:
        ModelClass = obj.__class__
        table = class_mapper(ModelClass).mapped_table
        fields = [field.name for field in table.c]

    for field in fields:
        name = field
        if name in ('current', 'expired_timestamp', 'expired_id'):
            continue
        if name == 'continuity_id':
            continue
        value = getattr(obj, name)
        if name == 'extras' and value:
            result_dict.update(json.loads(value))
        elif value is None:
            result_dict[name] = value
        elif isinstance(value, dict):
            result_dict[name] = value
        elif isinstance(value, int):
            result_dict[name] = value
        elif isinstance(value, datetime.datetime):
            result_dict[name] = value.isoformat()
        elif isinstance(value, list):
            result_dict[name] = value
        elif name in ('title', 'content'):
            result_dict[name] = parse_json_or_return_original(value) if value else {}
        else:
            result_dict[name] = text_type(value)

    result_dict.update(kw)

    # HACK For optimisation to get metadata_modified created faster.

    context['metadata_modified'] = max(result_dict.get('revision_timestamp', ''),
                                       context.get('metadata_modified', ''))

    return result_dict
