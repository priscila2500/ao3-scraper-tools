# -*- encoding: utf-8

from datetime import datetime
import requests
from .works import Work
from bs4 import BeautifulSoup

class User(object):
    def __init__(self, username, password, sess=None):
        self.username = username
        if sess is None:
            sess = requests.Session()
        self.sess = sess

    def __repr__(self):
        return '%s(username=%r)' % (type(self).__name__, self.username)

