'''
Created on 02-Nov-2013
@author: Nisheeth Barthwal
'''

from bs4 import BeautifulSoup
import urllib
import httplib2
import json

class Jcli(object):
    '''
    classdocs
    '''

    def __init__(self, site):
        self._http = httplib2.Http()
        self._cookie = None
        self._token = None
        if site.startswith('http://'):
            self._site = site.rstrip('/')
        else:
            raise Exception('Need absolute URI')
    
    def login(self, username, password):
        self._site_cfg = {
                            'username': username,
                            'password': password,
                          }
        print 'Logging in...'
        self._login()
        
    def plugin_install(self, install_type='directory', data=''):
        print 'Fetch install token...'
        allowed_types = ('folder', 'url')
        if install_type not in allowed_types:
            raise Exception('Only types allowed are: %s' % allowed_types)
        self._plg1_get_token()
        self._plg_cfg = {
                            'install_type': install_type,
                            'install_data': data,
                         }
        print 'Installing...'
        self._plg2_install()

    def install(self, cfg):
        self._cfg = cfg
        has = set(self._cfg.keys())
        diff = set([ 'site_name',
                    'site_description',
                    'admin_email',
                    'admin_user',
                    'admin_password1',
                    'admin_password2',
                    'site_offline',
                    'db_type',
                    'db_host',
                    'db_user',
                    'db_pass',
                    'db_name',
                    'db_prefix',
                    'db_old',
                    'sample_file',
                    'summary_email',
                    'summary_email_passwords',
                    'install_langs',
                    'administratorlang',
                    'frontendlang']) - has
                    
        if len(diff):
            raise Exception('Keys missing: %s' % diff)
        import time
        t = time.time()
        print 'Fetching token...'
        self._step1_get_token()
        print 'Site config...'
        self._step2_site_cfg()
        print 'DB config...'
        self._step3_db_cfg()
        print 'Email config...'
        self._step4_email_cfg()
        print 'Remove old DB...'
        self._step5_remove_db()
        print 'Create DB...'
        self._step6_create_db()
        print 'Install sample...'
        self._step7_install_sample()
        print 'Install config...'
        self._step8_install_config()
        if int(self._cfg['summary_email']) == 1:
            print 'Install email...'
            self._step9_install_email()
        print 'List languages...'
        self._step10_list_lang()
        print 'Install languages...'
        self._step11_install_lang()
        print 'List selectable languages...'
        self._step12_list_lang_select()
        print 'Set default languages...'
        self._step13_default_lang()
        print 'Fetch remove token...'
        self._step14_get_remove_token()
        print 'Remove directory...'
        self._step15_remove_dir()
        print 'Total time', (time.time() - t) 
        
    def _plg1_get_token(self):
        h = {
               'Cookie': self._cookie
               }
        resp, content = self._http.request(self.url('administrator/index.php?option=com_installer'), 'GET', headers=h)
        if resp.has_key('set-cookie'):
            self._cookie = resp['set-cookie']
            

        soup = BeautifulSoup(content)
        self._token = soup.find('input', {'value': 1, 'type': 'hidden'})['name']
    
    def _plg2_install(self):
        cfgdata = self._plg_cfg['install_data']
        
        data = {
                'installtype'       : self._plg_cfg['install_type'],
                'install_directory' : '/media/work/PHP/sites/instagib/joomla/tmp/jce',
                'task'              : 'install.install',
                self._token         : '1',
            }
        
        if data['installtype'] == 'folder':
            data['install_directory'] = cfgdata
        elif data['installtype'] == 'url':
            data['install_url'] = cfgdata
        
        r, _ = self._login_post('administrator/index.php?option=com_installer&view=install', data)
        if r['status'] != '200':
            raise Exception('Error installing plugin')

    
    def _login(self):
        resp, content = self._http.request(self.url('administrator/index.php'), 'GET')
        if resp['status'] == '404':
            raise Exception('File does not exist at: %s' % self.url('administrator/index.php'))
        
        self._cookie = resp['set-cookie']
        
        soup = BeautifulSoup(content)
        self._token = soup.find('input', {'value': 1, 'type': 'hidden'})['name']
        return_val = soup.find('input', {'name': 'return', 'type': 'hidden'})['value']
        
        r, _ = self._login_post('administrator/index.php', data = {
            'username'      : self._site_cfg['username'],
            'passwd'        : self._site_cfg['password'],
            'lang'          : '',
            'option'        : 'com_login',
            'task'          : 'login',
            'return'        : return_val,
            self._token     : '1',
            })
        
        if r['status'] != '200':
            raise Exception('Error logging in')

    def url(self, uri):
        return '%s/%s' % (self._site, uri.lstrip('/'))
    
    def _login_post(self, uri, data):
        h = {
               'Content-type': 'application/x-www-form-urlencoded',
               'Cookie': self._cookie
               }
        resp, content = self._http.request(self.url(uri), 'POST', urllib.urlencode(data, doseq=True), headers=h)
        if resp.has_key('set-cookie'):
            self._cookie = resp['set-cookie']
        return resp, content

        
    def _install_post(self, uri, data):
        h = {
               'Content-type': 'application/x-www-form-urlencoded',
               'Cookie': self._cookie
               }
        resp, content = self._http.request(self.url(uri), 'POST', urllib.urlencode(data, doseq=True), headers=h)
        content = json.loads(content)
        if resp.has_key('set-cookie'):
            self._cookie = resp['set-cookie']
        self._token = content['token']
        
    def _step1_get_token(self):
        resp, content = self._http.request(self.url('installation/index.php'), 'GET')
        if resp['status'] == '404':
            raise Exception('Installation file does not exist at: %s' % self.url('installation/index.php'))
        soup = BeautifulSoup(content)
        token = soup.find('input', {'value': 1, 'type': 'hidden'})['name']
        self._cookie = resp['set-cookie']
        self._token = token
        
    def _step2_site_cfg(self):
        self._install_post('installation/index.php', data = {
                'format'                : 'json',
                'jform[site_name]'      : self._cfg['site_name'], #'lol1234',
                'jform[site_metadesc]'  : self._cfg['site_description'], #'Descriptah',
                'jform[admin_email]'    : self._cfg['admin_email'], #'nbaztec@gmail.com',
                'jform[admin_user]'     : self._cfg['admin_user'], #'nbaztec',
                'jform[admin_password]' : self._cfg['admin_password1'], #'mayans',
                'jform[admin_password2]': self._cfg['admin_password2'], #'mayans',
                'jform[site_offline]'   : self._cfg['site_offline'], #'0',
                'task'                  : 'site',
                self._token             : '1',
                })
    
    def _step3_db_cfg(self):
        self._install_post('installation/index.php', data = {
                'format'            : 'json',
                'jform[db_type]'    : self._cfg['db_type'], #'mysqli',
                'jform[db_host]'    : self._cfg['db_host'], #'localhost',
                'jform[db_user]'    : self._cfg['db_user'], #'nbaztec',
                'jform[db_pass]'    : self._cfg['db_pass'], #'',
                'jform[db_name]'    : self._cfg['db_name'], #'jtest02',
                'jform[db_prefix]'  : self._cfg['db_prefix'], #'lol_',
                'jform[db_old]'     : self._cfg['db_old'], #'remove',
                'task'              : 'database',
                self._token         : '1',
                })
    
    def _step4_email_cfg(self):
        self._install_post('installation/index.php', data = {
                'format'                        : 'json',
                'jform[sample_file]'            : self._cfg['sample_file'], #'sample_data.sql',
                'jform[summary_email]'          : self._cfg['summary_email'], #'1',
                'jform[summary_email_passwords]': self._cfg['summary_email_passwords'], #'1',
                'task'              : 'summary',
                self._token         : '1',
                })
    
    def _step5_remove_db(self):
        self._install_post('installation/index.php?task=InstallDatabase_remove', data = {
                'format'            : 'json',
                self._token         : '1',
                })
    
    def _step6_create_db(self):
        self._install_post('installation/index.php?task=InstallDatabase', data = {
                'format'            : 'json',
                self._token         : '1',
                })
    
    def _step7_install_sample(self):
        self._install_post('installation/index.php?task=InstallSample', data = {
                'format'            : 'json',
                self._token         : '1',
                })
    
    def _step8_install_config(self):
        self._install_post('installation/index.php?task=InstallConfig', data = {
                'format'            : 'json',
                self._token         : '1',
                })
        
    def _step9_install_email(self):
        self._install_post('installation/index.php?task=InstallEmail', data = {
                'format'            : 'json',
                self._token         : '1',
                })
    
    def _step10_list_lang(self):
        
        h = {
                   'Cookie': self._cookie
                   }
        _, content = self._http.request(self.url('installation/index.php?tmpl=body&view=languages'), 'GET', headers=h)
        
        soup = BeautifulSoup(content)
        
        '''
        # Find languages
        langs = {}
        for t in soup.find_all('label', {'class': 'checkbox'}):
            cb = t.find('input', {'type': 'checkbox'})
            for s in t.findAll(text=True):
                l = s.strip()
                if len(l):
                    langs[l.lower()] = cb['value']
                    break
        self._langs = langs
        print self._langs
        '''
        self._token = soup.find('input', {'type' : 'hidden', 'value' : '1'})['name']
        
        _, content = self._http.request('http://update.joomla.org/language/translationlist_3.xml', 'GET')
        soup = BeautifulSoup(content)
        langs = {}
        i = 0
        for e in soup.find_all('extension'):
            i+=1
            langs[e['element'][4:]] = {
                                       'name': e['name'],
                                       'id': i
                                       }
        self._langs = langs
        #print self._langs
    
    def _step11_install_lang(self):
        data = {
                'format'            : 'json',
                'task'              : 'InstallLanguages',
                'cid[]'             : [],
                self._token         : '1',
                }
        for l in self._cfg['install_langs']:
            data['cid[]'].append(self._langs[l]['id'])
        self._install_post('installation/index.php', data)
    
    def _step12_list_lang_select(self):
        h = {
                   'Cookie': self._cookie
                   }
        _, content = self._http.request(self.url('installation/index.php?tmpl=body&view=defaultlanguage'), 'GET', headers=h)
        # Find languages select
        langs = {
         'admin': {},
         'front': {},
         }
        soup = BeautifulSoup(content)
        for t in soup.find_all('input', {'name': 'administratorlang'}):
            langs['admin'][''.join(t.parent.parent.find('td', {'align': 'center'}).find_all(text=True)).strip().split()[0].lower()] = t['value']
        for t in soup.find_all('input', {'name': 'frontendlang'}):
            langs['front'][''.join(t.parent.parent.find('td', {'align': 'center'}).find_all(text=True)).strip().split()[0].lower()] = t['value']
        self._langs_select = langs
        self._token = soup.find('input', {'type' : 'hidden', 'value' : '1'})['name']
    
    def _step13_default_lang(self):
        self._install_post('installation/index.php', data = {
                'format'            : 'json',
                'administratorlang' : self._cfg['administratorlang'],
                'frontendlang'      : self._cfg['frontendlang'],
                'task'              : 'setdefaultlanguage',
                self._token         : '1',
                })
    
    def _step14_get_remove_token(self):
        h = {
                   'Cookie': self._cookie
                   }
        _, content = self._http.request(self.url('installation/index.php?tmpl=body&view=remove'), 'GET', headers=h)
        # Find languages select
        soup = BeautifulSoup(content)
        self._token = soup.find('input', {'type' : 'hidden', 'value' : '1'})['name']
        
    def _step15_remove_dir(self):
        self._install_post('installation/index.php?task=removefolder', data = {
                'format'            : 'json',
                'instDefault': 'Remove installation folder',
                self._token         : '1',
                })
        
