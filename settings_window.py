#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PySide.QtGui import QDialog, QIcon, QBoxLayout, QLabel, QLineEdit, QPushButton
from get_certificate_chain import GetCertificateTask


class SettingsWindow(QDialog):
    # noinspection PyUnresolvedReferences
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        super().__init__()
        self.setWindowIcon(QIcon('Logo_sync.png'))
        self.setGeometry(50, 80, 300, 400)
        self.setWindowTitle("c't SESAM Sync Settings")
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        # Widgets
        url_label = QLabel("&URL des c't SESAM Sync Server:")
        self.url_edit = QLineEdit()
        self.url_edit.setMaximumHeight(28)
        self.url_edit.textChanged.connect(self.save_settings)
        url_label.setBuddy(self.url_edit)
        layout.addWidget(url_label)
        layout.addWidget(self.url_edit)
        username_label = QLabel("&Benutzername:")
        self.username_edit = QLineEdit()
        self.username_edit.setMaximumHeight(28)
        self.username_edit.textChanged.connect(self.save_settings)
        username_label.setBuddy(self.username_edit)
        layout.addWidget(username_label)
        layout.addWidget(self.username_edit)
        password_label = QLabel("&Passwort:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMaximumHeight(28)
        self.password_edit.textChanged.connect(self.save_settings)
        password_label.setBuddy(self.password_edit)
        layout.addWidget(password_label)
        layout.addWidget(self.password_edit)
        self.test_button = QPushButton("Verbindung testen")
        self.test_button.clicked.connect(self.get_certificate)
        layout.addWidget(self.test_button)
        # Show the window
        layout.addStretch()
        self.setLayout(layout)
        self.setModal(True)
        self.show()
        self.url_edit.setText("https://ersatzworld.net/ctSESAM/")
        self.username_edit.setText("inter")
        self.password_edit.setText("op")

    def save_settings(self):
        self.settings_manager.sync_manager.set_server_address(self.url_edit.text())

    def get_certificate(self):
        GetCertificateTask(self.url_edit.text(), self.username_edit.text(), self.password_edit.text())
