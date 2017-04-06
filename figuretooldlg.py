import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import traceback


class FigureTooldlg(QDialog):
    titlesignal_a = pyqtSignal(str)
    linecolorsignal = pyqtSignal(QColor)
    bigcolorsignal = pyqtSignal(QColor)
    alphasignal = pyqtSignal(float)
    labelsignal = pyqtSignal(int)
    xaxis_index_signal = pyqtSignal(int)
    xaxis_text_signal = pyqtSignal(int, str)
    def __init__(self, parent=None):
        super(FigureTooldlg, self).__init__(parent)
        self.setWindowTitle("Figure Tool")
        self.setFixedSize(420, 300)
        GridLayout = QGridLayout()
        GridLayout.addWidget(QLabel("Title: "), 2, 0, 1, 1)
        self.line1 = QLineEdit("")
        GridLayout.addWidget(self.line1, 2, 1, 1, 2)
        GridLayout.addWidget(QLabel("Cell Name: "), 3, 0, 1, 1)
        self.xaxis_chooseindex = QComboBox()
        self.xaxis_chooseindex.addItem("1")
        self.xaxis_chooseindex.addItem("2")
        self.xaxis_chooseindex.addItem("3")
        self.xaxis_chooseindex.addItem("4")
        self.xaxis_chooseindex.addItem("5")
        self.xaxis_chooseindex.addItem("6")
        self.xaxisline = QLineEdit("")
        self.xaxisline.setFixedWidth(130)
        GridLayout.addWidget(self.xaxis_chooseindex, 3, 1, 1, 1)
        GridLayout.addWidget(self.xaxisline, 3, 2, 1, 1)
        self.xaxisline.textChanged.connect(self.xaxislabel_change)
        self.xaxis_chooseindex.activated.connect(self.chooseaxis_slot)
        GridLayout.addWidget(QLabel("Line Color:"), 4, 0, 1, 1)
        self.colorbutton = QPushButton("Color")
        self.colorbutton.clicked.connect(lambda: self.getColor(1))
        self.colorshow = QLabel()
        GridLayout.addWidget(self.colorshow, 4, 1, 1, 1)
        GridLayout.addWidget(self.colorbutton, 4, 2, 1, 1)
        GridLayout.addWidget(QLabel("Face Color:"), 5, 0, 1, 1)
        self.colorbutton2 = QPushButton("Color")
        self.colorbutton2.clicked.connect(lambda: self.getColor(0))
        self.colorshow2 = QLabel()
        GridLayout.addWidget(self.colorshow2, 5, 1, 1, 1)
        GridLayout.addWidget(self.colorbutton2, 5, 2, 1, 1)
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        GridLayout.addWidget(QLabel(" "), 9, 0, 1, 1)
        GridLayout.addWidget(self.okButton, 11, 1, 1, 1)
        GridLayout.addWidget(self.cancelButton, 11, 2, 1, 1)
        GridLayout.addWidget(QLabel("Show Data Label: "), 6, 0, 1, 1)
        self.label = QCheckBox(" ")
        GridLayout.addWidget(self.label, 6, 1, 1, 1)
        self.label.setChecked(True)
        GridLayout.addWidget(QLabel("Diaphaneity:"), 7, 0, 1, 1)
        self.transparencynum = QSpinBox()
        self.transparencynum.setRange(0, 100)
        GridLayout.addWidget(self.transparencynum, 7, 1, 1, 1)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setTickPosition(2)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self.transparencynum.setValue)
        self.transparencynum.valueChanged.connect(self.slider.setValue)
        GridLayout.addWidget(self.slider, 8, 1, 1, 2)
        self.chooseab = QComboBox()
        self.chooseab.addItem("Figure 1")
        self.chooseab.addItem("Figure 2")
        GridLayout.addWidget(QLabel("Choose a Figure: "), 0, 0, 1, 1)
        GridLayout.addWidget(self.chooseab, 0, 1, 1, 1)
        GridLayout.addWidget(QLabel(" "), 1, 1, 1, 1)
        self.setLayout(GridLayout)
        self.a = [1, 2]
        self.line1.textChanged.connect(self.emittitlesignal_a)
        self.slider.valueChanged.connect(self.emitalpha)
        self.label.clicked.connect(self.emitlabel)

    # signal
    def emittitlesignal_a(self, a):
        self.titlesignal_a.emit(a)

    def emitalpha(self):
        a = self.slider.value() / 100
        self.alphasignal.emit(a)

    def chooseabfunction(self):
        text = self.chooseab.currentText()
        return int(text[-1])

    def getColor(self, n):
        color = QColorDialog.getColor(Qt.black, self)
        try:
            if color.isValid():
                self.color = color
                if n:
                    pixmap = self._makePixmap(100, 4)
                    self.colorshow.setPixmap(pixmap)
                    self.linecolorsignal.emit(color)
                else:
                    pixmap = self._makePixmap(100, 30)
                    self.colorshow2.setPixmap(pixmap)
                    self.bigcolorsignal.emit(color)
        except:
            traceback.print_exc()

    def _makePixmap(self, width, height):
        pixmap = QPixmap(width, height)
        brush = QBrush(self.color)
        painter = QPainter(pixmap)
        painter.fillRect(pixmap.rect(), Qt.white)
        painter.fillRect(pixmap.rect(), brush)
        return pixmap

    def emitlabel(self):
        self.labelsignal.emit(self.label.checkState())

    def xaxislabel_change(self):
        _str = self.xaxisline.text()
        _index = int(self.xaxis_chooseindex.currentText())
        self.xaxis_text_signal.emit(_index, _str)

    def chooseaxis_slot(self):
        _index = int(self.xaxis_chooseindex.currentText())
        self.xaxis_index_signal.emit(_index)

    def xaxis_selection(self, _str):
        self.xaxisline.setText(_str)
        try:
            self.xaxisline.selectAll()
            self.xaxisline.setFocus()
        except:
            pass
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = FigureTooldlg()
    form.show()
    app.exec_()
