#!/usr/bin/env python3
# npackage example  https://svn.lliurex.net/pandora/n4d-ldap/trunk
# jinja2 http://jinja.pocoo.org/docs/templates

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
from jinja2 import Template
import tempfile
import shutil
import os
import subprocess
import string
import random
import crypt
from n4d.server.core import Core
import n4d.responses
from n4d.utils import n4d_mv

class NetinstallManager:

    def __init__(self):
        try:
            self.n4d = Core.get_core()
        except Exception as e:
            return build_authentication_failed_response()
        #Load template file
        self.tpl_env = Environment(loader=FileSystemLoader('/usr/share/n4d/templates/netinstall'))
        self.imagepath="/etc/ltsp/bootopts/"
        pass
    #def init
    
    def startup(self,options):
        # executed when launching n4d
        pass    
    #def startup

    def apt(self):
        # executed after apt operations
        pass    
    #def apt
    
    # service test and backup functions #
    def test(self):
        pass
    #def test
    
    def backup(self):
        pass
    #def test
    
    def restore(self):
        pass
    #def test
        
    def load_exports(self,restart_dnsmasq=False):
        #Get template
        template_cname = self.tpl_env.get_template("cname")
        list_variables = {}
        
        ###########################
        #Getting VARS
        ###########################
        try:
            list_variables.setdefault('INTERNAL_DOMAIN',self.n4d.get_variable('INTERNAL_DOMAIN').get('return',None))
            list_variables.setdefault('HOSTNAME',self.n4d.get_variable('HOSTNAME').get('return',None))
        except Exception as e:
            return n4d.responses.build_authentication_failed_response()
        if not list_variables.get('INTERNAL_DOMAIN',None):
            return n4d.responses.build_failed_call_response(-1,'Variable INTERNAL_DOMAIN not defined')
        if not list_variables.get('HOSTNAME',None):
            return n4d.responses.build_failed_call_response(-1,'Variable HOSTNAME not defined')
            
        #Encode vars to UTF-8
        string_template = template_cname.render(list_variables).encode('UTF-8')
        #Open template file
        fd, tmpfilepath = tempfile.mkstemp()
        new_export_file = open(tmpfilepath,'w')
        new_export_file.write(string_template)
        new_export_file.close()
        os.close(fd)
        #Write template values
        n4d_mv(tmpfilepath,'/var/lib/dnsmasq/config/cname-preseed',True,'root','root','0644',True )
        if restart_dnsmasq:
            subprocess.Popen(['systemctl','restart','dnsmasq'],stdout=subprocess.PIPE).communicate()
        return n4d.responses.build_successful_call_response(ret_msg='Exports written')
    #def load_exports
    
    def getNetinstall(self):
        '''
        Reads file /etc/ltsp/bootopts/netinstall and returns true or false
        '''
        # 1. /opt/ltsp/name-chroot
        # 2. /opt/ltsp/images/name-chroot.img
        # 3. /var/lib/tftpboot/ltsp/name-chroot
        # if 1,2 and 3 exist -> show
        # if 1 but not exist 2 or/and 3 -> show with error
        #
        
        json_data=open(self.imagepath+"netinstall.json")
        data = json.load(json_data)
        json_data.close()
        
        if(data["netinstall_boot"].lower()=="true"):
            netinstall='true';
        else:
            netinstall='false';
        if(data["netinstall_unattended"].lower()=="true"):
            unattended='true';
        else:
            unattended='false';
        
        if("netinstall_stats" not in list(data.keys()) or data["netinstall_stats"].lower()!="false"):
            do_stats='true';
            data['netinstall_stats']='true';
        else:
            do_stats='false';
        if("nongplapps" not in list(data.keys()) or data["nongplapps"].lower()=="false"):
            nongplapps='false';
            data['nongplapps']='false';
        else:
            nongplapps='true';
        
        if ("normal_install" not in list(data.keys()) or data["normal_install"].lower() == "false"):
                normal_install='false';
                data['normal_install']='false';
        else:
                normal_install='true';
        #write the json file
        ret=self.setNetinstall(data["netinstall_boot"].lower(),data["netinstall_unattended"].lower(),data["netinstall_stats"].lower(),data["nongplapps"].lower(),data["normal_install"].lower())
        if ret['status'].lower() != 'true':
            raise n4d.responses.build_failed_call_response(-1,ret_msg='Error setting json file calling setNetinstall')
        
        return n4d.responses.build_successful_call_response(ret_msg="{}".format({"netinstall":netinstall, "unattended":unattended, "stats": do_stats, 'nongplapps':nongplapps, 'normal_install':normal_install}))     
    # END def GetNetInstall

    def setNetinstall(self, status, unattended, stats, nongplapps, type_install):
        '''
        receives data from admin-center form
        sets option for netinstall int bootopt.json (status and unattended install)
        '''
        try:
            mirror_var="/var/lib/n4d/variables-dir/LLIUREXMIRROR"
            if os.path.isfile(mirror_var):
                if (status.lower()=="true" or status.lower()=="false"):
                    path_to_write = os.path.join(self.imagepath,"netinstall.json")
                    f = open(path_to_write,'w')
                    data='{"netinstall_boot":"'+str(status)+'", "netinstall_unattended":"'+str(unattended)+'", "netinstall_stats":"'+str(stats)+'","nongplapps":"'+str(nongplapps)+'"'+',"normal_install":"'+type_install+'"}'
                    f.writelines(data)
                    f.close()
                    
                    # Enable or disable NETINSTALL on menu (the last option, but enabled)
                    if (status.lower()=="true"):
                        self.n4d.get_plugin("LlxBootManager").pushToBootList("netinstall")
                    else:
                        self.n4d.get_plugin("LlxBootManager").removeFromBootList("netinstall")

                    # Removing user and password from preseed
                    self.setNetinstallUnattended(status, "", "", "")
                    
                    return n4d.responses.build_successful_call_response()
    
                else:
                    return n4d.responses.build_invalid_arguments_response(-1)
                    # return {"status":"false", "msg":"option not valid"}
            else:
                    return n4d.responses.build_failed_call_response(-1,ret_msg='mirror is not available')
                    # return {"status":"false", "msg":"mirror is not available"}
                
            #return data;
        except Exception as e:
            return {"status":"false", "msg":str(e)};

        # END def getListTemplate(self, image)
    
    def set_force_classroom_stats(self,stats):
        var_name='STATS_ENABLED'
        stats_value = self.n4d.get_variable(var_name)
        
        ret = False
        if  stats_value == None:
            # Register new variable
            ret = self.n4d.set_variable(var_name,'0',{'description':'Stats enabled for lliurex-statistics'})
            if stats.lower() == 'true' or stats == '1':
            # Enable 
                ret = self.n4d.set_variable(var_name,'1')
            else:
                # Disable
                ret = self.n4d.set_variable(var_name,'0')
        if ret != True:
            return n4d.responses.build_failed_call_response(-1,ret_msg='Error setting variable')
        else:
            return n4d.responses.build_successful_call_response()
    #END def set_force_classroom_stats(self,status)
    
    def get_force_classroom_stats(self):
        var_name='STATS_ENABLED'
        stats_value = self.n4d.get_variable(var_name)
        
        if  stats_value == None:
            # Register new variable
            ret = self.n4d.set_variable(var_name,'0',{'description':'Stats enabled for lliurex-statistics'})
            stats_value = self.n4d.get_variable(var_name)
            # return n4d.responses.build_successful_call_response(ret_msg=stats_value)
            # return str(stats_value)
        return n4d.responses.build_successful_call_response(ret_msg=stats_value)
        #else:
        #    return n4d.responses.build_successful_call_response(ret_msg=stats_value)
            # return str(stats_value)
    #END def get_force_classroom_stats(self):
    
    def install_nongpl(self, do):
        '''
        TODO: REMOVE THIS FUNCTION , NONGPL FUNCTIONS (FLASH)
        '''
        if isinstance(do,bool):
            do=str(do).lower()
        elif isinstance(do,str):
            do=do.lower()
        else:
            do="false"

        filedir="/var/www/preseed"
        filename="extra-packages.netinstall"
        file=filedir+'/'+filename
        line="repository: http://archive.canonical.com/ubuntu xenial partner\n"
        line+="package: adobe-flashplugin\n"
        try:
            with open(file,'w') as fp:
                if do == 'true':
                    fp.write(line)
            return n4d.responses.build_successful_call_response()
            # return {'status':"True",'msg': 'Ok'}
        except Exception as e:
            return n4d.responses.build_failed_call_response(-1,ret_msg=str(e))
            # return {'status':"False",'msg': str(e)}         
    # END def install_nongpl(self, do):
    
    def set_desktop_type(self, thin=False):
        if isinstance(thin,bool):
            thin=str(thin).lower()
        elif isinstance(thin,str):
            thin=thin.lower()
        else:
            thin="false"

        filedir="/var/www/preseed"
        filename="extra-commands.netinstall"
        file=filedir+'/'+filename
        if thin == 'true':
            line="in-target sh -c 'llx-desktop-layout set classic || (touch /llx-desktop-layout-not-found; echo true > /llx-desktop-layout-not-found)'"
        else:
            line="in-target sh -c 'llx-desktop-layout set default || (touch /llx-desktop-layout-not-found; echo false > /llx-desktop-layout-not-found)'"
        try:
            with open(file,'w') as fp:
                fp.write(line)
            return n4d.responses.build_successful_call_response()
            # return {'status':"True",'msg': 'Ok'}
        except Exception as e:
            return n4d.responses.build_failed_call_response(-1,ret_msg=str(e))
            # return {'status':"False",'msg': str(e)}         
    # END def set_desktop_type(self, thin):
    
    def setNetinstallUnattended(self, status, username, password, rootpassword):
        '''
        Writing in presseed username and password
        '''				
        if status == True and (not username or not password or not rootpassword):
            return n4d.responses.build_failed_call_response(-1,ret_msg="Usernames or Passwords can't be an empty string")
            # return {"status":"false", "msg": "Usernames or Passwords can't be an empty string"}
        try:
            filedir="/var/www/preseed"
            filepath="/var/www/preseed/unattended.cfg"
            filepartman="/var/www/preseed/partman_sda.cfg"

            if not os.path.exists(filedir):
                os.makedirs(filedir)
            
            preseed=open(filepath,'w')
            preseed.write("# LMD Created user account\n")
            salt=''.join([random.choice(string.ascii_letters + string.digits) for _ in range(16)])
            userpassencrypted=crypt.crypt(str(password),"$6$"+salt+"$")
            salt=''.join([random.choice(string.ascii_letters + string.digits) for _ in range(16)])
            rootpassencrypted=crypt.crypt(str(rootpassword),"$6$"+salt+"$")
            
            if(status==True):
                # Saving file
                
                userfullline="d-i passwd/user-fullname string "+str(username)+"\n";
                userline="d-i passwd/username string "+str(username)+"\n";
                passline="d-i passwd/user-password-crypted password "+str(userpassencrypted)+"\n"
                
                if (len(rootpassword) > 0):
                    rootpassline = "d-i passwd/root-password-crypted password "+str(rootpassencrypted) + "\n"
                else:
                    rootpassline = "# d-i passwd/root-password-crypted password "+str(rootpassencrypted) + "\n"
                    
                # Partition preseed
                try:
                    partman = open(filepartman,'r')
                    preseed.writelines(partman.readlines())
                    preseed.write("\n")
                    partman.close()
                except Exception as e:
                    return str(e)
                
            else:
                userfullline="#d-i passwd/user-fullname string \n"
                userline="#d-i passwd/username string \n"
                passline="# d-i passwd/user-password-crypted password \n"
                rootpassline = "# d-i passwd/root-password-crypted password \n"

            preseed.write("# Normal user name\n")
            preseed.write(userfullline)
            preseed.write(userline)
            preseed.write("# Normal user's password, either in clear text\n")
            preseed.write("#d-i passwd/user-password password insecure\n")
            preseed.write("# Normal user's password encrypted using an MD5 hash.\n")
            preseed.write(passline)
            preseed.write(rootpassline)
            
            # Allow weak passwords
            preseed.write("d-i user-setup/allow-password-weak boolean true\n")
            
            preseed.close()
            
            return n4d.responses.build_successful_call_response()
            # return {"status":"true", "msg":"all ok"}
            
        except Exception as e:
            return n4d.responses.build_failed_call_response(-1,ret_msg=str(e))
            # return {"status":"false", "msg":str(e)}
    # END def getListTemplate(self, image)
    
#class N4dProxy 
if __name__ == '__main__':
    pass
    # m = NetinstallManager()
    # print(m.load_exports(True))
    # print(m.getNetinstall())
    # status = True
    # unattended = True
    # stats = True
    # nongplapps = True
    # type_install = True
    # print(m.setNetinstall(status,unattended,stats,nongplapps,type_install))
    # stats = False
    # print(m.set_force_classroom_stats(stats))
    # print(m.get_force_classroom_stats())
    # do = False
    # print(m.install_nongpl(do))
    # thin = True
    # print(m.set_desktop_type(thin))
    # status = False
    # username = 'lliurex'
    # password = 'lliurex'
    # rootpassword = 'lliurex'
    # print(m.setNetinstallUnattended(status,username,password,rootpassword))    
