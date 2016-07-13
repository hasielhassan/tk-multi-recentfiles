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
A window which show the latest work files.

"""

import tank

class RecentFiles(tank.platform.Application):

    def init_app(self):
        """
        Called as the application is being initialized
        """

        self.group_files_by_name = self.get_setting('group_files_by_name')


        self.tk_multi_recentfiles = self.import_module("tk_multi_recentfiles")
        cb = lambda : self.tk_multi_recentfiles.show_dialog(self)
        # add stuff to main menu
        self.engine.register_command("Recent Work Files...", cb)


    def post_engine_init(self):

        """
        Implemented by deriving classes in order to run
        code after the engine has completely finished
        initializing itself and all its apps. At this point,
        the engine has a fully populated apps dictionary
        and all loaded apps have been fully initialized
        and validated.
        """

        # only launch the dialog once at startup
        # use tank object to store this flag
        if not hasattr(tank, '_tk_multi_recent_files_shown'):
            # very first time we run this app
            tank._tk_multi_recent_files_shown = True
            # show the UI at startup - but only if the engine supports a UI
            if self.get_setting('launch_at_startup') and self.engine.has_ui:
                self.tk_multi_recentfiles.show_dialog(self)