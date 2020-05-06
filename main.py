import sys  # We need sys so that we can pass argv to QApplication

import commentAnalyzer
import design
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog, QPushButton, QLabel

############ GLOBAL VARIABLES ############
GUI_ASSETS_PATH = 'gui_assets//'


##########################################

# it also keeps events etc that we defined in Qt Designer

class CommentAnalyzerApp(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()

        self.show_intro_dialog('Welcome!')
        self.create_main_window()
        self.set_style_sheets()

        self.results_text_browser.setVisible(False)
        self.results_text_browser_2.setVisible(False)
        self.results_text_browser_3.setVisible(False)
        self.results_text_browser_4.setVisible(False)
        self.results_text_browser_5.setVisible(False)
        self.label_prod_img.setVisible(False)
        self.label_prod_img_2.setVisible(False)

        QObject.connect(self.enter_data_button, SIGNAL("clicked()"), self.activate_comment_analyzer)

        QObject.connect(self.checkBox_URL, SIGNAL("clicked()"), self.checkbox_url_control)
        QObject.connect(self.checkBox_ProdID, SIGNAL("clicked()"), self.checkbox_prodid_control)
        # QObject.connect(self.exitButton, SIGNAL("clicked()"), self.exittt())
        #

        ###################################################
        w = self.centralwidget
        # b = QPushButton(w)

        # b.setText("Hello World!")
        # b.move(50, 50)


        # w.setWindowTitle("PyQt Dialog demo")
        w.show()

    def checkbox_url_control(self):
        if self.checkBox_URL.isChecked():
            self.checkBox_ProdID.setVisible(False)
        else:
            self.checkBox_ProdID.setVisible(True)

    def checkbox_prodid_control(self):
        if self.checkBox_ProdID.isChecked():
            self.checkBox_URL.setVisible(False)
        else:
            self.checkBox_URL.setVisible(True)

    def create_main_window(self):
        self.setupUi(self)

    ###################################################
    @staticmethod
    def background_image_script(image_file_name):
        return 'background-image: url(' + GUI_ASSETS_PATH + image_file_name + '); background-attachment: fixed'

    def set_style_sheets(self):
        dummy_style_script = self.background_image_script('')

        self.setStyleSheet(self.background_image_script('1.jpg'))
        self.results_text_browser.setStyleSheet((self.background_image_script('text_browser_background.png')))
        self.results_text_browser_2.setStyleSheet((self.background_image_script('text_browser_background.png')))
        self.results_text_browser_3.setStyleSheet((self.background_image_script('text_browser_background.png')))
        self.results_text_browser_4.setStyleSheet((self.background_image_script('text_browser_background.png')))
        self.results_text_browser_5.setStyleSheet((self.background_image_script('text_browser_background.png')))

        self.text_edit.setStyleSheet((self.background_image_script('text_browser_background.png')))

        self.exitButton.setStyleSheet(dummy_style_script)
        self.checkBox_URL.setStyleSheet(dummy_style_script)
        self.checkBox_ProdID.setStyleSheet(dummy_style_script)
        self.enter_data_label.setStyleSheet(dummy_style_script + ';color: rgb(255, 255, 255);')
        self.enter_data_label_2.setStyleSheet(dummy_style_script + ';color: rgb(255, 255, 255);')
        self.enter_data_button.setStyleSheet(dummy_style_script)
        self.clear_data_button.setStyleSheet(dummy_style_script)
        self.label_prod_img_2.setStyleSheet(dummy_style_script)
        self.checkBox_URL.setStyleSheet('color: rgb(255, 255, 255);')
        self.checkBox_ProdID.setStyleSheet('color: rgb(255, 255, 255);')

    @staticmethod
    def show_intro_dialog(dialog_str='dialog'):
        d = QDialog()
        d.setGeometry(500, 400, 340, 150)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(design._fromUtf8("gui_assets/app_logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        d.setWindowIcon(icon)
        label = QLabel('    Welcome to Comment Analyzer v1.0!\n    This program is made by Berk Sudan.', d)
        label.move(50, 50)
        button = QPushButton('Forward to program', d)
        button.move(100, 100)
        button.connect(button, SIGNAL("clicked()"), d.close)
        d.setWindowTitle(dialog_str)
        d.setWindowModality(Qt.ApplicationModal)
        d.exec_()

    @staticmethod
    def show_dialog(dialog_str, showed_msg):
        d = QDialog()
        d.setGeometry(500, 400, 200, 60)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(design._fromUtf8("gui_assets/app_logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        d.setWindowIcon(icon)
        label = QLabel(showed_msg, d)
        label.move(10, 10)
        button = QPushButton('Ok', d)
        button.move(100, 100)
        button.connect(button, SIGNAL("clicked()"), d.close)
        d.setWindowTitle(dialog_str)
        d.setWindowModality(Qt.ApplicationModal)
        d.exec_()

    def activate_comment_analyzer(self):
        entered_data = self.get_text_edit_text()
        if self.checkBox_ProdID.isChecked() is False and self.checkBox_URL.isChecked() is False:
            self.show_dialog('ERROR OCCURRED', 'You should select a data type!')
            return

        if self.checkBox_ProdID.isChecked():
            if entered_data.__contains__('https://') is True:
                self.show_dialog('ERROR OCCURRED', 'Entered data is not an ID!\nCheck it again!')
                return
            else:
                prod_id = entered_data
                entered_data = 'https://www.amazon.com/dp/' + entered_data + '/'
        elif self.checkBox_URL.isChecked() and entered_data.__contains__('https://') is False:
            self.show_dialog('ERROR OCCURRED', 'Entered data is not an URL!\nCheck it again!')
            return
        else:
            prod_id = self.text_edit_to_prod_id()

        gui_connection = commentAnalyzer.GuiConnections()
        gui_connection.set_product_url(entered_data)

        try:
            commentAnalyzer.main(gui_connection)
        except:
            self.show_dialog('ERROR OCCURRED', 'Error in Comment Analysis!\nPlease try again!')

        myPixmap = QtGui.QPixmap(design._fromUtf8(
            commentAnalyzer.DIR_PATH + commentAnalyzer.Product.collect_prod_id(
                gui_connection.product_url) + commentAnalyzer.PROD_IMG_POSTFIX))
        myScaledPixmap = myPixmap.scaled(self.label_prod_img.size(), Qt.KeepAspectRatio)
        self.label_prod_img.setPixmap(myScaledPixmap)
        self.label_prod_img.setVisible(True)

        myPixmap = QtGui.QPixmap(design._fromUtf8(
            commentAnalyzer.DIR_PATH + commentAnalyzer.Product.collect_prod_id(
                gui_connection.product_url) + commentAnalyzer.PROD_PLOT_POSTFIX))
        myScaledPixmap = myPixmap.scaled(self.label_prod_img_2.size(), Qt.KeepAspectRatio)
        self.label_prod_img_2.setPixmap(myScaledPixmap)
        self.label_prod_img_2.setVisible(True)


        tmp = commentAnalyzer.DIR_PATH + prod_id
        f = open( tmp + commentAnalyzer.PROD_INFO_POSTFIX, 'r')
        f2 = open(tmp + commentAnalyzer.TOTAL_SENT_SCORE_POSTFIX, 'r')
        f3 = open(tmp + commentAnalyzer.LOG_DIR_PATH_POSTFIX+ 'KNearestNeighborsClustering.txt','r')
        f4 = open(tmp + commentAnalyzer.LOG_DIR_PATH_POSTFIX+ 'SentimentScoreCalculation.txt' , 'r')
        f5 = open(tmp + commentAnalyzer.LOG_DIR_PATH_POSTFIX+ 'Comments.txt', 'r')

        self.results_text_browser.setText(self.fetch_file(f))
        self.results_text_browser_2.setText(self.fetch_file(f2))
        self.results_text_browser_3.setText(self.fetch_file(f3))
        self.results_text_browser_4.setText(self.fetch_file(f4))
        self.results_text_browser_5.setText(self.fetch_file(f5))


        self.results_text_browser.setVisible(True)
        self.results_text_browser_2.setVisible(True)
        self.results_text_browser_3.setVisible(True)
        self.results_text_browser_4.setVisible(True)
        self.results_text_browser_5.setVisible(True)


        f.close()
        f2.close()
        f3.close()
        f4.close()
        f5.close()

    def text_edit_to_prod_id(self):
        return commentAnalyzer.Product.collect_prod_id(self.text_edit.toPlainText())

    def get_text_edit_text(self):
        return self.text_edit.toPlainText()
    def fetch_file(self,file_pointer):
        tmp_str = ''
        for line in file_pointer:
            tmp_str += line
        return tmp_str


def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication

    form = CommentAnalyzerApp()  # We set the form to be our CommentAnalyzerApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app


############################################


if __name__ == '__main__':
    main()

