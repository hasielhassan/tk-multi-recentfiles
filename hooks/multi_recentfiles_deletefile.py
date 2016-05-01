# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook that deletes items from the specified path. 

This hook supports a number of different platforms and the behaviour on each platform is
different. See code comments for details.


"""
import tank
import os
from tank.platform.qt import QtGui

class DeleteFileFromPath(tank.Hook):

    def get_file_owner(self, path):
        try:
            import pwd # wont work on windows
            owner = pwd.getpwuid(os.stat(path).st_uid).pw_name
            return owner
        except Exception, e:

            try:
                #workarround for windows

                #ensure the local python win32 librarys can be used by the engines python interpreter
                import sys
                #todo: use dynamic path, or other method...
                sys.path.append("C:\\Python27\\Lib\\site-packages\\win32")

                import win32security
                f = win32security.GetFileSecurity(path, win32security.OWNER_SECURITY_INFORMATION)
                (username, domain, sid_name_use) =  win32security.LookupAccountSid(None, f.GetSecurityDescriptorOwner())
                return username

            except:

                return None

    def perform_delete(self, path):

        import shutil

        try:
            os.remove(path)
            msg = "The file was succesfully deleted!"
            QtGui.QMessageBox.information(None, "File Deleted!", msg)
        except:
            import traceback
            error = traceback.format_exc()

            msg = "There was a problem trying to delete the file:\n%s" % error

            QtGui.QMessageBox.critical(None, "Cannot Delete File!", msg)


    
    def execute(self, file_path, **kwargs):

        if os.path.exists(file_path):

            owner = self.get_file_owner(file_path)

            if owner != None:

                filters = [["id", "is", self.parent.context.user["id"]]]

                current_user = self.parent.shotgun.find_one("HumanUser", filters, ["login"])

                if current_user != None:

                    if owner != current_user["login"]:

                        msg = "The file you are trying to delete its owned by another user!"

                        QtGui.QMessageBox.critical(None, "Cannot Delete File!", msg)

                    else:

                        self.perform_delete(file_path)

                else:

                    self.perform_delete(file_path)

            else:
                self.perform_delete(file_path)


