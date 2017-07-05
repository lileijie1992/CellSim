from PyQt5.QtCore import (QUrl, Qt)
from PyQt5.QtWidgets import (QAction,
                            QApplication, 
                            QDialog, 
                            QLabel, 
                            QTextBrowser, 
                            QToolBar, 
                            QVBoxLayout)
from PyQt5.QtGui import (QKeySequence, QIcon,QFont)
import qrc_resource


class HelpForm(QDialog):
    def __init__(self,  page,  parent=None):
        super(HelpForm, self).__init__(parent)
        self.setWindowTitle("CellSim Help")
        self.setAttribute(Qt.WA_DeleteOnClose)
        # actions
        backAction = QAction(QIcon(":/back.png"), "&Back", self)
        backAction.setShortcut(QKeySequence.Back)
        homeAction = QAction(QIcon(":/home.png"), "&Home", self)
        homeAction.setShortcut("Home")
        self.pageLabel = QLabel()
        #toolbar
        toolBar = QToolBar()
        toolBar.addAction(backAction)
        toolBar.addAction(homeAction)
        toolBar.addWidget(self.pageLabel)
        self.pageLabel.setFont(QFont("Roman times", 12, QFont.Bold))
        self.textBrowser = QTextBrowser()
        # layout
        layout = QVBoxLayout()
        layout.addWidget(toolBar)
        layout.addWidget(self.textBrowser, 1)
        self.setLayout(layout)
        # signals and slots
        backAction.triggered.connect(self.textBrowser.backward)
        homeAction.triggered.connect(self.textBrowser.home)
        self.textBrowser.sourceChanged.connect(self.updatePageTitle)
        self.textBrowser.setSearchPaths([":/help"])
        self.textBrowser.setSource(QUrl(page))
        self.resize(400, 600)

    def updatePageTitle(self):
        self.pageLabel.setText( "  " + self.textBrowser.documentTitle())

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = HelpForm("index.html")
    form.show()
    app.exec_()
