'''
Created on 02-Nov-2013

@author: Nisheeth Barthwal
'''

from jcli import Jcli

if __name__ == '__main__':
    jc = Jcli('http://localhost/instagib/joomla/')
    
    # Install the joomla instance
    jc.install({
                    'site_name'         : 'My Joomla! Site',
                    'site_description'  : 'Site description for my playground',
                    'admin_email'       : 'user@domain.com',
                    'admin_user'        : 'juser',
                    'admin_password1'   : 'jpasswd',
                    'admin_password2'   : 'jpasswd',
                    'site_offline'      : '0', #0/1
                    'db_type'           : 'mysqli',
                    'db_host'           : 'localhost',
                    'db_user'           : 'jdbuser',
                    'db_pass'           : 'jdbpasswd',
                    'db_name'           : 'jdbname',
                    'db_prefix'         : 'pre_',
                    'db_old'            : 'remove', #backup/remove
                    'sample_file'       : 'sample_data.sql',
                    'summary_email'     : '0',
                    'summary_email_passwords': '0',
                    'install_langs'     : ['fr-FR', 'de-DE'],   # Besides en-GB
                    'administratorlang' : 'en-GB',
                    'frontendlang'      : 'fr-FR'
                })
    
    # Install plugins
    jc.login('myusername', 'mypassword')
    jc.plugin_install('url', 'http://www.joomlacontenteditor.net/downloads/editor/joomla-30?task=callelement&format=raw&item_id=1059&element=f85c494b-2b32-4109-b8c1-083cca2b7db6&method=download&args[0]=ece1ef1b710ab3dbec6004347d55eb8e')
    jc.plugin_install('folder', '/opt/sites/plugin/jce')
