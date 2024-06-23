from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout,QComboBox, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal, QTime, pyqtSlot

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from gen_data import gen_dependency_pandas
from read_data import read_text_data

import MVD_FD_alg_poly as Mf
import os
import csv

class RunWorkerV2(QThread):
    '''
    run the tests with thread
    
    '''
    finished = pyqtSignal(float)
    all_finished = pyqtSignal()
    str_pass = pyqtSignal(str)
    def __init__(self,test_cases, algo_name = "algorithm 1_poly"):
        super().__init__()

        self.currentExeTime = 0
        self.time_total = 0
        self.test_cases = test_cases
        self.algo_name = algo_name

    def run(self):
        print(f"data type of test_cases: {type(self.test_cases)}")
        #temp_dict = self.test_cases
        for test in self.test_cases.values():
            # print(f"Running test {test}")
            print(f"data type: {type(test)}")
            universe_str = test["universe"].split()
            X_str = test["X"].split()
            mvd_text = test["MVDs"]
            fd_text = test["FDs"]
            X = [int(x) for x in X_str]
            universe = [int(u) for u in universe_str]

            exe_time = self.run_test(fd_text, mvd_text, X, universe)

            self.finished.emit(exe_time)

            self.currentExeTime = exe_time
            self.time_total += exe_time

            len_universe = len(universe)
            len_X = len(X)
            len_F = len(fd_text)
            len_G = len(mvd_text)
            temp_str = f"Test case: |U| = {len_universe}, |X| = {len_X}, |F| = {len_F}, |G| = {len_G}"
            print(temp_str)
            self.str_pass.emit(temp_str)

            algorithm_name = self.algo_name
            current_directory = os.path.dirname(__file__)

            log_file_name = os.path.join(current_directory, "log_devtest.csv")

            if not os.path.exists(log_file_name):
                with open(log_file_name, "w", newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["algorithm_name", "len_universe", "len_X", "len_F", "len_G", "exe_time"])

            with open(log_file_name, "a", newline='') as file:
                writer = csv.writer(file)
                writer.writerow([algorithm_name, len_universe, len_X, len_F, len_G, exe_time])
                file.write(f"{algorithm_name},{len_universe},{len_X},{len_F},{len_G},{exe_time}\n")
        self.all_finished.emit()


    def run_test(self,fd_text, mvd_text, X, universe):
        
        F ,G = Mf.parse_dependencies(fd_text, mvd_text)
        start_time = QTime.currentTime()
        basis, closure = Mf.dep_basis(set(X), set(universe), G, F)
        end_time = QTime.currentTime()
        exe_time = start_time.msecsTo(end_time) / 1000
        # self.finished.emit(exe_time)
        print(f"Execution time: {exe_time} seconds")
        return exe_time

class GenWorker(QThread):
    '''
    Worker class to generate the test data with thread
    '''
    finished = pyqtSignal(float)
    def __init__(self, file_path, file_name, test_id, target_size, chunk_size, universe_size):
        super().__init__()
        self.file_path = file_path
        self.file_name = file_name
        self.test_id = test_id
        self.target_size = target_size
        self.chunk_size = chunk_size
        self.universe_size = universe_size

    def run(self):
        gen_file_path, gen_time = gen_dependency_pandas(self.file_path, self.file_name, self.test_id, self.target_size, self.chunk_size, self.universe_size)
        self.finished.emit(gen_time)

class RunWorker(QThread):
    '''
    run the tests with thread
    
    '''
    finished = pyqtSignal(float)
    def __init__(self, fd_text, mvd_text, X, universe):
        super().__init__()
        self.fd_text = fd_text
        self.mvd_text = mvd_text
        self.X = X
        self.universe = universe

    @pyqtSlot()
    def run_test(self):
        start_time = QTime.currentTime()
        F ,G = Mf.parse_dependencies(self.fd_text, self.mvd_text)
        basis, closure = Mf.dep_basis(set(self.X), set(self.universe), G, F)
        end_time = QTime.currentTime()
        exe_time = start_time.msecsTo(end_time) / 1000
        self.finished.emit(exe_time)
        print(f"Execution time: {exe_time} seconds")
        return exe_time
    

class LoadWorker(QThread):
    '''
    Worker class to load the massive data with thread
    
    '''
    finished = pyqtSignal(dict)
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        total_input_dict = read_text_data(self.file_path)
        self.finished.emit(total_input_dict)
