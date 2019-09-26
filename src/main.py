from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QDialog, QFileDialog, QApplication
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QUrl, Qt
from set_proxy import SetProxies
from search_links import SearchLinks
from collect_pdf import CollectPdf
from datetime import datetime
import sys
import threading


class GooglePatentsScraper(QDialog):

    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.searchButton.setIcon(QIcon('resources/iconfinder_search_461380.png'))
        self.collectpdf = None
        self.searchlinks = None
        self.setproxies_dialog = None
        self.collectpdf_thread = None
        self.numbers = None
        self.titles = None
        self.links = None
        self.proxy = None

    def set_proxy(self, ip):
        self.proxy = ip
        self.proxyLabel.setText(f'<span style="color:Chocolate">Current Proxy: {self.proxy}</span>')

    def mousePressEvent(self, event):
        if app.focusWidget():
            self.setFocus()

    @pyqtSlot()
    def on_setproxiesButton_clicked(self):
        if not self.setproxies_dialog:
            self.setproxies_dialog = SetProxies()
            self.setproxies_dialog.proxy_selected.connect(self.set_proxy)
        self.setproxies_dialog.show()

    @pyqtSlot()
    def on_directoryButton_clicked(self):
        self.directoryEdit.setText(QFileDialog.getExistingDirectory(self, 'choose output directory'))

    @pyqtSlot()
    def on_searchButton_clicked(self):
        if self.searchtermsEdit.text() == '':
            self.update_log('Please enter your search terms first.')
        else:
            self.searchlinks = SearchLinks(self.proxy)
            self.searchlinks.search(self.searchtermsEdit.text())
            self.numbers, self.titles = self.searchlinks.collect_links()
            self.links = [f'https://patents.google.com/patent/{s}/en' for s in self.numbers]
            self.print_search_result()

    @pyqtSlot()
    def on_downloadButton_clicked(self):
        self.update_log('Preparing your download...')
        self.collectpdf = CollectPdf(self.directoryEdit.text())
        self.collectpdf.signal_update.connect(self.update_log)
        self.collectpdf.signal_download_progress.connect(self.update_progressbar)
        self.collectpdf_thread = threading.Thread(target=self.collectpdf.start_download,
                                                  args=(self.links, self.searchtermsEdit.text(),
                                                        self.downloadoptionsBox.currentIndex()))
        self.collectpdf_thread.start()

    def update_progressbar(self, percentage):
        self.progressBar.setValue(percentage)

    def update_log(self, message):
        self.logBrowser.append(f'({datetime.today().strftime("%H:%M:%S")}) {message}')

    def print_search_result(self):
        s = ''
        s += '<style type="text/css">a{text-decoration: none; cursor: pointer;}</style>'
        # remember to set font of TextBrowser to "Monospaced Font" (I choose Monaco)
        for index, (number, title) in enumerate(zip(self.numbers, self.titles), start=1):
            link = f'https://patents.google.com/patent/{number}/en'
            a = f'{f"({index})":<4}{number:<12} : {title}'
            s += f'<a href="{link}">{a.replace(" ", "&nbsp;")}</a><br>'

        self.searchresultBrowser.setHtml(s)
        self.aboutLabel.setText(f'(About {len(self.numbers)} results)')

    @pyqtSlot()
    def on_openfolderButton_clicked(self):
        if not QDesktopServices.openUrl(QUrl('file://' + self.directoryEdit.text())):
            self.update_log('Could not open output directory.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GooglePatentsScraper()
    window.show()
    sys.exit(app.exec_())
