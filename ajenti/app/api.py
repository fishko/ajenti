from ajenti.com import Interface

class IRequestDispatcher(Interface):
    def match(self, uri):
        pass

    def process(self, req, start_response):
        pass


class IContentProvider(Interface):
    path = ''
    module = ''
    js_files = []
    css_files = []
    widget_files = []

    def content_path(self):
        pass

    def widget_path(self):
        pass

    def template_path(self):
        pass


class ICategoryProvider(Interface):
    """ ICategoryProvider should contain:
    'get_ui()' method to retrieve main panel
    """

    def get_ui():
        pass


class IEventDispatcher(Interface):
    def match_event(self, event):
        pass

    def event(self, event, *params, **kwparams):
        pass
        

