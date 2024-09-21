# -*- coding: utf-8 -*-
"""Some general utilitary stuff"""

import os
from PySide6.QtGui import ( # pylint: disable=no-name-in-module,import-error
    QDesktopServices
)
from PySide6.QtCore import ( # pylint: disable=no-name-in-module
    Slot,
    QUrl
)
import maya.cmds as cmds # pylint: disable=no-name-in-module,import-error
import dublast.dumaf as maf

@Slot()
def open_help():
    """Opens the online help for the addon"""
    QDesktopServices.openUrl( QUrl( "https://codeberg.org/RxLaboratory/DuBlast-Maya" ) )

@Slot()
def donate():
    """Opens the donation page"""
    QDesktopServices.openUrl( QUrl( "http://donate.rxlab.info" ) )

def getVideoPlayer():
    """Gets the video player to use when playblasting"""
    default = os.path.dirname( cmds.pluginInfo('DuBlast', query=True, path=True) )
    default = default + '/ffplay.exe'
    current = maf.options.get('dublast.videoPlayer', default)
    if current == "":
        current = default
    return current
