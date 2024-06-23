import sys
import time
import os
import csv
import random

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout,QComboBox, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal, QTime

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# import the implemented algorithms
# import MVD_alg_linear as Ml
# import MVD_alg_poly as Mp
import MVD_FD_alg_poly as Mf
# import algo_membership as Mm

from datetime import datetime

from thread_workers import GenWorker, RunWorker, LoadWorker, RunWorkerV2
from read_data import read_text_data
from gen_data import  generate_single_dependency, generate_dependencies_struct, gen_dependency_pandas
from plot_window import PlotDialog

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# def process_line(line, total_input_dict):




class MVDParser(QWidget):
    def __init__(self):
        super().__init__()
        self.saved_inputs_mvd = []  # Store parsed multivalued dependencies
        self.saved_inputs_fd = []  # Store parsed functional dependencies
        self.saved_strings = []  # Store additional string data
        self.worker = None
        self.len = 0
        self.initUI()
        
    
    def initUI(self):
        self.setWindowTitle('MVD and FD')
        self.setGeometry(1000, 200, 800, 600)  # Adjusted window size for better layout

        layout_total = QHBoxLayout()
        layout_gen = QVBoxLayout()
        layout = QVBoxLayout()


        self.combo = QComboBox(self)
        self.combo.addItem("algorithm 1_poly")
        self.combo.addItem("algorithm 2_linear")
        self.label = QLabel("Choose algorithm", self)
        layout.addWidget(self.label)
        layout.addWidget(self.combo)
        self.combo.activated[str].connect(self.onActivated)


        self.entry_universe = QLineEdit(self)
        self.Uni_label = QLabel("Universe of attributes:", self)
        self.entry_universe.setPlaceholderText("Universe of attributes, e.g., '0,1,2,3,4,5'")
        layout.addWidget(self.Uni_label)
        layout.addWidget(self.entry_universe)

        self.entry_X = QLineEdit(self)
        self.XY_label = QLabel("Dependency to test:", self)
        self.entry_X.setPlaceholderText("X->Y: the dependency to test, e.g., '0 -> 5'")
        layout.addWidget(self.XY_label)
        layout.addWidget(self.entry_X)


        self.entry_mvd = QLineEdit(self)
        self.G_label = QLabel("Known MVDs and FDs:", self)
        self.entry_mvd.setPlaceholderText("FUG : in form like 'FD:[2] -> [4];MVD:[0, 1] -> [2, 3];FD:[2] -> [5]'")
        layout.addWidget(self.G_label)
        layout.addWidget(self.entry_mvd)
        
        clipboard_button = QPushButton('Get input from Clipboard', self)
        clipboard_button.clicked.connect(self.get_from_clipboard)
        layout.addWidget(clipboard_button)
        
        parse_button = QPushButton('Phasing the input and run the algorithm', self)
        parse_button.clicked.connect(self.process_input_and_save_data)
        layout.addWidget(parse_button)
        
        file_button = QPushButton('Load from File', self)
        file_button.clicked.connect(self.load_from_file)
        layout.addWidget(file_button)

        latest_file_button = QPushButton('Load from Latest File', self)
        latest_file_button.clicked.connect(self.load_from_latest_file)
        layout.addWidget(latest_file_button)

        # self.masterProgressBar = QProgressBar(self)
        # layout.addWidget(self.masterProgressBar)

        self.testEdit = QTextEdit(self)
        self.testEdit.setReadOnly(True)
        layout.addWidget(self.testEdit)

        latest_file_button.clicked.connect(self.add_text)
        file_button.clicked.connect(self.add_text)
        
        self.status_label = QLabel('', self)
        layout.addWidget(self.status_label)

        # self.time_label = QLabel('', self)
        # layout.addWidget(self.time_label)

        self.size_input = QLineEdit(self)
        self.size_input.setPlaceholderText('Enter size of dependencies')
        layout_gen.addWidget(self.size_input)

        self.size_input_uni = QLineEdit(self)
        self.size_input_uni.setPlaceholderText('Enter size of universe')
        layout_gen.addWidget(self.size_input_uni)

        self.size_input_X = QLineEdit(self)
        self.size_input_X.setPlaceholderText('Enter size of X')
        layout_gen.addWidget(self.size_input_X)

        self.tests_input = QLineEdit(self)
        self.tests_input.setPlaceholderText('Enter number of tests')
        layout_gen.addWidget(self.tests_input)

        self.button = QPushButton('Gen test data', self)
        self.button.clicked.connect(self.on_click_with_thread)
        layout_gen.addWidget(self.button)

        self.button_plot = QPushButton('Gen Plot', self)
        self.button_plot.clicked.connect(self.open_plot_window)
        layout_gen.addWidget(self.button_plot)
        # self.progressBar = QProgressBar(self)
        # layout_gen.addWidget(self.progressBar)

        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        layout_gen.addWidget(self.result_text)

        self.dependencies_text = QTextEdit(self)
        self.dependencies_text.setPlaceholderText("Generated Dependencies will appear here.")
        self.dependencies_text.setReadOnly(True)
        layout_gen.addWidget(self.dependencies_text)
        
        layout_total.addLayout(layout)
        layout_total.addLayout(layout_gen)
        
        self.setLayout(layout_total)
        self.status_label.setText("Ready")
    
    def onActivated(self, text):
        # 更新标签内容以显示选择的选项
        self.label.setText(f"You selected: {text}")
        self.status_label.setText(f"Running {text} algorithm...")

    def open_plot_window(self):
        plot_dialog = PlotDialog(self)
        plot_dialog.exec_()

    def add_text(self):
        sender = self.sender()
        new_text = f"Clicked on {sender.text()}\n"
        self.testEdit.moveCursor(QTextCursor.End)
        self.testEdit.insertPlainText(new_text)
        self.testEdit.ensureCursorVisible()

    def on_finished_load(self, total_input_dict):
        print("The datatype of the total_input_dict is: ", type(total_input_dict))
        self.status_label.setText("Finished loading the data")
        self.run_testsV2(total_input_dict)

    def thread_read_run(self, file_path):
        if self.worker is None or not self.worker.isRunning():
            algo_load_worker = LoadWorker(file_path)
            self.worker = algo_load_worker
            self.worker.finished.connect(self.on_finished_load)
            self.worker.start()
        else:
            self.status_label.setText("Worker is running, please wait...")

    def find_latest_file(self, directory):
        # 获取目录下所有文件的路径
        files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.txt')]
        # 根据修改时间找到最新的文件
        if files:
            latest_file = max(files, key=os.path.getmtime)
            return latest_file
        return None

    def load_from_file(self):
        '''
        get the file name from the user and load the data from the file
        '''
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "/dissertation/testcode/testData/", "Text Files (*.txt)")
        if file_name:
            self.testEdit.append(f"Loading data from {file_name}...")
            self.thread_read_run(file_name)
            self.testEdit.append("Loading data from the file")
        else:
            self.status_label.setText("No file selected")

    def load_from_latest_file(self):
        '''
        get the latest file from the testData folder and load the data from the file
        return a dictionary of test cases
        '''
        current_directory = os.path.dirname(__file__)
        folder_path = os.path.join(current_directory, "testData")
        print(folder_path)
        
        file_name= self.find_latest_file(folder_path)
        
        if file_name:
            self.testEdit.append(f"Loading data from {file_name}...")
            self.thread_read_run(file_name)
            self.testEdit.append("Loading data from the file")
        else:
            self.status_label.setText("No file found in the testData folder")

    def run_testsV2(self, test_cases):
        result_signal = pyqtSignal(str)
        self.len = len(test_cases)
        self.testEdit.append("Running tests...\n")
        if self.worker is None or not self.worker.isRunning():
            self.worker = RunWorkerV2(test_cases, self.combo.currentText())
            self.worker.finished.connect(self.on_finished_runtest)
            self.worker.all_finished.connect(self.on_finished_allruntest)
            self.worker.str_pass.connect(self.testEdit.append)
            self.worker.start()
        else:
            self.testEdit.append("Worker is running, please wait...")


    def on_finished_runtest(self, exe_time):
        self.testEdit.append(f"Execution time: {exe_time} seconds")
        return exe_time
    def on_finished_allruntest(self):
        self.testEdit.append("All done")
        self.testEdit.append(f"Finished running {self.len} tests")
        self.status_label.setText(f"Finished running {self.len} tests")
        time.sleep(5)
        self.status_label.setText("Ready")
    
    def run_tests(self, test_cases):
        '''
        test_cases: a dictionary of test cases, where the key is the test name and the value is a dictionary of universe, X, MVDs, and FDs
        this test_cases is generated from the file, and processed by the load_from_file function or load_from_latest_file function
        '''
        results = []
        total_time = 0
        self.testEdit.append("Running tests...\n")
        

        for test in test_cases.values():
            # print(test)
            universe_str = test["universe"].split()
            X_str = test["X"].split()
            mvd_text = test["MVDs"]
            fd_text = test["FDs"]
            X = [int(x) for x in X_str]
            universe = [int(u) for u in universe_str]

            # F ,G = Mf.parse_dependencies(fd_text, mvd_text)
            # basis, closure = Mf.dep_basis(set(X), set(universe), G, F)
            if self.worker is None or not self.worker.isRunning():
                algo_test_worker = RunWorker(fd_text, mvd_text, X, universe)
                self.worker = algo_test_worker
                # self.worker.finished.connect(self.on_finished_runtest)
                exe_time = self.worker.run_test()
                self.worker.start()
                # self.worker.wait()
                
            total_time += exe_time
            # results.append(f"new basis: {basis} | new closure: {closure}")
            # results.append(f"Execution time: {exe_time} seconds")
            self.testEdit.append(f"Execution time: {exe_time} seconds")

            # save the running log to a file
            len_universe = len(universe)
            len_X = len(X)
            len_F = len(fd_text)
            len_G = len(mvd_text)
            algorithm_name = self.combo.currentText()
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

        self.status_label.setText(f"Finished running {len(test_cases)} tests")
        self.testEdit.setText(f"Average time: {total_time / len(test_cases)} seconds \n" +"\n".join(results))



    def get_from_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text()
        if clipboard_text:
            lines = clipboard_text.splitlines()

            if len(lines) >= 3:
                self.entry_universe.setText(lines[0])
                self.entry_X.setText(lines[1])
                self.entry_mvd.setText(lines[2])
            else:
                QMessageBox.warning(self, "Invalid clipboard content", "Clipboard content does not match the expected format")
        else:
            QMessageBox.warning(self, "Empty clipboard", "Clipboard is empty")

        self.status_label.setText("Pasted text from clipboard")


    def process_input_and_save_data(self):
        '''
        process the input and save the data
        run the algorithm with the input get from the GUI text box
        '''
        mvd_text = self.entry_mvd.text()
        if mvd_text:
            try:
                lines = mvd_text.split(';')
                self.saved_inputs_mvd.clear()
                self.saved_inputs_fd.clear()
                for line in lines:
                    parts = line.split(':')
                    if len(parts) == 2:
                        if parts[0].strip() == "FD":
                            self.saved_inputs_fd.append(Mf.parse_dependency_string(parts[1]))
                        elif parts[0].strip() == "MVD":
                            self.saved_inputs_mvd.append(Mf.parse_dependency_string(parts[1]))
                        else:
                            raise ValueError("Invalid dependency type: " + parts[0])
            except Exception as e:
                self.status_label.setText(f"MVD Phasing Error: {str(e)}")
                return

        universe_str = self.entry_universe.text().strip().split(',')
        universe = set([int(u) for u in universe_str if u])
        if self.entry_X.text().strip():
            X, Y = Mf.parse_single_dependency(self.entry_X.text().strip())
        else:
            self.status_label.setText("No dependency to test")

        if universe and X:
            self.saved_strings = [universe, X]
        
        if (self.saved_inputs_fd or self.saved_inputs_mvd) and self.saved_strings:
            start_time = time.time()
            memberTestResult, basis = Mf.membership_test(set(X), set(Y), set(self.saved_strings[0]), self.saved_inputs_fd, self.saved_inputs_mvd)
            # basis, closure = Mp.dep_basis(set(self.saved_strings[1]), set(self.saved_strings[0]), self.saved_inputs)
            end_time = time.time()
            exe_time = end_time - start_time
            
            # mvd_outputs = ", ".join([f"{x[0]} ->> {x[1]}" for x in self.saved_inputs])
            # string_outputs = ", ".join(self.saved_strings)
            self.testEdit.setText(f"Running time: {exe_time} seconds | Result: {memberTestResult} | Basis: {basis}\n")
            # self.result_label.setText(f"new basis: {basis}")
            # self.time_label.setText(f"Execution time: {exe_time} seconds")


    def on_click_with_thread(self):
        '''
        on_click function, to generate the test data with thread

        '''
        if self.size_input.text()!='':
            size = int(self.size_input.text())
        else:
            size = 100
        if self.size_input_uni.text()!='':
            uni_size = int(self.size_input_uni.text())
        else:
            uni_size = 1000
        if self.size_input_X.text()!='':
            X_size = int(self.size_input_X.text())
        else:
            X_size = 5

        if self.tests_input.text()!='':
            tests = int(self.tests_input.text())
        else:
            tests = 10

        total_time = 0
        # Generate filename based on current datetime and input size
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"deptest_FUG{size}_u{uni_size}_{timestamp}.csv"

        current_directory = os.path.dirname(__file__)
        folder_path = os.path.join(current_directory, "testData")

        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)

        for test_id in range(tests):
            if self.worker is None or not self.worker.isRunning():
                testdata_gen_worker = GenWorker(file_path, filename, test_id, size, 1000000, uni_size)
                self.worker = testdata_gen_worker
                self.worker.finished.connect(self.on_finished)
                progress = 100*test_id/tests
                self.worker.start()
            #_, temp_time = self.gen_dependency_pandas(file_path, filename, test_id, size, chunk_size=1000000, universe_size=uni_size)
            #total_time += temp_time
        #average_time = total_time / tests
        #self.result_text.setText(f'Average time for size {size} with {tests} tests: {average_time:.4f} seconds')
        print("Finished generating test data")
        self.status_label.setText(f"Dependencies saved to {file_path}")
    
    def on_finished(self, gen_time):
        self.result_text.append(f"Generation time: {gen_time:.4f} seconds")
        # return gen_time



app = QApplication(sys.argv)
ex = MVDParser()
ex.show()
sys.exit(app.exec_())

