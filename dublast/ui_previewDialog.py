"""
The dialog with the preview options.
"""

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

import os
from PySide6.QtWidgets import ( # pylint: disable=no-name-in-module,import-error
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QSpinBox,
    QVBoxLayout,
    QFormLayout,
    QWidget,
    QComboBox,
    QLineEdit,
    QPushButton,
    QSlider,
    QFileDialog
)

from PySide6.QtCore import ( # pylint: disable=no-name-in-module,import-error
    Slot,
    Qt,
    QFileInfo
)

import maya.mel as mel  # pylint: disable=import-error
import maya.cmds as cmds # pylint: disable=import-error

import dublast.dumaf as maf
from dublast.ui_dialog import Dialog
from dublast.utils import getVideoPlayer

class PreviewDialog( Dialog ):
    """The dialog for preview options"""

    def __init__(self, parent=None):
        super(PreviewDialog, self).__init__(parent)
        self.modelEditor = None
        self.pbWin = 'ramsesPlayblasterWin'
        self.pbLayout = 'ramsesPlayblasterLayout'
        self.modelPanel = 'ramsesPlayblasterPanel'

        self._setupMenu()
        self._setupUi()
        self._loadCameras()
        self.showRenderer()
        self._connectEvents()
        self._loadSettings()

    def _setupMenu(self):
        self._resetAction = self.edit_menu.addAction("Reset defaults")
        self._setPlayerAction = self.edit_menu.addAction("Set video player...")

    def _setupUi(self):
        self.setWindowTitle( "Create preview" )
        self.setMinimumWidth(300)

        topLayout = QFormLayout()
        topLayout.setFieldGrowthPolicy( QFormLayout.AllNonFixedFieldsGrow )
        topLayout.setSpacing(3)

        self.cameraBox = QComboBox()
        topLayout.addRow("Camera:", self.cameraBox)

        sizeWidget = QWidget()
        sizeLayout = QHBoxLayout()
        sizeLayout.setContentsMargins(0,1,0,0)
        sizeLayout.setSpacing(3)
        self.sizeEdit = QSpinBox()
        self.sizeEdit.setMaximum(100)
        self.sizeEdit.setMinimum(10)
        self.sizeEdit.setSuffix(' %')
        self.sizeEdit.setValue(50)
        sizeLayout.addWidget(self.sizeEdit)
        self.sizeSlider = QSlider()
        self.sizeSlider.setOrientation( Qt.Horizontal )
        self.sizeSlider.setMaximum(100)
        self.sizeSlider.setMinimum(10)
        self.sizeSlider.setValue(50)
        sizeLayout.addWidget(self.sizeSlider)
        sizeWidget.setLayout(sizeLayout)
        topLayout.addRow("Size:", sizeWidget)

        renderOptionsWidget = QWidget()
        renderOptionsLayout = QVBoxLayout()
        renderOptionsLayout.setContentsMargins(0,1,0,0)
        renderOptionsLayout.setSpacing(3)
        self.displayAppearenceBox = QComboBox()
        self.displayAppearenceBox.addItem("Smooth Shaded", 'smoothShaded')
        self.displayAppearenceBox.addItem("Flat Shaded", 'flatShaded')
        self.displayAppearenceBox.addItem("Bounding Box", 'boundingBox')
        self.displayAppearenceBox.addItem("Points", 'points')
        self.displayAppearenceBox.addItem("Wireframe", 'wireframe')
        renderOptionsLayout.addWidget(self.displayAppearenceBox)
        self.useLightsBox = QComboBox( )
        self.useLightsBox.addItem( "Default Lighting", 'default' )
        self.useLightsBox.addItem( "Silhouette", 'none' )
        self.useLightsBox.addItem( "Scene Lighting", 'all' )
        renderOptionsLayout.addWidget(self.useLightsBox)
        self.displayTexturesBox = QCheckBox( "Display Textures")
        self.displayTexturesBox.setChecked(True)
        renderOptionsLayout.addWidget(self.displayTexturesBox)
        self.displayShadowsBox = QCheckBox("Display Shadows")
        self.displayShadowsBox.setChecked(True)
        renderOptionsLayout.addWidget(self.displayShadowsBox )
        self.aoBox = QCheckBox("Ambient Occlusion")
        self.aoBox.setChecked(True)
        renderOptionsLayout.addWidget(self.aoBox)
        self.aaBox = QCheckBox("Anti-Aliasing")
        self.aaBox.setChecked(True)
        renderOptionsLayout.addWidget(self.aaBox)
        self.onlyPolyBox = QCheckBox("Only Polygons")
        self.onlyPolyBox.setChecked(True)
        renderOptionsLayout.addWidget(self.onlyPolyBox)
        self.motionTrailBox = QCheckBox("Show Motion Trails")
        renderOptionsLayout.addWidget(self.motionTrailBox)
        self.imagePlaneBox = QCheckBox("Show Image Plane")
        renderOptionsLayout.addWidget(self.imagePlaneBox)
        self.showHudBox = QCheckBox("Show HUD")
        self.showHudBox.setChecked(True)
        renderOptionsLayout.addWidget(self.showHudBox)
        renderOptionsWidget.setLayout( renderOptionsLayout )
        topLayout.addRow("Renderer:", renderOptionsWidget)

        self.commentEdit = QLineEdit()
        self.commentEdit.setMaxLength(20)
        topLayout.addRow("Comment:", self.commentEdit)

        self._playblastBox = QCheckBox("Playblast")
        self._playblastBox.setChecked(True)
        topLayout.addRow("Type:", self._playblastBox)
        self._thumbnailBox = QCheckBox("Thumbnail")
        self._thumbnailBox.setChecked(True)
        topLayout.addRow("", self._thumbnailBox)

        folderLayout = QHBoxLayout()
        folderLayout.setSpacing(3)
        folderLayout.setContentsMargins(0,0,0,0)
        topLayout.addRow("Folder:", folderLayout)

        self.folderEdit = QLineEdit()
        self.folderEdit.setPlaceholderText("Same as scene folder")
        folderLayout.addWidget(self.folderEdit)

        self.folderButton = QPushButton("Browse...")
        folderLayout.addWidget(self.folderButton)

        folderLayout.setStretch(0, 1)
        folderLayout.setStretch(1, 0)

        self.filenameEdit = QLineEdit()
        self.filenameEdit.setPlaceholderText("Same as scene name")
        topLayout.addRow("File name:", self.filenameEdit)

        self.main_layout.addLayout(topLayout)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.setSpacing(2)
        self._renderButton = QPushButton("Render")
        buttonsLayout.addWidget( self._renderButton )
        self._cancelButton = QPushButton("Cancel")
        buttonsLayout.addWidget( self._cancelButton )
        self.main_layout.addLayout( buttonsLayout )

    def _connectEvents(self):
        self._resetAction.triggered.connect( self._resetDefaults )
        self._setPlayerAction.triggered.connect( self._setPlayer )
        self._renderButton.clicked.connect( self._ok )
        self._renderButton.clicked.connect( self.accept )
        self._cancelButton.clicked.connect( self.reject )
        self.rejected.connect(self.hideRenderer)
        self.displayAppearenceBox.currentIndexChanged.connect( self._updateLightsBox )
        self.displayAppearenceBox.currentIndexChanged.connect( self._updateRenderer )
        self.useLightsBox.currentIndexChanged.connect( self._updateRenderer )
        self.displayTexturesBox.clicked.connect( self._updateRenderer )
        self.motionTrailBox.clicked.connect( self._updateRenderer )
        self.imagePlaneBox.clicked.connect( self._updateRenderer )
        self.displayShadowsBox.clicked.connect( self._updateRenderer )
        self.cameraBox.currentIndexChanged.connect( self._updateRenderer )
        self.aaBox.clicked.connect( self._updateRenderer )
        self.aoBox.clicked.connect( self._updateRenderer )
        self.sizeSlider.valueChanged.connect( self.sizeEdit.setValue )
        self.sizeEdit.valueChanged.connect( self.sizeSlider.setValue )
        self.folderButton.clicked.connect( self._browseFolder )

    def _updateRenderer(self):
        cam = self.cameraBox.currentData()
        cmds.modelEditor(self.modelEditor,
            camera=self.cameraBox.currentData(),
            displayAppearance=self.displayAppearenceBox.currentData(),
            displayLights= self.useLightsBox.currentData(),
            displayTextures=self.displayTexturesBox.isChecked(),
            motionTrails=self.motionTrailBox.isChecked(),
            shadows=self.displayShadowsBox.isChecked(),
            imagePlane=self.imagePlaneBox.isChecked(),
            edit=True)

        cmds.setAttr('hardwareRenderingGlobals.multiSampleEnable',self.aaBox.isChecked() ) # AA
        cmds.setAttr('hardwareRenderingGlobals.ssaoEnable', self.aoBox.isChecked() ) # AO
        # JUST BRUTE FORCE
        # Otherwise Maya just doesn't understand
        cmds.lookThru(cam)
        mel.eval("lookThroughModelPanel " + cam + " modelPanel4;")
        cmds.refresh()

    def showRenderer(self):
        """Shows the renderer window / Maya viewport for capturing the preview"""
        # Get/Create window
        if not cmds.window( self.pbWin, exists=True, query=True):
            cmds.window( self.pbWin )
            # Workaround to make windowPref available later: show and delete and recreate the window
            # show
            cmds.showWindow( self.pbWin )
            # and delete :)
            cmds.deleteUI( self.pbWin )
            # and get it back
            cmds.window( self.pbWin )
            # add the layout
            cmds.paneLayout( self.pbLayout )

        # Set window title
        cmds.window(self.pbWin, title= 'Ramses Playblaster', edit=True)

        # Set window size to the renderer size
        # Prepare viewport
        cmds.windowPref(self.pbWin, maximized=True,edit=True)

        # Get/Create new model panel
        if not cmds.modelPanel(self.modelPanel,exists=True,query=True):
            cmds.modelPanel(self.modelPanel)
        cmds.modelPanel(self.modelPanel, parent=self.pbLayout, menuBarVisible=False, edit=True)

        # The model editor with default values
        self.modelEditor = cmds.modelPanel(self.modelPanel, modelEditor=True, query=True)
        # Adjust render setting
        cmds.modelEditor(self.modelEditor, activeView=True, edit=True)

        # Adjust cam
        cmds.camera(self.cameraBox.currentData(),e=True,displayFilmGate=False,displayResolution=False,overscan=1.0)
        # Clear selection
        cmds.select(clear=True)

        # Show window
        cmds.showWindow( self.pbWin )
        self._updateRenderer()

    def _ok(self):
        self._saveSettings()
        if self.onlyPolyBox.isChecked():
            cmds.modelEditor(self.modelEditor, e=True, alo=False) # only polys, all off
            cmds.modelEditor(self.modelEditor, e=True, polymeshes=True) # polys
            cmds.modelEditor(self.modelEditor, e=True, motionTrails=self.motionTrailBox.isChecked() )

    def _resetDefaults(self):
        self.sizeEdit.setValue( 50 )
        self.displayAppearenceBox.setCurrentText( "Smooth Shaded" )
        self.useLightsBox.setCurrentText( "Default Lighting" )
        self.displayTexturesBox.setChecked( True )
        self.displayShadowsBox.setChecked( True )
        self.aoBox.setChecked( True )
        self.aaBox.setChecked( True )
        self.onlyPolyBox.setChecked( True )
        self.motionTrailBox.setChecked( False )
        self.imagePlaneBox.setChecked( False )
        self.showHudBox.setChecked( True )
        self.folderEdit.setText( "" )
        maf.options.save('dublast.videoPlayer', '')

    def _loadSettings(self):
        # Init
        self.sizeEdit.setValue(
            maf.options.get('dublast.size', 50)
        )
        self.displayAppearenceBox.setCurrentText(
            maf.options.get('dublast.displayAppearance', "Smooth Shaded")
        )
        self.useLightsBox.setCurrentText(
            maf.options.get('dublast.useLights', "Default Lighting")
        )
        self.displayTexturesBox.setChecked(
            maf.options.get('dublast.displayTextures', 1) == 1
        )
        self.displayShadowsBox.setChecked(
            maf.options.get('dublast.displayShadows', 1) == 1
        )
        self.aoBox.setChecked(
            maf.options.get('dublast.ao', 1) == 1
        )
        self.aaBox.setChecked(
            maf.options.get('dublast.aa', 1) == 1
        )
        self.onlyPolyBox.setChecked(
            maf.options.get('dublast.onlyPoly', 1) == 1
        )
        self.motionTrailBox.setChecked(
            maf.options.get('dublast.motionTrail', 0) == 1
        )
        self.imagePlaneBox.setChecked(
            maf.options.get('dublast.imagePlane', 0) == 1
        )
        self.showHudBox.setChecked(
            maf.options.get('dublast.showHud', 1) == 1
        )
        folder = maf.options.get('dublast.folder', "")
        if not QFileInfo.exists(folder):
            folder = ""
        self.folderEdit.setText( folder )
        self._updateRenderer()

    def _saveSettings(self):
        maf.options.save('dublast.size', self.sizeEdit.value())
        maf.options.save('dublast.displayAppearance', self.displayAppearenceBox.currentText())
        maf.options.save('dublast.useLights', self.useLightsBox.currentText())
        maf.options.save('dublast.displayTextures', 1 if self.displayTexturesBox.isChecked() else 0)
        maf.options.save('dublast.displayShadows', 1 if self.displayShadowsBox.isChecked() else 0)
        maf.options.save('dublast.ao', 1 if self.aoBox.isChecked() else 0)
        maf.options.save('dublast.aa', 1 if self.aaBox.isChecked() else 0)
        maf.options.save('dublast.onlyPoly',1 if self.onlyPolyBox.isChecked() else 0)
        maf.options.save('dublast.motionTrail', 1 if self.motionTrailBox.isChecked() else 0)
        maf.options.save('dublast.imagePlane', 1 if self.imagePlaneBox.isChecked() else 0)
        maf.options.save('dublast.showHud', 1 if self.showHudBox.isChecked() else 0)
        maf.options.save('dublast.folder', self.folderEdit.text())

    def _setPlayer(self):
        current = getVideoPlayer()
        new = QFileDialog.getOpenFileName(self, "Select the video player", os.path.dirname(current))[0]
        if QFileInfo.exists(new):
            maf.options.save('dublast.videoPlayer', new)

    Slot()
    def _updateLightsBox(self, index):
        self.useLightsBox.setEnabled( index < 2 )

    Slot()
    def _thumbnail(self):
        self.done(2)

    def _loadCameras(self):
        maf.ui.update_cam_combobox(self.cameraBox)

    Slot()
    def _browseFolder(self):
        f = QFileDialog.getExistingDirectory(self, "Select output folder", self.folderEdit.text() )
        if QFileInfo.exists(f):
            self.folderEdit.setText(f)

    def comment(self):
        """Returns the comment added by the user"""
        return self.commentEdit.text()

    def camera(self):
        """Returns the selected camera"""
        return self.cameraBox.currentData()

    def getSize(self):
        """Returns the size %"""
        return self.sizeEdit.value() / 100.0

    def showHUD(self):
        """Returns True if the HUD has to be shown"""
        return self.showHudBox.isChecked()

    def thumbnail(self):
        """Do we have to create a thumbnail?"""
        return self._thumbnailBox.isChecked()

    def playblast(self):
        """Do we have to create a playblast?"""
        return self._playblastBox.isChecked()

    def folder(self):
        """The output folder (empty string for auto)"""
        return self.folderEdit.text()

    def fileName(self):
        """The filename, including the comment (empty string for auto)"""
        fn = self.filenameEdit.text()
        if fn == '':
            return ''
        if fn[-1] != "_":
            fn = fn + "_"
        fn = fn + self.commentEdit.text()
        return fn

    Slot()
    def hideRenderer(self):
        """Hides the Maya viewport used to capture the preview"""
        cmds.window( self.pbWin, visible=False, edit=True)

    def setWindowSize(self):
        """Changes the size of the viewport used to capture the preview"""
        s = self.getSize()
        w = cmds.getAttr("defaultResolution.width") * s - 4
        h = cmds.getAttr("defaultResolution.height") * s - 23
        cmds.windowPref(self.pbWin, maximized=False, edit=True)
        cmds.window(self.pbWin, width=w, height=h, edit=True)
        cmds.refresh(cv=True)

if __name__ == '__main__':
    dialog = PreviewDialog( maf.ui.getMayaWindow() )
    ok = dialog.exec_()
    print(ok)
