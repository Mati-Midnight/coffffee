import sys
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt
from random import randint
from PyQt5 import QtCore, QtGui, QtWidgets


class DialogWindow(QDialog):
    def __init__(self, main):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.cur = self.con.cursor()
        self.pushButton.clicked.connect(self.save)
        self.main = main
        self.select_data()

    def select_data(self):
        genre = self.cur.execute("""SELECT name FROM sorts""").fetchall()
        for i in genre:
            self.comboBox_2.addItem(*i)
        genre = self.cur.execute("""SELECT name FROM doneness""").fetchall()
        for i in genre:
            self.comboBox_3.addItem(*i)
        genre = self.cur.execute("""SELECT name FROM groundGrains""").fetchall()
        for i in genre:
            self.comboBox.addItem(*i)

    def save(self):
        self.main.new_post = [self.textEdit.toPlainText(), self.comboBox_2.currentText(),
                              self.comboBox_3.currentText(), self.comboBox.currentText(),
                              self.textEdit_2.toPlainText(), self.spinBox.value(),
                              self.spinBox_2.value()]
        self.close()


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.cur = self.con.cursor()
        self.modified = []
        self.pushButton.clicked.connect(self.save_results)
        self.pushButton_2.clicked.connect(self.dialog_window)
        self.columns = ['ID', 'name', 'sort', 'doneness', 'groundGrains', 'description', 'price', 'size']
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.new_post = []
        self.load_table()

    def item_changed(self, item):
        self.modified.append([item.row(), item.column(), item.text()])

    def save_results(self):
        for i in self.modified:
            self.cur.execute(f"""UPDATE coffee
                    SET "{self.columns[i[1]]}" = "{i[2]}"
                    WHERE ID = {i[0] + 1}""")
        self.con.commit()
        self.load_table()
        self.modified.clear()

    def load_table(self):
        result = self.cur.execute("""SELECT * FROM coffee""").fetchall()
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(result):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def dialog_window(self):
        dialog = DialogWindow(self)
        dialog.exec()
        if len(self.new_post[0]) > 0:
            print("""INSERT INTO coffee({},{},{},{},{},{},{})
             VALUES("{}","{}","{}","{}","{}",{},{})""".format(*self.columns[1:], *self.new_post))
            self.cur.execute("""INSERT INTO coffee({},{},{},{},{},{},{})
             VALUES("{}","{}","{}","{}","{}",{},{})""".format(*self.columns[1:], *self.new_post))
            self.con.commit()
            self.load_table()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())