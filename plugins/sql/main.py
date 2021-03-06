from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti import apis


class SQLPlugin(CategoryPlugin):
    text = 'SQL client'
    icon = '/dl/sql/icon.png'
    folder = 'tools'

    backends = None
    backend = None

    def on_init(self):
        self._logging_in = not self.config.has_option('sql', 'backend')
        self.backends = [b.name for b in self.app.grab_plugins(apis.sql.IDBBackend)]
        if self.config.has_option('sql', 'backend'):
            self.backend = self.app.grab_plugins(apis.sql.IDBBackend,
                            lambda x: x.name == self.config.get('sql', 'backend'))[0]

    def on_session_start(self):
        self._labeltext = ''
        self._logging_in = False
        self._login_dialog = False
        self._tab = 0
        self._sql = ''

    def get_ui(self):
        self.on_init()

        status = UI.VContainer(
                    UI.Label(text=('Disconnected' if self._logging_in else '%s@%s' % (self.config.get('sql', 'login'), self.config.get('sql', 'host')))),
                    UI.Button(text='Reconnect', id='btnLogout')
                 )

        panel = UI.PluginPanel(status, title='SQL Client', icon='/dl/sql/icon.png')


        if self._logging_in:
            panel.append(self.get_ui_login())
            return panel
        else:
            try:
                self.backend.connect(
                    self.config.get('sql', 'host'),
                    self.config.get('sql', 'login'),
                    self.config.get('sql', 'passwd'),
                    self.config.get('sql', 'db')
                )
            except Exception as e:
                panel.append(UI.VContainer(UI.ErrorBox(title='Error', text='Connection problem: ' + str(e))))
                return panel

            panel.append(self.get_default_ui())

        self.backend.disconnect()

        return panel

    def get_default_ui(self):
        t = UI.TabControl(active=self._tab)
        t.add('Tables', self.get_ui_tables())
        t.add('SQL', self.get_ui_sql())
        return t

    def get_ui_tables(self):
        tblTables = UI.DataTable(
                        UI.DataTableRow(
                            UI.Label(text='Name', width=200),
                            UI.Label(text=''),
                            header = True
                        )
                    )



        data = self.backend.sql('SHOW TABLES;')
        if str(data) == data: # 'if data is str', please write something more senseful here
            tblTables = UI.ErrorBox(title='SQL', text='Error: ' + data)
        else:
            for r in data:
                row = UI.DataTableRow(
                        UI.Label(text=r[0]),
                        UI.DataTableCell(
                            UI.MiniButton(text='View', id=('view/'+r[0])),
                            hidden=True
                        )
                      )
                tblTables.append(row)
        return tblTables

    def get_ui_sql(self):
        cnt = UI.DataTable()
        if len(self._sql)>0:
            if self._sql[-1] != ';': self._sql += ';'
            data = self.backend.sql(self._sql)
            if str(data) == data: # 'if data is str', please write something more senseful here
                cnt = UI.ErrorBox(title='SQL', text='Invalid query: ' + data)
            else:
                for row in data:
                    r = UI.DataTableRow()
                    for f in row:
                        r.append(UI.DataTableCell(UI.Label(text=str(f))))
                    cnt.append(r)
        else:
            cnt = UI.ErrorBox(title='SQL', text='Please specify your query')


        cntSQL = UI.VContainer(
                UI.HContainer(
                    UI.Form(
                        UI.HContainer(
                            UI.TextInput(name='query', size=60, value=self._sql),
                            UI.Button(text='Run', onclick='form', form='frmSQL')
                        ),
                        id='frmSQL'
                    )
                ),
                UI.Spacer(height=20),
                cnt
             )
        return cntSQL

    def get_ui_login(self):
        lstBends = UI.Select(name='backend')
        for b in self.backends:
            lstBends.append(UI.SelectOption(value=b, text=b))

        dlgLogin = UI.DialogBox(
                        UI.LayoutTable(
                            UI.LayoutTableRow(
                                UI.Label(text='Backend:'),
                                lstBends
                            ),
                            UI.LayoutTableRow(
                                UI.Label(text='Host:'),
                                UI.TextInput(name='host', value='localhost')
                            ),
                            UI.LayoutTableRow(
                                UI.Label(text='Login:'),
                                UI.TextInput(name='login', value='root')
                            ),
                            UI.LayoutTableRow(
                                UI.Label(text='Password:'),
                                UI.TextInput(name='passwd', value='')
                            ),
                            UI.LayoutTableRow(
                                UI.Label(text='Database:'),
                                UI.TextInput(name='db', value='')
                            )
                        ),
                        title="SQL server connection", id="dlgLogin"
                    )

        warn = UI.ErrorBox(title='SQL', text='Not connected')
        return UI.VContainer(warn, dlgLogin if self._login_dialog else None)

    def logout(self):
        self.config.remove_option('sql', 'login')
        self.config.remove_option('sql', 'host')
        self.config.remove_option('sql', 'passwd')
        self.config.remove_option('sql', 'db')
        self.config.remove_option('sql', 'backend')
        self.config.save()

    def login(self, vars):
        self.config.set('sql', 'backend', vars.getvalue('backend', 'mysql'))
        self.config.set('sql', 'host', vars.getvalue('host', 'localhost'))
        self.config.set('sql', 'login', vars.getvalue('login', 'root'))
        self.config.set('sql', 'passwd', vars.getvalue('passwd', '')) # plaintext!
        self.config.set('sql', 'db', vars.getvalue('db', ''))
        self.config.save()

    @event('button/click')
    @event('minibutton/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'btnLogout':
            self.logout()
            self._login_dialog = True
        if params[0] == 'view':
            self._tab = 1
            self._sql = 'SELECT * FROM %s;' % params[1]

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgLogin':
            if vars.getvalue('action', '') == 'OK':
                self.login(vars)
            self._logging_in = False
            self._login_dialog = False
        if params[0] == 'frmSQL':
            self._tab = 1
            self._sql = vars.getvalue('query', '')


class SQLContent(ModuleContent):
    module = 'sql'
    path = __file__
