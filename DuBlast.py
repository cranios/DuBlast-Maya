# -*- coding: utf-8 -*-
"""Better Playblasts for Maya"""

#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either VERSION 3
#  of the License, or (at your option) any later VERSION.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#======================= END GPL LICENSE BLOCK ========================

import maya.api.OpenMaya as om # pylint: disable=import-error

from dublast import DuBlastCmd, VENDOR, VERSION

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass

def initializePlugin( obj ):
    """Registers the command"""
    plugin = om.MFnPlugin(obj, VENDOR, VERSION)

    plugin.registerCommand( DuBlastCmd.name, DuBlastCmd.createCommand, DuBlastCmd.createSyntax )

def uninitializePlugin( obj ):
    """Unregisters the command"""
    plugin = om.MFnPlugin(obj, VENDOR, VERSION)

    plugin.deregisterCommand( DuBlastCmd.name )
