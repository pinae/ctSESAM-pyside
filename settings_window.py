#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PySide.QtCore import QByteArray, QUrl, QCryptographicHash, QSize, Signal
from PySide.QtGui import QDialog, QIcon, QBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QToolButton
from PySide.QtNetwork import QNetworkRequest, QSsl, QSslCertificate, QSslConfiguration, QSslSocket
from domain_extractor import extract_full_domain
from base64 import b64encode
import json
import re


class SettingsWindow(QDialog):
    certificate_loaded = Signal()
    url_edit = None
    username_edit = None
    password_edit = None
    test_button = None
    message = None

    def __init__(self, sync_manager, network_access_manager, url=None, username=None, password=None):
        self.sync_manager = sync_manager
        self.nam = network_access_manager
        self.certificate = ""
        self.replies = set()
        super().__init__()
        self.setWindowIcon(QIcon('Logo_sync.png'))
        self.setGeometry(70, 60, 300, 250)
        self.setWindowTitle("c't SESAM Sync Settings")
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.setContentsMargins(0, 0, 0, 0)
        # Header bar
        header_bar = QFrame()
        header_bar.setStyleSheet("QWidget { background: rgb(40, 40, 40); } " +
                                 "QToolButton { background: rgb(40, 40, 40); }" +
                                 "QToolTip { color: rgb(255, 255, 255); background-color: rgb(20, 20, 20); " +
                                 "border: 1px solid white; }")
        header_bar.setAutoFillBackground(True)
        header_bar.setFixedHeight(45)
        header_bar_layout = QBoxLayout(QBoxLayout.RightToLeft)
        header_bar_layout.addStretch()
        header_bar.setLayout(header_bar_layout)
        layout.addWidget(header_bar)
        self.create_header_bar(header_bar_layout)
        self.certificate_loaded.connect(self.test_connection)
        # Main area
        main_area = QFrame()
        main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        main_area.setLayout(main_layout)
        layout.addWidget(main_area)
        self.create_main_area(main_layout, url, username, password)
        # Show the window
        layout.addStretch()
        self.setLayout(layout)
        self.show()

    # noinspection PyUnresolvedReferences
    def create_header_bar(self, layout):
        back_button = QToolButton()
        back_button.setIconSize(QSize(30, 30))
        back_button.setIcon(QIcon("ic_action_back.png"))
        back_button.setStyleSheet("border: 0px;")
        back_button.setToolTip("Zurück")
        back_button.clicked.connect(self.back)
        layout.addWidget(back_button)

    # noinspection PyUnresolvedReferences
    def create_main_area(self, layout, url, username, password):
        url_label = QLabel("&URL des c't SESAM Sync Server:")
        self.url_edit = QLineEdit()
        if url:
            self.url_edit.setText(url)
        self.url_edit.setMaximumHeight(28)
        self.url_edit.textChanged.connect(self.url_changed)
        url_label.setBuddy(self.url_edit)
        layout.addWidget(url_label)
        layout.addWidget(self.url_edit)
        username_label = QLabel("&Benutzername:")
        self.username_edit = QLineEdit()
        if username:
            self.username_edit.setText(username)
        self.username_edit.setMaximumHeight(28)
        self.username_edit.textChanged.connect(self.save_settings)
        username_label.setBuddy(self.username_edit)
        layout.addWidget(username_label)
        layout.addWidget(self.username_edit)
        password_label = QLabel("&Passwort:")
        self.password_edit = QLineEdit()
        if password:
            self.password_edit.setText(password)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMaximumHeight(28)
        self.password_edit.textChanged.connect(self.save_settings)
        password_label.setBuddy(self.password_edit)
        layout.addWidget(password_label)
        layout.addWidget(self.password_edit)
        self.test_button = QPushButton("Verbindung testen")
        self.test_button.clicked.connect(self.test_connection)
        layout.addWidget(self.test_button)
        self.message = QLabel("")
        if not self.certificate:
            self.message.setText('<span style="font-size: 10px; color: #aa0000;">' +
                                 'Kein Zertifikat vorhanden.' +
                                 '</span>')
        layout.addWidget(self.message)

    def url_changed(self):
        if self.certificate:
            cert = QSslCertificate(encoded=self.certificate, format=QSsl.Pem)
            domain_list = [cert.subjectInfo(cert.SubjectInfo.CommonName)]
            for key in cert.alternateSubjectNames().keys():
                if type(key) == str and key[:3] == "DNS":
                    domain_list.append(cert.alternateSubjectNames()[key])
            if extract_full_domain(self.url_edit.text()) not in domain_list:
                self.certificate = ""
                self.message.setText('<span style="font-size: 10px; color: #aa0000;">' +
                                     'Kein Zertifikat für diese url vorhanden.' +
                                     '</span>')
        else:
            self.message.setText('<span style="font-size: 10px; color: #aa0000;">' +
                                 'Kein Zertifikat für diese url vorhanden.' +
                                 '</span>')
        self.save_settings()

    def save_settings(self):
        self.sync_manager.set_server_address(self.url_edit.text())
        self.sync_manager.set_username(self.username_edit.text())
        self.sync_manager.set_password(self.password_edit.text())
        if self.certificate:
            self.sync_manager.set_certificate(str(self.certificate))
            self.sync_manager.create_sync()

    def test_connection(self):
        self.message.setText('<span style="font-size: 10px; color: #000000;">' +
                             'Verbindung wird getestet.' +
                             '</span>')
        self.nam.finished.connect(self.test_reply)
        self.nam.sslErrors.connect(self.ssl_errors)
        ssl_config = QSslConfiguration().defaultConfiguration()
        ssl_config.setCiphers(QSslSocket().supportedCiphers())
        if self.certificate:
            certificate = QSslCertificate(encoded=self.certificate, format=QSsl.Pem)
            ssl_config.setCaCertificates([certificate])
        else:
            ssl_config.setCaCertificates([])
        url = QUrl(self.url_edit.text())
        url.setPath("/".join(filter(bool, (url.path() + "/ajax/read.php").split("/"))))
        request = QNetworkRequest(url)
        request.setSslConfiguration(ssl_config)
        request.setRawHeader("Authorization",
                             "Basic ".encode('utf-8') +
                             b64encode((self.username_edit.text() + ":" + self.password_edit.text()).encode('utf-8')))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
        self.replies.add(self.nam.post(request, QByteArray()))

    def ssl_errors(self, reply):
        try:
            self.replies.remove(reply)
        except KeyError:
            return False
        cert = reply.sslConfiguration().peerCertificateChain()[-1]
        if not cert.isValid():
            self.message.setText('<span style="font-size: 10px; color: #aa0000;">' +
                                 'Das Zertifikat ist nicht gültig.' +
                                 '</span>')
            return False
        domain_list = [cert.subjectInfo(cert.SubjectInfo.CommonName)]
        for key in cert.alternateSubjectNames().keys():
            if type(key) == str and key[:3] == "DNS":
                domain_list.append(cert.alternateSubjectNames()[key])
        if extract_full_domain(self.url_edit.text()) not in domain_list:
            self.message.setText('<span style="font-size: 10px; color: #aa0000;">' +
                                 'Das Zertifikat wurde für eine andere Domain ausgestellt.' +
                                 '</span>')
            return False
        message_box = QMessageBox()
        message_box.setText("Ein unbekanntes CA-Zertifikat wurde gefunden.")
        message_box.setInformativeText(
            "Das Zertifikat hat den Fingerabdruck " +
            ":".join(re.findall("(.{2})", str(cert.digest(QCryptographicHash.Sha1).toHex().toUpper()))) +
            ". Möchten Sie diesem Zertifikat vertrauen?")
        message_box.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        message_box.setDefaultButton(QMessageBox.Yes)
        answer = message_box.exec()
        if answer != QMessageBox.Yes:
            self.message.setText('<span style="font-size: 10px; color: #aa0000;">' +
                                 'Sie haben dem Zertifikat nicht vertraut.' +
                                 '</span>')
            return False
        if not self.certificate:
            reply.ignoreSslErrors()
        self.certificate = cert.toPem()
        self.save_settings()
        self.certificate_loaded.emit()

    def test_reply(self, reply):
        if reply not in self.replies:
            return False
        if reply.error() == reply.NetworkError.AuthenticationRequiredError:
            self.message.setText('<span style="font-size: 10px; color: #aa0000;">' +
                                 'Benutzername oder Passwort stimmen nicht.' +
                                 '</span>')
            return False
        content = reply.readAll()
        if content.isEmpty():
            return False
        reply_data = json.loads(str(content))
        if "status" in reply_data and reply_data["status"] == "ok":
            self.message.setText('<span style="font-size: 10px; color: #00AA00;">' +
                                 'Verbindung erfolgreich getestet.' +
                                 '</span>')
        else:
            self.message.setText('<span style="font-size: 10px; color: #aa0000;">' +
                                 'Vom Syncserver kam eine Antwort aber kein OK.' +
                                 '</span>')

    def back(self):
        if self.certificate:
            self.accept()
        else:
            self.reject()
