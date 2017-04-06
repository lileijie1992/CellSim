import traceback
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Loadfiledlg(QDialog):
    def __init__(self, parent=None):
        super(Loadfiledlg, self).__init__(parent)
        self.filename = None
        dir = (os.path.dirname(self.filename)
               if self.filename is not None else ".")
        fname, format_ = QFileDialog.getOpenFileName(self,
                                                     "Cellsim - Choose data",
                                                     dir,
                                                     "All Files (*);;Csv Files (*.csv);;Text Files(*.txt)")

        self.setWindowTitle("Load Data")
        Loadfiledlg.setFixedSize(self, 420, 460)
        f = open(fname, "r")
        lines = f.readlines()
        f.close()
        self.lines2 = []
        for line in lines:
            line = line.strip('\n')
            self.lines2.append(line.split(','))
        self.lines = [0]
        for i in range(len(self.lines2[1])):
            self.lines.append([x[i] for x in self.lines2])

        self.loadtabel = QTableWidget(len(self.lines2), len(self.lines2[1]))
        self.loadtabel.setSortingEnabled(False)
        self.loadtabel.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.loadtabel.setFixedSize(400, 200)
        self.loadtabel.verticalHeader().setVisible(False)
        for i in range(len(self.lines2)):
            for j in range(len(self.lines2[1])):
                item = QTableWidgetItem(str(self.lines2[i][j]))
                self.loadtabel.setItem(i, j, item)
        self.Box1 = QGroupBox("Cells Similarity")
        layout_b1 = QVBoxLayout()
        layout_b11 = QHBoxLayout()
        layout_b11.addWidget(QLabel('Cell List A'))
        layout_b11.addWidget(QLabel("  "))
        layout_b11.addWidget(QLabel("Cell List B"))
        layout_b1.addLayout(layout_b11)
        layout_b12 = QHBoxLayout()
        self.brushComboBox1 = QComboBox()
        self.brushComboBox2 = QComboBox()
        self.brushComboBox1.addItem('None')
        self.brushComboBox2.addItem('None')
        for i in range(len(self.lines2[1])):
            self.brushComboBox1.addItem("Colunm " + str(i + 1))
        self.brushComboBox1.activated.connect(self.Tableselect)
        for i in range(len(self.lines2[1])):
            self.brushComboBox2.addItem("Column " + str(i + 1))
        self.brushComboBox2.activated.connect(self.Tableselect)
        layout_b12.addWidget(self.brushComboBox1)
        layout_b12.addWidget(QLabel("         <=>"))
        layout_b12.addWidget(self.brushComboBox2)
        layout_b1.addLayout(layout_b12)
        self.Box1.setLayout(layout_b1)
        self.Box2 = QGroupBox("Cells Prediction")
        layout_b2 = QVBoxLayout()
        layout_b21 = QHBoxLayout()
        layout_b212 = QVBoxLayout()
        self.nradio = QRadioButton('Normal Cell')
        self.cradio = QRadioButton('Cancer Cell')
        layout_b212.addWidget(self.nradio)
        layout_b212.addWidget(self.cradio)
        layout_b21.addWidget(QLabel('Choose Search Type:'))
        layout_b21.addLayout(layout_b212)
        layout_b22 = QHBoxLayout()
        layout_b22.addWidget(QLabel('Gene List: '))
        self.brushComboBox3 = QComboBox()
        self.brushComboBox3.addItem('None')
        for i in range(len(self.lines2[1])):
            self.brushComboBox3.addItem("Colunm " + str(i + 1))
        self.brushComboBox3.activated.connect(self.Tableselect2)
        layout_b22.addWidget(self.brushComboBox3)
        layout_b2.addLayout(layout_b22)
        layout_b2.addLayout(layout_b21)
        self.Box2.setLayout(layout_b2)

        self.pushButton3 = QPushButton('OK')
        self.pushButton4 = QPushButton('Cancel')
        layout = QVBoxLayout()
        layout.addWidget(self.Box1)
        layout.addWidget(self.Box2)
        layout.addWidget(self.loadtabel)
        self.a = QWidget(self)
        layout2 = QHBoxLayout(self.a)
        layout2.addWidget(QLabel(''))
        layout2.addWidget(self.pushButton3)
        layout2.addWidget(self.pushButton4)
        layout.addWidget(self.a)
        layout.addStretch(1)
        self.setLayout(layout)
        self.pushButton3.clicked.connect(self.accept)
        self.pushButton4.clicked.connect(self.reject)

    def Tableselect(self, index):
        if index == 0:
            self.loadtabel.clearSelection()
        elif self.loadtabel.currentColumn() is not index - 1:
            self.loadtabel.setSelectionMode(QAbstractItemView.MultiSelection)
            self.loadtabel.selectColumn(index - 1)

    def Tableselect2(self, index):
        if index == 0:
            self.loadtabel.clearSelection()
        else:
            self.loadtabel.clearSelection()
            self.loadtabel.selectColumn(index - 1)

    def getdata(self):
        global out_list
        self.lines2.insert(0, 0)
        index1 = self.brushComboBox1.currentIndex()
        index2 = self.brushComboBox2.currentIndex()
        index3 = self.brushComboBox3.currentIndex()
        Radio_index = 0
        if self.nradio.isChecked():
            Radio_index = Radio_index + 1
        elif self.cradio.isChecked():
            Radio_index = Radio_index + 2
        out_list = [self.lines[index1], self.lines[index2], self.lines[index3], Radio_index]
        return out_list


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = Loadfiledlg()
    form.show()
    app.exec_()
