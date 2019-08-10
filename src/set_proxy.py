from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal
import sys
import urllib.request
import urllib.error
import urllib.parse
import threading


class SetProxies(QDialog):

    signal_update = pyqtSignal(str)
    proxy_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        loadUi('set_proxy.ui', self)
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.signal_update.connect(self.update_proxies_status)
        self.active_proxies = []
        self.selected_proxy = None
        self.check_proxies_thread = None
        self.proxies_checked = False

    def update_proxies_status(self, message):
        self.logList.addItem(message)

    def on_proxiesList_itemClicked(self, item):
        if self.proxies_checked:
            ip = item.text()
            if ip in self.active_proxies:
                self.selected_proxy_label.setText(f'{ip} selected')
                self.confirmButton.setEnabled(True)
                self.selected_proxy = ip

            else:
                self.selected_proxy_label.setText(f'{ip} is broken, please select a working one')
                self.confirmButton.setEnabled(False)
                self.selected_proxy = None

    @pyqtSlot()
    def on_addButton_clicked(self):
        self.proxiesList.addItem('0.0.0.0:0000')
        self.proxiesList.setCurrentRow(self.proxiesList.count()-1)
        self.proxiesList.currentItem().setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable |
                                                Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled)

    @pyqtSlot()
    def on_removeButton_clicked(self):
        self.proxiesList.takeItem(self.proxiesList.currentRow())

    @pyqtSlot()
    def on_confirmButton_clicked(self):
        self.proxy_selected.emit(self.selected_proxy)
        self.reject()

    @pyqtSlot()
    def on_checkproxiesButton_clicked(self):
        # a thread could only be started once, so we need to construct a new one every time
        self.check_proxies_thread = threading.Thread(target=self.check_proxies)
        self.check_proxies_thread.start()

    def check_proxies(self):
        self.logList.clear()
        self.mousePressEvent(None)
        for i in range(self.proxiesList.count()):
            ip = self.proxiesList.item(i).text()
            try:
                # check if proxy can connect to "https" site
                proxy_handler = urllib.request.ProxyHandler({'https': ip})
                opener = urllib.request.build_opener(proxy_handler)
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                req = urllib.request.Request('https://www.google.com')
                # set timeout to 5 (proxy will be classified to BAD if it can't open google in 5 sec)
                with urllib.request.urlopen(req, timeout=5):
                    self.signal_update.emit(f'\u2713: {ip} is working')
                    self.active_proxies.append(ip)
            except Exception as detail:
                self.signal_update.emit(f'\u2717: {ip} crashed, {detail}')
        self.proxies_checked = True

    def mousePressEvent(self, event):
        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = SetProxies()
    window.show()
    sys.exit(app.exec_())
