# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import tank
import os
import sys
import threading

from tank.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog

class AppDialog(QtGui.QWidget):

    def __init__(self, app):
        QtGui.QWidget.__init__(self)
        # set up the UI
        self.ui = Ui_Dialog()
        self._app = app 
        self.ui.setupUi(self)
        
        # display the context in the title bar of the window
        ctx_name = str(self._app.context)        
                
        # set up the browsers
        self.ui.browser.set_app(self._app)
        self.ui.browser.set_label(ctx_name)
        
        self.ui.browser.action_requested.connect( self.load_item )
        self.ui.browser.history_item_action.connect( self.load_item_from_path )
        self.ui.browser.delete_item_action.connect( self.delete_item_from_path )
        self.ui.browser.selection_changed.connect( self.toggle_load_button_enabled )
        self.ui.load.clicked.connect( self.load_item )
                
        self.toggle_load_button_enabled()
        # load data from shotgun
        self.setup_file_list()        
        
    ########################################################################################
    # make sure we trap when the dialog is closed so that we can shut down 
    # our threads. Nuke does not do proper cleanup on exit.
    
    def closeEvent(self, event):
        self.ui.browser.destroy()
        # okay to close!
        event.accept()
        
    ########################################################################################
    # basic business logic        
        
    def toggle_load_button_enabled(self):
        """
        Control the enabled state of the load button
        """
        curr_selection = self.ui.browser.get_selected_item()
        if curr_selection is None:
            self.ui.load.setEnabled(False)
        else:
            self.ui.load.setEnabled(True)
        
    def setup_file_list(self): 
        self.ui.browser.clear()
        d = {}
        self.ui.browser.load(d)
        
    def load_item(self):
        """
        Load something into the scene
        """
        curr_selection = self.ui.browser.get_selected_item()
        if curr_selection is None:
            return
        
        self.load_item_from_path(curr_selection.path)
        
        
    def load_item_from_path(self, path):

        # call out to our hook for loading.
        self._app.log_debug("Calling load hook for %s" % path)

        self._app.execute_hook("hook_add_file_to_scene", 
                               engine_name=self._app.engine.name, 
                               file_path=path)
        
        # close dialog
        self.close()


    def delete_item_from_path(self, path):

        # call out to our hook for loading.
        self._app.log_debug("Calling delete hook for %s" % path)

        self._app.execute_hook("hook_delete_file_from_path",
                               file_path=path)

        self.setup_file_list()     
        
        
