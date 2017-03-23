import os
import sys
import platform
import traceback
import re
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import loadfiledlg
import figuretooldlg
import qrc_resource
__version__ = "2.0.1"


class MainWindow(QMainWindow):
    global normalcellnet,normalcellname,cancercellnet,cancercellname
    normalcellnet = []
    normalcellname = []
    netlists = os.listdir("./data/net/fantom_allunique_normal_genelist/")
    for netlist in netlists:
        f = open("./data/net/fantom_allunique_normal_genelist/" + netlist, "r")
        lines = f.readlines()
        f.close()
        normalcellname.append(netlist.replace('.txt', ''))
        lines2 = []
        for line in lines:
            lines2.append(line.strip('\n'))
        normalcellnet.append(lines2)
    cancercellnet = []
    cancercellname = []
    netlists = os.listdir("./data/net/fantom_allunique_cancer_genelist/")
    for netlist in netlists:
        f = open("./data/net/fantom_allunique_cancer_genelist/" + netlist, "r")
        lines = f.readlines()
        f.close()
        cancercellname.append(netlist.replace('.txt', ''))
        lines2 = []
        for line in lines:
            lines2.append(line.strip('\n'))
        cancercellnet.append(lines2)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.line1 = QLineEdit()
        self.line2 = QLineEdit()
        self.geneline = QLineEdit()
        self.line1.setMaximumWidth(400)
        self.line2.setMaximumWidth(400)
        self.geneline.setMaximumWidth(400)
        self.label1 = QLabel(" Cell type A:")
        self.label2 = QLabel(" Cell type B:")
        self.genelabel = QLabel(" Gene list:")
        self.button = QPushButton("calculate")
        self.genebutton1 = QPushButton("Normal Cell calculate")
        self.genebutton2 = QPushButton("Cancer Cell calculate")
        self.imagelabel = QLabel()
        self.table = QTableWidget(1001, 4)
        self.table.setMouseTracking(True)
        self.table.setHorizontalHeaderLabels(['Celltype A', 'Celltype B', 'Simlarity', 'Common network'])
        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tab = QTabWidget()
        self.tab.setMovable(False)
        self.tab.setTabsClosable(False)
        # signals connect slot
        self.button.clicked.connect(self.Search)
        self.genebutton1.clicked.connect(lambda: self.geneSearch(1))
        self.genebutton2.clicked.connect(lambda: self.geneSearch(2))
        self.line1.returnPressed.connect(self.button.click)
        self.line2.returnPressed.connect(self.button.click)
        self.tab.tabCloseRequested.connect(self.tab.removeTab)
        self.tab.tabBarDoubleClicked.connect(self.tab.removeTab)

        self.setCentralWidget(self.tab)
        self.setWindowIcon(QIcon(":/icon.png"))
        self.setWindowIconText("Cell Similarity")
        self.setWindowTitle("CellSim")
        QTimer.singleShot(0, self.loadInitialFile)
        self.passcolor = []
        self.RDTable = []
        self.canvasdic = {'a': 2}
        self.axdic = {'a': 2}
        self.testlinedic = {'a': 2}
        self.anglesdic = {'a': 2}
        self.datadic = {'a': 2}
        self.xaxislabeldic = {'a': 2}
        self.logDockWidget = QDockWidget()
        self.filename = None

        # statusbar
        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel |
                                     QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 5000)

        # menu
        fileOpenAction = self.createAction("&Open...",
                                           self.fileOpen,
                                           QKeySequence.Open,
                                           "fileopen",
                                           "Open an existing file")
        fileSaveAsAction = self.createAction("Save &Similarity",
                                             self.fileSaveAs,
                                             icon="filesaveas",
                                             tip="Save the file using a new name")
        fileSaveDockAction = self.createAction("Save &Common network",
                                               self.fileSaveDock,
                                               icon="filesaved",
                                               tip="Save the Dockwidget data")
        fileSaveImageAction = self.createAction("Save &Figures",
                                                self.fileSaveImage,
                                                icon="filesavep",
                                                tip="Save the Figure")
        fileQuitAction = self.createAction("&Quit",  # 退出
                                           self.close,
                                           "Ctrl+Q",
                                           "filequit",
                                           "Close the application")
        demoaAction = self.createAction("&Cell type Demo",
                                        self.demoa)
        demobAction = self.createAction("&Gene list Demo",
                                        self.demob)  # tip="Examples for which cell type the genelist belongs to"
        figuretoolAction = self.createAction('&Figure tool',
                                             self.figuretool,
                                             icon="figuretool")
        helpAboutAction = self.createAction("&About CelltypeSim",
                                            self.helpAbout,
                                            icon="about")
        helpHelpAction = self.createAction("&Help",
                                           self.helpHelp,
                                           icon="help")
        self.fileMenu = self.menuBar().addMenu("&File")
        self.saveMenu = self.fileMenu.addMenu(QIcon(":/filesave.png"), "&Save")
        self.saveMenu.addActions((fileSaveAsAction,
                                  fileSaveDockAction,
                                  fileSaveImageAction))
        self.fileMenu.addAction(fileOpenAction)
        self.fileMenu.addMenu(self.saveMenu)
        self.fileMenu.addAction(fileQuitAction)
        self.demoMenu = self.menuBar().addMenu("&Demo")
        self.demoMenu.addActions((demoaAction, demobAction))
        self.FTMenu = self.menuBar().addMenu("&Tool")
        self.FTMenu.addAction(figuretoolAction)
        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addActions((helpAboutAction,
                                  helpHelpAction))

        # Tool Bar
        fileToolBar = self.addToolBar("File")
        fileToolBar.setObjectName("FileToolBar")
        fileToolBar.addActions((fileOpenAction,
                                fileSaveAsAction,
                                figuretoolAction))
        searchToolBar = self.addToolBar("Search")
        searchToolBar.setObjectName("SearchToolBar")
        searchToolBar.addWidget(self.label1)
        searchToolBar.addWidget(self.line1)
        searchToolBar.addWidget(self.label2)
        searchToolBar.addWidget(self.line2)
        searchToolBar.addWidget(self.button)
        genesearchTooBar = self.addToolBar("Gene")
        genesearchTooBar.setObjectName("GenesearchToolBar")
        genesearchTooBar.addWidget(self.genelabel)
        genesearchTooBar.addWidget(self.geneline)
        genesearchTooBar.addWidget(self.genebutton1)
        genesearchTooBar.addWidget(QLabel(' '))
        genesearchTooBar.addWidget(self.genebutton2)
        self.tab.addTab(self.imagelabel, 'Cells_Similarity')
        self.setMinimumSize(1000, 600)
        self.showImage()

    def fileOpen(self):
        try:
            February = loadfiledlg.Loadfiledlg(self)
            if February.exec_():
                january = February.getdata()
                if january[2] == 0:
                    self.Search(january[0:2])
                else:
                    self.Search(january[0:2])
                    self.geneSearch(n=january[3], str_=january[2])
        except:
            pass

    def fileSaveAs(self):
        fname, format_ = QFileDialog.getSaveFileName(self,
                                                     "Cell Similarity - Save",
                                                     '.',
                                                     "All Files (*);;Csv Files (*.csv);;Text Files(*.txt)")
        if fname:
            if "." not in fname:
                fname += ".csv"
            current = self.tab.currentWidget()
            try:
                if type(current) is QTableWidget:
                    f = open(fname, "w")
                    f.writelines(",".join(['Celltype A', 'Celltype B', 'Simlarity', 'Common network'])+'\n')
                    for i in range(current.rowCount()):
                        sign = []
                        if current.item(i, 0):
                            for j in range(current.columnCount()):
                                item = current.item(i, j)
                                sign.append(item.text())
                            f.writelines(",".join(sign) + '\n')
                        else:
                            break
                    f.close()
                elif type(current) is QWidget:
                    f = open(fname, "w")
                    save_RDdata = self.RDTable[self.tab.currentIndex() - 1]
                    for line in save_RDdata:
                        f.writelines(str(line[0]) + "," + str(line[1]) + "," + line[2] + '\n')
                    f.close()
                else:
                    print('Please Click the Table You Want Save!')
            except:
                pass

    def fileSaveDock(self):
        fname, format_ = QFileDialog.getSaveFileName(self,
                                                     "Cell Similarity - Save Dock Data",
                                                     '.',
                                                     "All Files (*);;Csv Files (*.csv);;Text Files(*.txt)")
        dockwidget_current = self.logDockWidget.focusWidget()
        if fname:
            if "." not in fname:
                fname += ".csv"
        try:
            if type(dockwidget_current) is QTableWidget:
                f = open(fname, "w")
                f.writelines(",".join(['Transcription Factor', 'Gene', 'Score']) + '\n')
                for i in range(dockwidget_current.rowCount()):
                    sign = []
                    for j in range(dockwidget_current.columnCount()):
                        item = dockwidget_current.item(i, j)
                        if type(item) is QTableWidgetItem:
                            sign.append(item.text())
                        else:
                            break
                    f.writelines(",".join(sign) + '\n')
                f.close()
            else:
                QMessageBox.about(self, "Error Message",
                                  """<b>Error: </b> Dock data is empty!
                                  <p>Please open a common network.""")
        except Exception as e:  #
            QMessageBox.about(self, "Error Message",
                              """<b>Error: </b>{0}.
                              <p><div style="color:white;">____</div>Fail to read the cell name.
                              <p><div style="color:white;">____</div>Please use the cell names coincided with Cell Ontology (<a href="www.obofoundry.org/ontology/cl.html">Visit Now</a>)
                              and use a comma as the separator.""".format(e))

    def fileSaveImage(self):
        fname, format_ = QFileDialog.getSaveFileName(self,
                                                     "Cell Similarity - Save Figure",
                                                     '.',
                                                     "All Files (*);;PNG Files(*.png);;PDF Files(*.pdf)")
        try:
            if fname:
                if "." not in fname:
                    fname += ".png"
                self.mapa.print_figure(fname, dpi=300)
                self.mapb.print_figure(fname.replace('.', '(1).'), dpi=300)
        except:
            traceback.print_exc()

    def addRecentFile(self, fname):
        if fname is None:
            return
        if not self.recentFiles or not fname in self.recentFiles:
            self.recentFiles.insert(0, fname)
            while len(self.recentFiles) > 9:
                self.recentFiles.takeLast()

    def loadInitialFile(self):
        settings = QSettings()
        fname = str(settings.value("LastFile"))
        if fname and QFile.exists(fname):
            self.loadFile(fname)

    def demoa(self):
        self.line1.setText('somatic stem cell,neuronal stem cell,osteoblast')
        self.line2.setText('stem cell,myoblast')
        self.Search()

    def demob(self):
        self.geneline.setText('CAD,DCPS,HTR2B,KIF14,KRTAP3-3,LARP6,PDGFC,PDK1,SPINK13,ADCY9,ALDH1A3')
        self.geneSearch(1)

    def figuretool(self):
        try:
            self.May = figuretooldlg.FigureTooldlg(self)
            self.May.show()
            self.May.titlesignal_a.connect(self.FTchangetitlea)
            self.May.linecolorsignal.connect(self.FTchangelinecolor)
            self.May.bigcolorsignal.connect(self.FTchangebigcolor)
            self.May.alphasignal.connect(self.FTchangealpha)
            self.May.labelsignal.connect(self.FTsetlabel)
            self.May.xaxis_text_signal.connect(self.FTsetxaxislabel)
            self.May.xaxis_index_signal.connect(self.FTselect)
        except:
            traceback.print_exc()

    def FTchangetitlea(self, a):
        sign2 = 'c' + str(int(self.tab.currentIndex()) * 2 + int(self.May.chooseabfunction()) - 1)
        try:
            self.axdic[sign2].set_title(a)
            self.canvasdic[sign2].draw()
        except:
            pass

    def FTchangelinecolor(self, color):
        sign2 = 'c' + str(int(self.tab.currentIndex()) * 2 + int(self.May.chooseabfunction()) - 1)
        try:
            self.axdic[sign2].lines[0].set_color(color.getRgbF())
            self.canvasdic[sign2].draw()
        except:
            pass

    def FTchangebigcolor(self, color):
        try:
            self.passcolor = color.getRgbF()
            sign2 = 'c' + str(int(self.tab.currentIndex()) * 2 + int(self.May.chooseabfunction()) - 1)
            self.axdic[sign2].fill(self.anglesdic[sign2], self.datadic[sign2], facecolor=color.getRgbF())
            self.canvasdic[sign2].draw()
        except:
            pass

    def FTchangealpha(self, a):
        try:
            if len(self.passcolor):
                sign2 = 'c' + str(int(self.tab.currentIndex()) * 2 + int(self.May.chooseabfunction()) - 1)
                self.axdic[sign2].fill(self.anglesdic[sign2], self.datadic[sign2], facecolor='w', alpha=1)
                self.axdic[sign2].fill(self.anglesdic[sign2], self.datadic[sign2], facecolor=self.passcolor, alpha=a)
                self.canvasdic[sign2].draw()
            else:
                sign2 = 'c' + str(int(self.tab.currentIndex()) * 2 + int(self.May.chooseabfunction()) - 1)
                self.axdic[sign2].fill(self.anglesdic[sign2], self.datadic[sign2], facecolor='w', alpha=1)
                self.axdic[sign2].fill(self.anglesdic[sign2], self.datadic[sign2], facecolor='b', alpha=a)
                self.canvasdic[sign2].draw()
        except:
            pass

    def FTsetlabel(self, n):
        sign2 = 'c' + str(int(self.tab.currentIndex()) * 2 + int(self.May.chooseabfunction()) - 1)
        try:
            if self.May.chooseabfunction() == 1:
                for i in range(0, 6):
                    self.testlinedic[sign2][i].set_visible(bool(n))
            else:
                for i in range(0, 6):
                    self.testlinedic[sign2][i].set_visible(bool(n))
            self.canvasdic[sign2].draw()
        except:
            pass

    def FTsetxaxislabel(self, index, text):
        sign2 = 'c' + str(int(self.tab.currentIndex()) * 2 + int(self.May.chooseabfunction()) - 1)
        try:
            self.xaxislabeldic[sign2][index-1] = text
            self.axdic[sign2].set_xticklabels(self.xaxislabeldic[sign2])
            self.canvasdic[sign2].draw()
        except:
            pass

    def FTselect(self, index):
        sign2 = 'c' + str(int(self.tab.currentIndex()) * 2 + int(self.May.chooseabfunction()) - 1)
        try:
            _text = self.xaxislabeldic[sign2][index-1]
            self.May.xaxis_selection(_text)
        except:
            pass

    def ShowTable(self, showdata):
        self.RDTable.append(1)
        self.sign = QTableWidget(1001, 4)
        self.sign.setHorizontalHeaderLabels(['Celltype A', 'Celltype B', 'Simlarity', 'Common network'])
        self.sign.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sign.setSortingEnabled(False)
        self.sign.setMouseTracking(True)
        showdata = [x for x in showdata if showdata.count(x) == 1]
        for k in range(0, min(len(showdata), 1001)):
            showdata[k][2] = float('%0.4f' % showdata[k][2])
            if int(showdata[k][2]) is not 1:
                for i in range(0, 3):
                    item = QTableWidgetItem(str(showdata[k][i]))
                    self.sign.setItem(k, i, item)
                if showdata[k][3] + showdata[k][4] is not 0:
                    if min(showdata[k][3], showdata[k][4]) is not 0:
                        item2 = QTableWidgetItem('Common Network')
                    elif showdata[k][3] is not 0:
                        item2 = QTableWidgetItem('{} Network'.format(showdata[k][0]))
                    else:
                        item2 = QTableWidgetItem('{} Network'.format(showdata[k][1]))
                    self.sign.setItem(k, 3, item2)
                else:
                    item2 = QTableWidgetItem(' No Network')
                    self.sign.setItem(k, 3, item2)
        self.sign.resizeColumnsToContents()
        self.sign.setSortingEnabled(True)
        self.tab.addTab(self.sign, '{} Cells_Similarity'.format(self.tab.count()))
        self.tab.setCurrentWidget(self.sign)
        self.sign.cellDoubleClicked.connect(self.myslot)

    def myslot(self, int1, int2):
        if int2 is 3:
            f = open("./data/normalcell/normal_fantom_onlyclname.csv", 'r')
            lines = f.readline()
            f.close()
            lines = lines.strip('\n')
            data = lines.split(',')
            word = self.sign.item(int1, int2).text()
            if word == 'Common Network':
                a = data.index(self.sign.item(int1, 0).text())
                b = data.index(self.sign.item(int1, 1).text())
                c = self.sign.item(int1, 0).text() + ' & ' + self.sign.item(int1, 1).text() + ' Network'
            elif word != ' No Network':
                a = data.index(word.replace(' Network', ''))
                b = -1
                c = word
            else:
                pass
            self.showcommonnet(min(a, b) + 1, max(a, b) + 1, c)
        else:
            pass

    def showcommonnet(self, _int1, _int2, name):
        try:
            net1dic = {'a': 2}
            net = [1]
            if _int1 == 0:
                _str = str(_int2) + '.txt'
                f = open('./data/normalcell/normalcellcommon_withweight/' + _str, "r")
                lines = f.readlines()
                f.close()
                for line in lines:
                    line = line.strip('\n')
                    L = line.split(' ')
                    net.append(L)
            else:
                _str1 = str(_int1) + '.txt'
                _str2 = str(_int2) + '.txt'
                f = open('./data/normalcell/normalcellcommon_withweight/' + _str1, "r")
                lines = f.readlines()
                f.close()
                for line in lines:
                    line = line.strip('\n')
                    L = line.split(' ')
                    net1dic[L[0]+L[1]] = L[2]
                f = open('./data/normalcell/normalcellcommon_withweight/' + _str2, "r")
                lines = f.readlines()
                f.close()
                for line in lines:
                    line = line.strip('\n')
                    L = line.split(' ')
                    together = L[0]+L[1]
                    try:
                        _num = net1dic[together]
                        net.append([L[0], L[1], (float(_num) + float(L[2]))/2])
                    except:
                        pass
            self.logtable = QTableWidget(10000, 3)
            self.logtable.setHorizontalHeaderLabels(['Transcription Factor', 'Gene', 'Score'])
            self.logtable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.logtable.setSortingEnabled(False)
            self.logtable.setMouseTracking(True)
            for i in range(0, min(len(net), 10000)):
                net[i+1][2] = float('%0.4f' % float(net[i+1][2]))
                for j in range(0, 3):
                    item = QTableWidgetItem(str(net[i + 1][j]))
                    self.logtable.setItem(i, j, item)
            self.logtable.resizeColumnsToContents()
            self.logtable.setSortingEnabled(True)
            self.logtable.sortItems(2, True)
            self.logtable.setMinimumWidth(340)
            self.logDockWidget = QDockWidget(name, self)
            self.logDockWidget.setObjectName("LogDockWidget")
            self.logDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |
                                               Qt.RightDockWidgetArea)
            self.logDockWidget.setWidget(self.logtable)
            self.addDockWidget(Qt.RightDockWidgetArea, self.logDockWidget)
        except:
            traceback.print_exc()

    def geneSearch(self, n, str_=None):
        try:
            if n == 1:
                global normalcellname, normalcellnet
                titlename = 'Normal Cell Result'
                name = normalcellname
                netall = normalcellnet
            else:
                global cancercellname, cancercellnet
                titlename = 'Cancer Cell Result'
                name = cancercellname
                netall = cancercellnet
            genelist = self.geneline.text()
            if str_:
                genelist = ",".join(str_)
            genelist = genelist.split(',')
            genelistup = []
            for _list in genelist:
                genelistup.append(_list.upper())
            global radaralldata
            radaralldata = []
            for i in range(0, len(netall)):
                commonnumber = len(set(genelistup).intersection(set(netall[i])))
                radaralldata.append([commonnumber / len(netall[i]), commonnumber / len(genelistup),
                                     name[i]])
            radaralldata.sort(reverse=True, key=lambda x: x[0])
            self.RDTable.append(radaralldata)
            self.mapa = self.RDshow(radaralldata, 0, self.tab.count())
            self.mapb = self.RDshow(radaralldata, 1, self.tab.count())
            self.genetable = QTableWidget(400, 3)
            self.genetable.setMaximumWidth(1000)
            self.genetable.setHorizontalHeaderLabels(['Percent of Cell Type', 'Percent of Query Gene list', 'Cell Type'])
            self.genetable.setSortingEnabled(False)
            self.genetable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            for i in range(0, len(radaralldata)):
                radaralldata[i][0] = float('%0.4f' % radaralldata[i][0])
                radaralldata[i][1] = float('%0.4f' % radaralldata[i][1])
                item = QTableWidgetItem(str(radaralldata[i][0]))
                self.genetable.setItem(i, 0, item)
                item = QTableWidgetItem(str(radaralldata[i][1]))
                self.genetable.setItem(i, 1, item)
                item = QTableWidgetItem(str(radaralldata[i][2]))
                self.genetable.setItem(i, 2, item)
            self.genetable.setSortingEnabled(True)
            self.genetable.resizeColumnsToContents()
            self.mainmap_widget = QWidget(self)
            ll = QVBoxLayout(self.mainmap_widget)
            ll.addWidget(self.mapa)
            ll.addWidget(self.mapb)
            self.main_widget = QWidget(self)
            l = QHBoxLayout(self.main_widget)
            l.addWidget(self.mainmap_widget)
            l.addWidget(self.genetable)
            self.tab.addTab(self.main_widget, '{} '.format(self.tab.count()) + titlename)
            self.tab.setCurrentWidget(self.main_widget)
        except:
            traceback.print_exc()

    def RDshow(self, radaralldata, n, tabnum):
        try:
            _label = []
            genedata = []
            for i in range(0, 6):
                wholename = radaralldata[i][2]
                separatename = ''
                lines = wholename.split(' ')
                for line in lines:
                    if line.isalpha:
                        separatename = separatename + line[0].upper()
                    else:
                        separatename = separatename + line
                _label.append(separatename)
                genedata.append(radaralldata[i][n])
            _label[3] = '       ' + _label[3] + '                    '
            _label[0] = '          ' + _label[0]
            dataLength = 6
            angles = np.linspace(0, 2 * np.pi, dataLength, endpoint=False)
            data = np.concatenate((genedata, [genedata[0]]))
            angles = np.concatenate((angles, [angles[0]]))
            self.fig = pyplot.figure()
            sign = 'c' + str(tabnum * 2 + n)
            self.xaxislabeldic[sign] = np.array(_label)
            self.canvasdic[sign] = FigureCanvas(self.fig)
            self.ax = self.fig.add_subplot(111, polar=True)
            self.ax.set_yticklabels([])
            self.ax.plot(angles, data, 'bo-', linewidth=2)
            self.testline = list(range(6))
            if data[0] == 1:
                self.testline[0] = pyplot.text(angles[0], data[0], '%0.2f' % data[0], ha='right', va='top', fontsize=8,
                                            fontproperties="Times New RoMan")
            else:
                self.testline[0] = pyplot.text(angles[0], data[0], '%0.2f' % data[0], ha='left', va='top', fontsize=8,
                                            fontproperties="Times New RoMan")
            self.testline[3] = pyplot.text(angles[3], data[3] + 0.05, '%0.2f' % data[3], ha='right', va='center',
                                        fontsize=8, fontproperties="Times New RoMan")
            self.testline[4] = pyplot.text(angles[4], data[4] + 0.05, '%0.2f' % data[4], ha='center', va='top',
                                        fontsize=8, fontproperties="Times New RoMan")
            self.testline[5] = pyplot.text(angles[5], data[5] + 0.05, '%0.2f' % data[5], ha='left', va='top',
                                        fontsize=8, fontproperties="Times New RoMan")
            for a in [1, 2]:
                if float('%0.2f' % data[a]) != 0:
                    self.testline[a] = pyplot.text(angles[a], data[a] + 0.05, s='%0.2f' % data[a], ha='center',
                                                va='bottom', fontsize=8, fontproperties="Times New RoMan")
            self.testlinedic[sign] = self.testline
            self.anglesdic[sign] = angles
            self.datadic[sign] = data
            self.ax.fill(angles, data, facecolor='b', alpha=0.5)
            self.ax.set_thetagrids(angles * 180 / np.pi, self.xaxislabeldic[sign], frac=1.1, fontsize=9,
                                   fontproperties="Times New RoMan")
            self.ax.set_title("{} Radar Chart".format(['Net Map', 'Gene List Map'][n]), va='bottom', fontsize=14,
                              fontproperties="Times New RoMan")
            self.ax.set_rlim(0, 1)
            self.fig.set_facecolor("#ffffff")
            self.ax.grid(True)
            self.axdic[sign] = self.ax
            self.canvasdic[sign].draw()
            return self.canvasdic[sign]
        except:
            traceback.print_exc()

    def Search(self, str_=None):
        global normalcellname
        searchstr1 = self.line1.text()
        searchstr2 = self.line2.text()
        data = self.getdata()
        cellname = data[0]
        if str_:
            if str_[0]:
                searchstr1 = ",".join(str_[0])
            if str_[1]:
                searchstr2 = ",".join(str_[1])
        if len(searchstr1) and len(searchstr2):
            showdata = []
            try:
                searchname1 = self.strnormalize(searchstr1)
                searchname2 = self.strnormalize(searchstr2)
                for i in range(0, len(searchname1)):
                    index1 = cellname.index(searchname1[i])
                    for j in range(0, len(searchname2)):
                        index2 = cellname.index(searchname2[j])
                        showdata.append([searchname1[i], searchname2[j], float(data[index1 + 1][index2 + 1]),
                                         int(data[index1 + 1][0]), int(data[index2 + 1][0])])
                if len(showdata[0]) is not 1:
                    showdata.sort(reverse=True, key=lambda x: x[2])
                self.ShowTable(showdata)
            except Exception as e:
                traceback.print_exc()
                QMessageBox.about(self, "Error Message",
                                  """<b>Error: </b>{0}.
                                  <p><div style="color:white;">____</div>Fail to read the cell name.
                                  <p><div style="color:white;">____</div>Please use the cell names coincided with Cell Ontology (<a href="www.obofoundry.org/ontology/cl.html">Visit Now</a>)
                                  and use a comma as the separator.""".format(e))
        elif len(searchstr1) or len(searchstr2):
            searchname = searchstr1 + searchstr2
            try:
                showdata = []
                searchname = self.strnormalize(searchname)
                if len(searchname) is 1:
                    searchname = searchname[0]
                    _index = cellname.index(searchname)
                    similarity = data[_index + 1][1:]
                    for i in range(0, len(similarity)):
                        showdata.append([searchname, cellname[i], float(similarity[i]), int(data[_index + 1][0]),
                                         int(data[i + 1][0])])
                    if len(showdata[0]) is not 1:
                        showdata.sort(reverse=True, key=lambda x: x[2])  # 这个可以把整个序列排序，跟着变的
                    self.ShowTable(showdata)
                else:
                    for i in range(0, len(searchname) - 1):
                        for j in range(i + 1, len(searchname)):
                            _index1 = cellname.index(searchname[i])
                            _index2 = cellname.index(searchname[j])
                            showdata.append([searchname[i], searchname[j], float(data[_index1 + 1][_index2 + 1])])
                    if len(showdata[0]) is not 1:
                        showdata.sort(reverse=True, key=lambda x: x[2])
                    self.ShowTable(showdata)
            except Exception as e:
                traceback.print_exc()
                QMessageBox.about(self, "Error Message",
                                  """<b>Error: </b>{0}.
                                  <p><div style="color:white;">____</div>Fail to read the cell name.
                                  <p><div style="color:white;">____</div>Please use the cell names coincided with Cell Ontology (<a href="www.obofoundry.org/ontology/cl.html">Visit Now</a>)
                                  and use a comma as the separator.""".format(e))
        else:
            return

    def strnormalize(self, _str):
        _str = re.sub('[^A-Za-z0-9-,./ ]', '', _str)
        namelist = []
        lists = set(_str.split(','))
        for list2 in lists:
            if list2 is '' or list2 is ' ':
                continue
            elif list2[-1].isspace():
                namelist.append(list2[0:len(list2) - 1])
            elif list2[0].isspace():
                namelist.append(list2[1:])
            else:
                namelist.append(list2)
        return namelist

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{0}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def helpAbout(self):
        QMessageBox.about(self, "About CellSim",
                          """<b>CellSim</b> v {0}
                          <p>Copyright &copy; ~~~.
                          <p>This application can be used to find the similarity between different cell type.
                          <p>Python {1} - Qt {2} - PyQt {3} on {4}""".format(
                              __version__, platform.python_version(),
                              QT_VERSION_STR, PYQT_VERSION_STR,
                              platform.system()))

    def helpHelp(self):
        QMessageBox.about(self, "CellSim Help",
                          """<p>&nbsp; &nbsp;The <b>Cellsim</b> program provides cell type similarity calculation.</p>
                             <p>&nbsp; &nbsp;The <font color="#0000FF">File</font> menu is used to load files and save current data
                              (including the similarity between cell types, common networks, and figures).</p>
                             <p>&nbsp; &nbsp;The <font color="#0000FF">Demo</font> menu offers two demos.</p>
                             <p>&nbsp; &nbsp;The <font color="#0000FF">Tool</font> menu offers a tool to edit the figure.</p>
                             <p>&nbsp; &nbsp;All the most commonly used functions are also available on the
                             toolbar. The toolbar provides an easy way of similarity calculation.</p>""")

    def showImage(self):
        d = QApplication.desktop()
        self.showMaximized()
        if d.width() > 1900:
            image = QImage("./images/workflow21.tif")
        elif d.width() > 1299:
            image = QImage("./images/workflow19.tif")
        else:
            image = QImage("./images/workflow15.tif")
        width = image.width()
        height = image.height()
        image2 = image.scaled(width, height, Qt.KeepAspectRatio)
        self.imagelabel.setPixmap(QPixmap.fromImage(image2))

    def getdata(self):
        data = [1]
        f = open("./data/sim_onlyhuman.txt", "r")
        lines = f.readlines()
        f.close()
        for line in lines:
            line = line.strip('\n')
            L = line.split(',')
            data.append(L)
        f = open("./data/onlyhuman_allcell_name.csv", 'r')
        lines = f.readline()
        f.close()
        lines = lines.strip('\n')
        data[0] = lines.split(',')
        return data


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Karma Ltd.")
    app.setOrganizationDomain("karma.au")
    app.setApplicationName("Image Changer")
    form = MainWindow()
    form.showMaximized()
    app.exec_()


main()
