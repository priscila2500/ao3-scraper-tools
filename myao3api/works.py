# -*- encoding: utf-8
# -*- encoding: utf-8

from datetime import datetime
import json
from bs4 import BeautifulSoup, Tag
import requests


class WorkNotFound(Exception):
    pass

class RestrictedWork(Exception):
    pass


class Work(object):

    def __init__(self, id, sess=None):
        self.id = id
        self._soup = None

        if sess is None:
            sess = requests.Session()

        req = sess.get(f'https://archiveofourown.org/works/{self.id}')

        if req.status_code == 404:
            raise WorkNotFound(f'Unable to find a work with id {self.id}')
        elif req.status_code != 200:
            raise RuntimeError(f'Unexpected error from AO3 API: {req.text} ({req.status_code})')

        if 'This work could have adult content' in req.text:
            req = sess.get(f'https://archiveofourown.org/works/{self.id}?view_adult=true')

        if 'This work is only available to registered users' in req.text:
            raise RestrictedWork(f'Looking at work ID {self.id} requires login')

        self._html = req.text
        if not self._html:
            raise RuntimeError(f"Empty response for work ID {self.id}")

        self._soup = BeautifulSoup(self._html, 'html.parser')
        if self._soup is None:
            raise RuntimeError(f"Failed to parse HTML for work ID {self.id}")

    def __repr__(self):
        return f'{type(self).__name__}(id={self.id!r})'

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self))

    @property
    def url(self):
        return f'https://archiveofourown.org/works/{self.id}'

    @property
    def title(self):
        title_tag = self._soup.find('h2', attrs={'class': 'title'})
        return title_tag.contents[0].strip() if title_tag else ''

    @property
    def author(self):
        byline_tag = self._soup.find('h3', attrs={'class': 'byline'})
        if not byline_tag:
            return ''
        a_tag = [t for t in byline_tag.contents if isinstance(t, Tag)]
        return a_tag[0].contents[0].strip() if a_tag else ''

    @property
    def summary(self):
        summary_div = self._soup.find('div', attrs={'class': 'summary'})
        if summary_div:
            blockquote = summary_div.find('blockquote')
            return blockquote.renderContents().decode('utf8').strip() if blockquote else ''
        return ''

    def _lookup_stat(self, class_name, default=None):
        dd_tag = self._soup.find('dd', attrs={'class': class_name})
        if dd_tag is None:
            return default
        return dd_tag.contents[0] if dd_tag.contents else default

    @property
    def rating(self):
        return self._lookup_stat('rating', [])

    @property
    def fandoms(self):
        return self._lookup_stat('fandom', [])

    def json(self, *args, **kwargs):
        data = {
            'workid': self.id,
            'title': self.title,
            'author': self.author,
            'summary': self.summary,
            'rating': self.rating,
            'fandoms': self.fandoms,
            'url': self.url
        }
        return json.dumps(data, *args, **kwargs)

