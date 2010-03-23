import os.path
import xml.dom.minidom as dom
from genshi.template import MarkupTemplate, TemplateLoader

from ajenti.ui.classes import Html

EMPTY_TEMPLATE="""<html xmlns="http://www.w3.org/1999/xhtml" 
        xmlns:py="http://genshi.edgewall.org/" 
        xmlns:xi="http://www.w3.org/2001/XInclude" py:strip="" />
"""

class BasicTemplate(object):
    def __init__(self, filename=None, search_path=[], includes=[]):
        """ Initializes UI templates from file, or from default one

        @filename - if not empty, will load template from file
        @search_path - list of locations where templates and includes resides
        @includes - list of files to include via XInclude

        >>> from ajenti.ui.template import BasicTemplate
        >>> b = BasicTemplate(includes=['widgets.xml'])
        >>> b.toxml()
        u'<?xml version="1.0" ?> \
        <html py:strip="" xmlns="http://www.w3.org/1999/xhtml" \
        xmlns:py="http://genshi.edgewall.org/" \
        xmlns:xi="http://www.w3.org/2001/XInclude">\
        <xi:include href="widgets.xml"/></html>'
        """
        self.search_path = search_path

        if filename is not None:
            for p in search_path:
                if os.path.isfile(os.path.join(p, filename)):
                    filename = os.path.join(p, filename)
            self._dom = dom.parse(filename)
        else:
            self._dom = dom.parseString(EMPTY_TEMPLATE)


        e = self._dom.childNodes[0]
        h = Html()
        for i in includes:
            e.insertBefore(h.gen('xi:include', href=i), e.firstChild)

    def appendChildInto(self, dest, child):
        """ Tries to append child element to given tag
        FIXME: Change to use ids instead tags

        @dest - destination tag to append to
        @child - child DOM element
        """
        elements = self._dom.getElementsByTagName(dest)
        if len(elements) == 0:
            raise RuntimeError("Tag <%s> not found"%dest)

        elements[0].appendChild(child)

    def appendChild(self, child):
        """ Appends child to most outer element """
        e = self._dom.childNodes[0]
        e.appendChild(child)

    def toxml(self):
        return self._dom.toxml()

    def toprettyxml(self):
        return self._dom.toprettyxml()
    
    def render(self, *args, **kwargs):
        loader = TemplateLoader(self.search_path)
        template = MarkupTemplate(self.toxml(), loader=loader)
        return template.generate(**kwargs).render('html', doctype='html')
