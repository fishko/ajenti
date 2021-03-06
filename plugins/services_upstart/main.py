import os

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis


class UpstartServiceManager(Plugin):
    implements(apis.services.IServiceManager)
    platform = ['Debian', 'Ubuntu']

    def list_all(self):
        r = []
        found = []
                
        if os.path.exists('/etc/init'):        
            for s in os.listdir('/etc/init'):
                if len(s) > 5:
                    s = s[:-5]
                    svc = apis.services.Service()
                    svc.name = s
                    if 'start/running' in shell('service %s status' % s):
                        svc.status = 'running'
                        r.append(svc)
                        found.append(s)
                    elif 'stop/waiting' in shell('service %s status' % s):
                        svc.status = 'stopped'
                        r.append(svc)
                        found.append(s)
                    
        for s in shell('service --status-all').split('\n'):
            if len(s) > 3 and s[3] != '?':
                name = s.split()[3]
                if not name in found:
                    found.append(name)
                    svc = apis.services.Service()
                    svc.name = name
                    svc.status = 'running' if s[3] == '+' else 'stopped'
                    r.append(svc)
            
        return sorted(r, key=lambda s: s.name)

    def start(self, name):
        shell('service ' + name + ' start')

    def stop(self, name):
        shell('service ' + name + ' stop')

    def restart(self, name):
        shell('service ' + name + ' --full-restart')
