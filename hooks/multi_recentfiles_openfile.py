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
Hook that loads items into the current scene. 

This hook supports a number of different platforms and the behaviour on each platform is
different. See code comments for details.


"""
import tank
import os
from tank.platform.qt import QtGui

class AddFileToScene(tank.Hook):
    
    def execute(self, engine_name, file_path, **kwargs):
        """
        Hook entry point and app-specific code dispatcher
        """
                
        if self.parent.engine.name == "tk-nuke":
            self.load_item_from_path_nuke(file_path)
        
        elif self.parent.engine.name == "tk-maya":
            self.load_item_from_path_maya(file_path)
        
        elif self.parent.engine.name == "tk-motionbuilder":
            self.load_item_from_path_motionbuilder(file_path)
        
        elif self.parent.engine.name == "tk-3dsmax":
            self.load_item_from_path_3dsmax(file_path)

        elif self.parent.engine.name == "tk-3dsmaxplus":
            self.load_item_from_path_3dsmaxplus(file_path)

        elif self.parent.engine.name == "tk-photoshop":
            self.load_item_from_path_photoshop(file_path)

        elif self.parent.engine.name == 'tk-hiero':
            self.load_item_from_path_hiero(file_path)

        elif self.parent.engine.name == 'tk-fusion':
            self.load_item_from_path_fusion(file_path)

        else:
            raise tank.TankError("Unsupported engine '%s'!" % engine_name)
                
        
        ##########################################################################################

    def load_item_from_path_hiero(self, path):

        import hiero

        # close open projects
        hiero.core.closeAllProjects(False)

        # fix slashes
        path = path.replace(os.sep, '/')
        # manually fire signal since Hiero doesn't fire this when loading 
        # from the tk file manager
        hiero.core.events.sendEvent("kBeforeProjectLoad", None)
        # open
        hiero.core.openProject(path)

        
    def load_item_from_path_nuke(self, path):
        
        import nuke
        # fix slashes
        path = path.replace(os.sep, "/")
        # open
        nuke.scriptOpen(path)


    def load_item_from_path_fusion(self, path):
        
        import PeyeonScript
        f_connection = PeyeonScript.scriptapp ("Fusion")

        # open
        f_connection.LoadComp (path)
        
        
    def load_item_from_path_maya(self, path):
        
        import pymel.core as pm
        import maya.cmds as cmds
        # fix slashes
        path = path.replace(os.sep, "/")
        
        if cmds.file(query=True, modified=True):
            
            # changes have been made to the scene
            res = QtGui.QMessageBox.question(None,
                                             "Save your scene?",
                                             "Your scene has unsaved changes. Save before proceeding?",
                                             QtGui.QMessageBox.Yes|QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel)
            
            if res == QtGui.QMessageBox.Cancel:
                # return to dialog
                return

            elif res == QtGui.QMessageBox.No:
                # don't save!
                pm.system.openFile(path, force=True)
            
            else:
                # save before!
                
                if pm.sceneName() != "":
                    # scene has a name!
                    # normal save
                    cmds.file(save=True, force=True)
                else:
                    # scene does not have a name. 
                    # save as dialog
                    cmds.SaveSceneAs()
                    # not sure about return value here, so check the scene!
                    if cmds.file(query=True, modified=True):
                        # still unsaved changes
                        # assume user clicked cancel in dialog
                        return
                    
        # okay all good to go. Scene is saved and has a name.
        # now we can safely replace it with the desired scene... :)
        pm.system.openFile(path)
        
        
    def load_item_from_path_motionbuilder(self, path):

        from pyfbsdk import FBApplication
        app = FBApplication()
        app.FileOpen(path)
        
        
    def load_item_from_path_3dsmax(self, path):

        from Py3dsMax import mxs
        
        # there is a file open
        if mxs.getSaveRequired():
            # there are unsaved changes in the scene
            # TODO: handle this for the user!
            
            # the currently opened file has not been saved
            mxs.messageBox("Your current scene has unsaved changes. Please save it before proceeding.")
            return
                    
        else:
            # no need to save any change. load new file.
            mxs.loadMaxFile(path)

    def load_item_from_path_3dsmaxplus(self, path):

        import MaxPlus

        # there is a file open
        if MaxPlus.FileManager.IsSaveRequired():
            # there are unsaved changes in the scene
            res = QtGui.QMessageBox.question(None,
                                             "Save your scene?",
                                             "Your scene has unsaved changes. Save before proceeding?",
                                             QtGui.QMessageBox.Yes|QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel)
            
            if res == QtGui.QMessageBox.Cancel:
                # return to dialog
                return

            elif res == QtGui.QMessageBox.No:
                # don't save!
                MaxPlus.FileManager.Open(path)
                return

            else:
                # save before!

                if MaxPlus.FileManager.GetFileNameAndPath() != '':
                    # scene has a name!
                    # normal save
                    if MaxPlus.FileManager.Save(MaxPlus.FileManager.GetFileNameAndPath()):
                        MaxPlus.FileManager.Open(path)
                    else:
                        # still unsaved changes
                        # assume user clicked cancel in dialog
                        return

                else:
                    # scene does not have a name. 
                    # save as dialog
                    if MaxPlus.FileManager.SaveAs():
                        MaxPlus.FileManager.Open(path)
                    else:
                        # still unsaved changes
                        # assume user clicked cancel in dialog
                        return
                    
        else:
            # no need to save any change. load new file.
            MaxPlus.FileManager.Open(path)

    def load_item_from_path_photoshop(self, path):
        import photoshop
        f = photoshop.RemoteObject('flash.filesystem::File', path)
        photoshop.app.load(f)
