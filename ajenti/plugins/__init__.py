import re

from ajenti.plugins.core import *
from ajenti.plugins.advancedcontrols import *
from ajenti.plugins.dashboard import *
from ajenti.plugins.config import *

from ajenti.com import *
from ajenti.app.urlhandler import URLHandler, url

class DemoDispatcher(URLHandler, Plugin):

    @url('^/demo')
    def process(self, req, sr):
        from pprint import pformat
        sr('200 OK', [('Content-type','text/plain')])
        return pformat(req)
