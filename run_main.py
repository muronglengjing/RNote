import logging
import os
import pickle
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog, QDialogButtonBox, QTreeWidgetItem, QListWidgetItem

import about
import function
import main
import newBlock
import newBook
import newPage
import set

address = {}
book = {}  # 名字-地址

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG, filename='log.txt',
                    filemode='a')


class Ui(main.Ui_Main):
    def update_tree(self):
        try:
            self.tree.clear()
            logging.debug("update the tree view")
            for books in book.keys():
                items = QTreeWidgetItem(ui.tree)
                items.setText(0, books)
                for blocks in book[books]:
                    item = QTreeWidgetItem()
                    item.setText(0, blocks)
                    for pages in book[books][blocks]:
                        page = QTreeWidgetItem()
                        page.setText(0, pages)
                        item.addChild(page)
                    items.addChild(item)
                self.tree.topLevelItem(0).addChild(items)
            logging.debug("update tree completed!")
            self.tree.expandAll()
        except OSError:
            logging.debug("failed to update the tree")


def data_input():
    filename = QFileDialog.getOpenFileName(widget, 'Open file', '/home', "RNote Files (*.rnb);;All Files (*)")
    if filename[0]:
        try:
            logging.debug("input data from {}".format(filename[0]))
            with open(filename[0], 'rb') as f:
                data_book, data_address = pickle.load(f)
            for books in data_book:
                if books in book:
                    for blocks in data_book[books]:
                        if blocks in book[books]:
                            for pages in book[books][blocks]:
                                if pages in book[books][blocks]:
                                    continue
                                book[books][blocks].append(pages)
                    data_book[books][blocks] = data_book[books][blocks]
                book[books] = data_book[books]
            for addresses in data_address:
                if addresses in address:
                    continue
                address[addresses] = data_address[addresses]
            save()
            ui.update_tree()
            ui.statusbar.showMessage("数据导入成功")
        except IOError:
            logging.warning("failed to input data from {}".format(filename[0]))


def data_output():
    filename = QFileDialog.getSaveFileName(widget, "输出数据", '/note_data', "RNote File(*.rnb);;AllFiles(*)")
    if filename[0] != "":
        try:
            logging.debug("output data to {}".format(filename[0]))
            with open(filename[0], "wb") as f:
                pickle.dump([book, address], f)
            logging.debug("data output!")
        except IOError:
            logging.warning("failed to output data to {}".format(filename[0]))


def delete():
    try:
        if set_ui.tabWidget.currentIndex() == 0:
            if set_ui.treeWidget.currentIndex().data() in book:
                logging.debug("detele {}".format(set_ui.treeWidget.currentIndex().data()))
                book.pop(set_ui.treeWidget.currentIndex().data())
                address.pop(set_ui.treeWidget.currentIndex().data())
                set_init()
                ui.update_tree()
                save()
            else:
                ui.statusbar.showMessage("选择地址是不可以的哦！把鼠标左移一点吧！")
        elif set_ui.tabWidget.currentIndex() == 1:
            logging.debug("detele {}".format(set_ui.listWidget.currentIndex().data()))
            book[set_ui.comboBox.currentText()].pop(set_ui.listWidget.currentIndex().data())
            path = "{}/{}".format(address[set_ui.comboBox.currentText()], set_ui.listWidget.currentIndex().data())
            dir = QDir()
            dir.rmdir(path)
            set_init()
            ui.update_tree()
            save()
        else:
            logging.debug("detele {}".format(set_ui.listWidget_2.currentIndex().data()))
            book[set_ui.comboBox_2.currentText()][set_ui.comboBox_3.currentText()].remove(
                set_ui.listWidget_2.currentIndex().data())
            path = "{}/{}/{}.md".format(address[set_ui.comboBox_2.currentText()],
                                        set_ui.comboBox_3.currentText(), set_ui.listWidget_2.currentIndex().data())
            dir = QDir()
            dir.remove(path)
            set_init()
            ui.update_tree()
            save()
    except IOError:
        logging.warning("failed to delete")


def search():
    try:
        if set_ui.tabWidget.currentIndex() == 1:
            logging.debug("search file {}".format(set_ui.comboBox.currentText()))
            path = "{}/".format(address[set_ui.comboBox.currentText()])
            for root, dirs, files in os.walk(path, topdown=True):
                if root == path:
                    for dir in dirs:
                        if dir not in book[set_ui.comboBox.currentText()]:
                            book[set_ui.comboBox.currentText()][dir] = []
            set_init()
            ui.update_tree()
            save()
        elif set_ui.tabWidget.currentIndex() == 2:
            logging.debug("search file {}".format(set_ui.comboBox_3.currentText()))
            path = "{}/{}/".format(address[set_ui.comboBox_2.currentText()],
                                   set_ui.comboBox_3.currentText())
            for root, dirs, files in os.walk(path):
                for file in files:
                    if ".md" in file:
                        file = file.replace(".md", "")
                        if file not in book[set_ui.comboBox_2.currentText()][set_ui.comboBox_3.currentText()]:
                            book[set_ui.comboBox_2.currentText()][set_ui.comboBox_3.currentText()].append(file)
            set_init()
            ui.update_tree()
            save()
    except IOError:
        logging.warning("failed to search")


def check():
    try:
        if not ui.tree.currentItem().parent() is None:
            if not ui.tree.currentItem().parent().parent() is None:
                logging.debug("open the file {}".format(ui.tree.currentItem().text(0)))
                items = ui.tree.currentItem().parent().parent()
                dir = items.data(0, 0)
                item = ui.tree.currentItem().parent()
                block = item.data(0, 0)
                pages = ui.tree.currentItem().text(0)
                file = "{}/{}/{}.md".format(address[dir], block, pages)
                use_system_open(file)
    except FileExistsError:
        logging.warning("failed to open")


def set_init():
    set_Dialog.show()
    try:
        logging.debug("get the book address")
        set_ui.treeWidget.clear()
        for books in address:
            items = QTreeWidgetItem(set_ui.treeWidget)
            items.setText(0, books)
            items.setText(1, address[books])
            set_ui.treeWidget.topLevelItem(0).addChild(items)
            set_ui.treeWidget.setCurrentItem(items)
    except OSError:
        logging.debug("failed to get")
    try:
        logging.debug("get the block")
        set_ui.comboBox.clear()
        for blocks in book:
            set_ui.comboBox.addItem(blocks)
    except OSError:
        logging.debug("failed to get")
    try:
        logging.debug("get the page")
        set_ui.comboBox_2.clear()
        for blocks in book:
            set_ui.comboBox_2.addItem(blocks)
    except OSError:
        logging.debug("failed to get")


def text_save():
    try:
        if not ui.tree.currentItem().parent() is None:
            if not ui.tree.currentItem().parent().parent() is None:
                logging.debug("get the text {}".format(ui.tree.currentItem().text(0)))
                items = ui.tree.currentItem().parent().parent()
                dir = items.data(0, 0)
                item = ui.tree.currentItem().parent()
                block = item.data(0, 0)
                pages = ui.tree.currentItem().text(0)
                file = "{}/{}/{}.md".format(address[dir], block, pages)
                try:
                    logging.debug("save the file {}".format(file))
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(ui.plainTextEdit.toPlainText())
                    ui.statusbar.showMessage("内容更新到{}".format(file))
                except EOFError:
                    logging.warning("failed to save")
    except IOError:
        logging.warning("failed to get")


def choose_page():
    try:
        if not ui.tree.currentItem().parent() is None:
            if not ui.tree.currentItem().parent().parent() is None:
                logging.debug("get the text {}".format(ui.tree.currentItem().text(0)))
                items = ui.tree.currentItem().parent().parent()
                dir = items.data(0, 0)
                item = ui.tree.currentItem().parent()
                block = item.data(0, 0)
                pages = ui.tree.currentItem().text(0)
                file = "{}/{}/{}.md".format(address[dir], block, pages)
                if ui.toolBox.currentIndex() == 0:
                    try:
                        logging.debug("read the file {}".format(file))
                        read(file)
                        ui.statusbar.showMessage("文件{}打开".format(file))
                    except EOFError:
                        logging.warning("failed to read")
                elif ui.toolBox.currentIndex() == 1:
                    try:
                        ui.plainTextEdit.clear()
                        logging.debug("read the file {}".format(file))
                        with open(file, 'r', encoding='utf-8') as f:
                            ui.plainTextEdit.appendPlainText(f.read())
                    except EOFError:
                        logging.warning("failed to read")
    except IOError:
        logging.warning("failed to get")


def use_system_open(path):
    try:
        logging.warning("open the file with normal application {}".format(path))
        os.startfile(path)
        ui.statusbar.showMessage("使用默认程序打开{}".format(path))
    except IOError:
        logging.warning("failed to open")


def read(file):
    try:
        logging.debug("read file {}".format(file))
        ui.textBrowser.clear()
        with open(file, "r", encoding='utf-8') as f:
            x = f.read()
            x = mA.analyses_whole(x)
            ui.textBrowser.append(x)
    except IOError:
        logging.warning("failed to read")


def load():
    global book, address
    try:
        logging.debug("load book data")
        with open("resource/book.pk", "rb") as f:
            book = pickle.load(f)
    except IOError:
        logging.warning("failed to load")
    try:
        logging.debug("load address data")
        with open("resource/address.pk", "rb") as f:
            address = pickle.load(f)
        logging.debug("address {}".format(address))
    except IOError:
        logging.warning("failed to load")
    ui.update_tree()


def save():
    try:
        logging.debug("save book")
        with open("resource/book.pk", "wb") as f:
            pickle.dump(book, f)
    except IOError:
        logging.warning("failed to save")
    try:
        logging.debug("save address")
        with open("resource/address.pk", "wb") as f:
            pickle.dump(address, f)
    except IOError:
        logging.warning("failed to save")
    ui.update_tree()


def newB():
    try:
        logging.debug("block windows show")
        block_ui.comboBox.clear()
        for blocks in book:
            block_ui.comboBox.addItem(blocks)
        block_Dialog.show()
    except OSError:
        logging.debug("failed to show")


def newP():
    try:
        logging.debug("page windows show")
        page_ui.comboBox.clear()
        page_dialog.show()
        for blocks in book:
            page_ui.comboBox.addItem(blocks)
    except OSError:
        logging.debug("failed to show")


def setup_page():
    try:
        logging.debug("set up block")
        page_ui.comboBox_2.clear()
        if page_ui.comboBox.currentText():
            for books in book[page_ui.comboBox.currentText()]:
                page_ui.comboBox_2.addItem(books)
    except OSError:
        logging.warning("failed to set up")


def setup_set_page():
    try:
        logging.debug("set up page")
        set_ui.comboBox_3.clear()
        if set_ui.comboBox_2.currentText():
            for books in book[set_ui.comboBox_2.currentText()]:
                set_ui.comboBox_3.addItem(books)
        setup_set_page_list()
    except OSError:
        logging.warning("failed to set up")


def setup_set_block_list():
    try:
        logging.debug("set the block list")
        set_ui.listWidget.clear()

        if set_ui.comboBox.currentText():
            for blocks in list(book[set_ui.comboBox.currentText()]):
                items = QListWidgetItem(set_ui.listWidget)
                items.setText(blocks)
                set_ui.listWidget.setCurrentItem(items)
    except OSError:
        logging.warning("failed to set")


def setup_set_page_list():
    try:
        logging.debug("set the pages list")
        set_ui.listWidget_2.clear()
        if set_ui.comboBox_2.currentText() and set_ui.comboBox_3.currentText():
            for pages in list(book[set_ui.comboBox_2.currentText()][set_ui.comboBox_3.currentText()]):
                items = QListWidgetItem(set_ui.listWidget_2)
                items.setText(pages)
                set_ui.listWidget_2.setCurrentItem(items)
    except OSError:
        logging.warning("failed to set")


def open_file(widget):
    try:
        logging.debug("opened dir")
        path = QFileDialog.getExistingDirectory(widget, "getExistingDirectory", "./")
        if not path.isspace():
            book_ui.pushButton.setText(path)
    except OSError:
        logging.warning("failed to open")


def add_book():
    try:
        if not book_ui.pushButton.text() == "打开" and book_ui.lineEdit.text():
            logging.warning("add book {}".format(book_ui.lineEdit.text()))
            book[book_ui.lineEdit.text()] = {}
            address[book_ui.lineEdit.text()] = book_ui.pushButton.text()
            logging.debug("new book added! {}".format(book_ui.pushButton.text()))
            save()
            ui.statusbar.showMessage("笔记本{}创建".format(book_ui.lineEdit.text()))
        else:
            ui.statusbar.showMessage("输入不完整！重新输入···")
    except OSError:
        logging.warning("failed to add")


def add_block():
    try:
        if not (block_ui.comboBox.currentText() == "" and block_ui.lineEdit.text() == ""):
            logging.debug("create dir {}".format(block_ui.lineEdit.text()))
            path = "{}/{}".format(address[block_ui.comboBox.currentText()], block_ui.lineEdit.text())
            dir = QDir()
            dir.mkdir(path)
            try:
                logging.warning("add block")
                book[block_ui.comboBox.currentText()][block_ui.lineEdit.text()] = []
                save()
                ui.statusbar.showMessage("分区{}创建".format(book_ui.lineEdit.text()))
            except OSError:
                logging.warning("failed to add")
    except OSError:
        logging.warning("failed to create")


def add_page():
    try:
        if not (page_ui.comboBox.currentText() == ""
                and page_ui.comboBox_2.currentText() == "" and page_ui.lineEdit.text() == ""):
            logging.debug("create file {}".format(block_ui.lineEdit.text()))
            path = "{}/{}/{}.md".format(address[page_ui.comboBox.currentText()],
                                        page_ui.comboBox_2.currentText(), page_ui.lineEdit.text())

            with open(path, "a", encoding='utf-8') as f:
                f.write("")
            try:
                logging.debug("add page")
                book[page_ui.comboBox.currentText()][page_ui.comboBox_2.currentText()].append(page_ui.lineEdit.text())
                save()
                ui.statusbar.showMessage("页{}创建".format(book_ui.lineEdit.text()))
            except IOError:
                logging.warning("failed to add")
    except EOFError:
        logging.debug("failed to create")


def connect():
    ui.addNoteBook.triggered.connect(book_Dialog.show)
    ui.addBlock.triggered.connect(newB)
    ui.addPage.triggered.connect(newP)
    ui.tree.clicked.connect(choose_page)
    ui.check.triggered.connect(check)
    ui.welcome.triggered.connect(lambda: read("resource/readme"))
    ui.about.triggered.connect(about_Dialog.show)
    ui.log.triggered.connect(lambda: use_system_open("log.txt"))
    ui.set_tool.triggered.connect(set_init)
    ui.actionimport_data.triggered.connect(data_input)
    ui.actionoutput_data.triggered.connect(data_output)
    ui.save.clicked.connect(text_save)
    ui.toolBox.currentChanged.connect(choose_page)
    book_ui.pushButton.clicked.connect(lambda: open_file(book_Dialog))
    book_ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(add_book)
    block_ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(add_block)
    page_ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(add_page)
    page_ui.comboBox.currentIndexChanged.connect(setup_page)
    set_ui.comboBox.currentIndexChanged.connect(setup_set_block_list)
    set_ui.comboBox_2.currentIndexChanged.connect(setup_set_page)
    set_ui.comboBox_3.currentIndexChanged.connect(setup_set_page_list)
    set_ui.deleteButton.clicked.connect(delete)
    set_ui.searchButton.clicked.connect(search)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QMainWindow()
    ui = Ui()
    ui.setupUi(widget)

    widget.show()

    book_Dialog = QtWidgets.QDialog()
    book_ui = newBook.Ui_Dialog()
    book_ui.setupUi(book_Dialog)
    block_Dialog = QtWidgets.QDialog()
    block_ui = newBlock.Ui_Dialog()
    block_ui.setupUi(block_Dialog)
    page_dialog = QtWidgets.QDialog()
    page_ui = newPage.Ui_Dialog()
    page_ui.setupUi(page_dialog)
    about_Dialog = QtWidgets.QDialog()
    about_ui = about.Ui_Dialog()
    about_ui.setupUi(about_Dialog)
    set_Dialog = QtWidgets.QDialog()
    set_ui = set.Ui_Dialog()
    set_ui.setupUi(set_Dialog)

    mA = function.MarkdownAnalyses()

    read("resource/readme")

    load()

    connect()

    sys.exit(app.exec_())
