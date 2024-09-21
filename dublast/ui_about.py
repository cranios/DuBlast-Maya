# -*- coding: utf-8 -*-
"""The about dialog of the addon"""

from PySide6.QtWidgets import ( # pylint: disable=no-name-in-module,import-error
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton
)

from dublast.constants import VERSION, VENDOR, TOOL_NAME
from dublast.utils import donate

class AboutDialog(QDialog):
    """The about dialog"""

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        self.setWindowTitle("About " + TOOL_NAME)

        l = QVBoxLayout()
        l.setContentsMargins(6,6,6,6)
        l.setSpacing(6)
        self.setLayout(l)

        l.addWidget(QLabel( "<p><strong>About " + TOOL_NAME + "</strong> by " + VENDOR + "<br />"
            "<i>v" + VERSION + "</i></p>"
            "<p>Better Playblasts for Maya.<br>"
            "More info on <a href=\"https://rxlaboratory.org\">rxlaboratory.org</a></p>"
            
        ))
        l.addWidget(QLabel("<p>Licensed under the GNU General Public License v3</p>"
                          "<p>Please make a donation if you like this!</p>" ))

        self.donateButton = QPushButton("💟 Donate")
        l.addWidget(self.donateButton)

        self.donateButton.clicked.connect(donate)

if __name__ == "__main__":
    app = QApplication.instance() or QApplication()
    d = AboutDialog()
    d.exec_()
