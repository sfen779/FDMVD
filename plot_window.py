from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout,QComboBox, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal, QTime

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import os
import pandas as pd
import numpy as np



class PlotDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plot Window")
        self.setGeometry(100, 100, 800, 600)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        df = self.read_data()
        y = df['exe_time']
        x = df['len_F']+df['len_G']
        self.plot(x,y)

        self.button = QPushButton('Save Plot', self)
        self.button.clicked.connect(self.save_plot)
        

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def save_plot(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "",
                                                   "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", options=options)
        if file_name:
            # 保存图表
            self.canvas.figure.savefig(file_name)
            print(f"Saved: {file_name}")

    def read_data(self):
        current_directory = os.path.dirname(__file__)
        log_file_name = os.path.join(current_directory, "log.csv")
        df = pd.read_csv(log_file_name)
        return df

    def plot(self,x, y):
        ax = self.figure.add_subplot(111)
        ax.scatter(x, y, label = 'Execution time', color='r', s=25, marker="o")

        coeffcient = np.polyfit(x, y, deg=2)
        poly = np.poly1d(coeffcient)
        yfit = poly(x)
        # ax.plot(x, yfit, label = f"y={coeffcient[0]:.4f}x+{coeffcient[1]:.4f}", color='b')
        ax.set_title('Running time vs. input size')
        ax.set_xlabel('MVD + FD size')
        ax.set_ylabel('Running time (s)')
        self.canvas.draw()