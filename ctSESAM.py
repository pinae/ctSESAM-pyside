#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
from PySide.QtGui import QApplication, QWidget, QBoxLayout, QFont, QIcon, QFrame
from PySide.QtGui import QLabel, QLineEdit, QComboBox, QToolButton
from PySide.QtCore import Qt, QSize, QPoint, QCoreApplication, QSettings
from PySide.QtNetwork import QNetworkAccessManager
from password_strength_selector import PasswordStrengthSelector
from settings_window import SettingsWindow
from base64 import b64decode

from password_generator import CtSesam
from preference_manager import PreferenceManager
from kgk_manager import KgkManager
from password_settings_manager import PasswordSettingsManager
from decrypt_kgk_task import DecryptKgkTask


class MainWindow(QWidget, object):
    master_password_label = None
    master_password_edit = None
    domain_label = None
    domain_edit = None
    username_label = None
    username_edit = None
    strength_label = None
    strength_selector = None
    password_label = None
    password = None
    sync_button = None
    clipboard_button = None
    setting = None
    decrypt_kgk_task = None
    settings_window = None

    def __init__(self):
        super(MainWindow, self).__init__()
        self.nam = QNetworkAccessManager()
        self.setWindowIcon(QIcon(os.path.join('icons', 'Logo_rendered_edited.png')))
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.setContentsMargins(0, 0, 0, 0)
        self.preference_manager = PreferenceManager()
        self.kgk_manager = KgkManager()
        self.kgk_manager.set_preference_manager(self.preference_manager)
        self.settings_manager = PasswordSettingsManager(self.preference_manager)
        self.setting_dirty = True
        # Header bar
        header_bar = QFrame()
        header_bar.setStyleSheet(
            "QWidget { background: rgb(40, 40, 40); } " +
            "QToolButton { background: rgb(40, 40, 40); }" +
            "QToolTip { color: rgb(255, 255, 255); background-color: rgb(20, 20, 20); " +
            "border: 1px solid white; }")
        header_bar.setAutoFillBackground(True)
        header_bar.setFixedHeight(45)
        header_bar_layout = QBoxLayout(QBoxLayout.LeftToRight)
        header_bar_layout.addStretch()
        header_bar.setLayout(header_bar_layout)
        layout.addWidget(header_bar)
        self.create_header_bar(header_bar_layout)
        # Widget area
        main_area = QFrame()
        main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        main_area.setLayout(main_layout)
        layout.addWidget(main_area)
        self.create_main_area(main_layout)
        # Window layout
        layout.addStretch()
        main_layout.addStretch()
        self.setLayout(layout)
        settings = QSettings()
        size = settings.value("MainWindow/size")
        if not size:
            size = QSize(350, 450)
        self.resize(size)
        position = settings.value("MainWindow/pos")
        if not position:
            position = QPoint(0, 24)
        self.move(position)
        self.setWindowTitle("c't SESAM")
        self.master_password_edit.setFocus()
        self.show()

    # noinspection PyUnresolvedReferences
    def create_header_bar(self, layout):
        self.sync_button = QToolButton()
        self.sync_button.setIconSize(QSize(30, 30))
        self.sync_button.setIcon(QIcon(os.path.join("icons", "ic_action_sync.png")))
        self.sync_button.setStyleSheet("border: 0px;")
        self.sync_button.setToolTip("Sync")
        self.sync_button.clicked.connect(self.sync_clicked)
        self.sync_button.setVisible(False)
        layout.addWidget(self.sync_button)
        self.clipboard_button = QToolButton()
        self.clipboard_button.setIconSize(QSize(30, 30))
        self.clipboard_button.setIcon(QIcon(os.path.join("icons", "ic_action_copy.png")))
        self.clipboard_button.setStyleSheet("border: 0px;")
        self.clipboard_button.setToolTip("in die Zwischenablage")
        self.clipboard_button.clicked.connect(self.copy_to_clipboard)
        self.clipboard_button.setVisible(False)
        layout.addWidget(self.clipboard_button)

    # noinspection PyUnresolvedReferences
    def create_main_area(self, layout):
        # Master password
        master_password_label = QLabel("&Master-Passwort:")
        self.master_password_edit = QLineEdit()
        self.master_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.master_password_edit.textChanged.connect(self.masterpassword_changed)
        self.master_password_edit.returnPressed.connect(self.move_focus)
        self.master_password_edit.editingFinished.connect(self.masterpassword_entered)
        self.master_password_edit.setMaximumHeight(28)
        master_password_label.setBuddy(self.master_password_edit)
        layout.addWidget(master_password_label)
        layout.addWidget(self.master_password_edit)
        # Domain
        domain_label = QLabel("&Domain:")
        self.domain_edit = QComboBox()
        self.domain_edit.setEditable(True)
        self.domain_edit.textChanged.connect(self.domain_changed)
        self.domain_edit.currentIndexChanged.connect(self.domain_changed)
        self.domain_edit.lineEdit().editingFinished.connect(self.domain_entered)
        self.domain_edit.lineEdit().returnPressed.connect(self.move_focus)
        self.domain_edit.setMaximumHeight(28)
        domain_label.setBuddy(self.domain_edit)
        layout.addWidget(domain_label)
        layout.addWidget(self.domain_edit)
        # Username
        self.username_label = QLabel("&Username:")
        self.username_label.setVisible(False)
        self.username_edit = QLineEdit()
        self.username_edit.textChanged.connect(self.username_changed)
        self.username_edit.returnPressed.connect(self.move_focus)
        self.username_edit.setMaximumHeight(28)
        self.username_edit.setVisible(False)
        self.username_label.setBuddy(self.username_edit)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        # Password strength
        self.strength_label = QLabel("&Passwortstärke:")
        self.strength_label.setVisible(False)
        self.strength_selector = PasswordStrengthSelector()
        self.strength_selector.set_min_length(4)
        self.strength_selector.set_max_length(36)
        self.strength_selector.setMinimumHeight(60)
        self.strength_selector.set_length(12)
        self.strength_selector.set_complexity(6)
        self.strength_selector.strength_changed.connect(self.strength_changed)
        self.strength_selector.setVisible(False)
        self.strength_label.setBuddy(self.strength_selector)
        layout.addWidget(self.strength_label)
        layout.addWidget(self.strength_selector)
        # Password
        self.password_label = QLabel("&Passwort:")
        self.password_label.setVisible(False)
        self.password = QLabel()
        self.password.setTextFormat(Qt.PlainText)
        self.password.setAlignment(Qt.AlignCenter)
        self.password.setFont(QFont("Helvetica", 18, QFont.Bold))
        self.password.setVisible(False)
        self.password_label.setBuddy(self.password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password)

    def set_masterpassword(self, masterpassword):
        self.master_password_edit.setText(masterpassword)

    def set_domain(self, domain):
        self.domain_edit.lineEdit().setText(domain)

    def closeEvent(self, *args, **kwargs):
        settings = QSettings()
        settings.setValue("MainWindow/size", self.size())
        settings.setValue("MainWindow/pos", self.pos())
        settings.sync()

    def masterpassword_changed(self):
        self.kgk_manager.reset()
        self.decrypt_kgk_task = None
        self.clipboard_button.setVisible(False)
        if len(self.master_password_edit.text()) > 0:
            self.sync_button.setVisible(True)
        else:
            self.sync_button.setVisible(False)

    def masterpassword_entered(self):
        if len(self.master_password_edit.text()) > 0 and not self.decrypt_kgk_task:
            self.kgk_manager.get_kgk_crypter_salt()
            self.decrypt_kgk_task = DecryptKgkTask(
                self.master_password_edit.text(),
                self.preference_manager,
                self.kgk_manager,
                self.settings_manager,
                self.domain_edit)

    def set_visibilities(self):
        if len(self.domain_edit.lineEdit().text()) > 0:
            self.username_label.setVisible(True)
            self.username_edit.setVisible(True)
            self.strength_label.setVisible(True)
            self.strength_selector.setVisible(True)
            self.password_label.setVisible(True)
            self.password.setVisible(True)
        else:
            self.username_label.setVisible(False)
            self.username_edit.setVisible(False)
            self.strength_label.setVisible(False)
            self.strength_selector.setVisible(False)
            self.password_label.setVisible(False)
            self.password.setVisible(False)
            self.clipboard_button.setVisible(False)

    def domain_changed(self):
        self.setting_dirty = True
        self.password.setText("")
        self.clipboard_button.setVisible(False)
        self.set_visibilities()
        if self.kgk_manager.has_kgk() and (not self.decrypt_kgk_task or not self.decrypt_kgk_task.is_running()) and \
           len(self.domain_edit.lineEdit().text()) > 0 and \
           self.domain_edit.lineEdit().text() in self.settings_manager.get_domain_list():
            self.domain_entered()

    def domain_entered(self):
        self.setting_dirty = self.domain_edit.lineEdit().text() not in self.settings_manager.get_domain_list()
        self.setting = self.settings_manager.get_setting(self.domain_edit.lineEdit().text())
        self.username_edit.blockSignals(True)
        self.username_edit.setText(self.setting.get_username())
        self.username_edit.blockSignals(False)
        self.strength_selector.blockSignals(True)
        self.strength_selector.set_length(self.setting.get_length())
        self.strength_selector.set_complexity(self.setting.get_complexity())
        self.strength_selector.set_extra_count(len(self.setting.get_extra_character_set()))
        self.strength_selector.blockSignals(False)
        self.generate_password()

    def move_focus(self):
        line_edits = [self.master_password_edit, self.domain_edit, self.username_edit]
        for i, edit in enumerate(line_edits):
            if edit.hasFocus() and i + 1 < len(line_edits):
                line_edits[i + 1].setFocus()
                return True
        self.generate_button.setFocus()

    def generate_password(self):
        if not self.kgk_manager.has_kgk():
            self.kgk_manager.create_new_kgk()
            self.kgk_manager.create_and_save_new_kgk_block()
        if not self.kgk_manager.kgk_crypter or not self.kgk_manager.salt:
            self.kgk_manager.get_kgk_crypter(self.master_password_edit.text().encode('utf-8'),
                                             self.kgk_manager.get_kgk_crypter_salt())
        if self.setting_dirty:
            self.setting.new_salt()
            self.setting.calculate_template()
        self.settings_manager.set_setting(self.setting)
        if not self.setting.get_legacy_password():
            generator = CtSesam(self.setting.get_domain(),
                                self.setting.get_username(),
                                self.kgk_manager.get_kgk(),
                                self.setting.get_salt(),
                                self.setting.get_iterations())
            password = generator.generate(self.setting)
        else:
            password = self.setting.get_legacy_password()
        self.password.setText(password)
        self.password.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.clipboard_button.setVisible(True)
        self.settings_manager.store_local_settings(self.kgk_manager)
        self.setting_dirty = False

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.password.text())

    def username_changed(self):
        if self.setting:
            if self.setting.get_username() != self.username_edit.text():
                self.setting.set_username(self.username_edit.text())
                self.setting_dirty = True
            self.generate_password()

    def strength_changed(self, complexity, length):
        if self.setting:
            if self.setting.get_length() != length:
                self.setting.set_length(length)
                self.setting_dirty = True
            if self.setting.get_complexity() != complexity:
                self.setting.set_complexity(complexity)
                self.setting_dirty = True
            self.generate_password()

    def migrate_local_domains(self, new_kgk_manager):
        for domain in self.settings_manager.get_domain_list():
            setting = self.settings_manager.get_setting(domain)
            generator = CtSesam(setting.get_domain(),
                                setting.get_username(),
                                self.kgk_manager.get_kgk(),
                                setting.get_salt(),
                                setting.get_iterations())
            setting.set_legacy_password(generator.generate(setting))
            self.settings_manager.set_setting(setting)
        self.kgk_manager = new_kgk_manager
        self.settings_manager.store_local_settings(self.kgk_manager)

    # noinspection PyUnresolvedReferences
    def sync_clicked(self):
        self.masterpassword_entered()
        if not self.settings_manager.sync_manager.has_settings():
            self.show_sync_settings()
        else:
            pull_successful, data = self.settings_manager.sync_manager.pull()
            if pull_successful and len(data) > 0:
                remote_kgk_manager = KgkManager()
                remote_kgk_manager.update_from_blob(self.master_password_edit.text().encode('utf-8'), b64decode(data))
                if len(self.preference_manager.get_kgk_block()) == 112 and \
                   remote_kgk_manager.has_kgk() and self.kgk_manager.has_kgk() and \
                   self.kgk_manager.get_kgk() != remote_kgk_manager.get_kgk():
                    if len(self.settings_manager.get_domain_list()) > 0:
                        print("Lokal und auf dem Server gibt es unterschiedliche KGKs. Das ist ein Problem!")
                    self.migrate_local_domains(remote_kgk_manager)
                else:
                    if len(self.preference_manager.get_kgk_block()) != 112:
                        self.kgk_manager = remote_kgk_manager
                        self.kgk_manager.set_preference_manager(self.preference_manager)
                        self.kgk_manager.store_local_kgk_block()
                    self.settings_manager.update_from_export_data(remote_kgk_manager, b64decode(data))
                    self.domain_edit.blockSignals(True)
                    current_domain = self.domain_edit.lineEdit().text()
                    for i in reversed(range(self.domain_edit.count())):
                        self.domain_edit.removeItem(i)
                    self.domain_edit.insertItems(0, self.settings_manager.get_domain_list())
                    self.domain_edit.blockSignals(False)
                    self.domain_edit.setEditText(current_domain)
            self.settings_manager.store_settings(self.kgk_manager)

    # noinspection PyUnresolvedReferences
    def show_sync_settings(self, url=None, username=None, password=None):
        self.settings_window = SettingsWindow(
            self.settings_manager.sync_manager,
            self.nam,
            url=self.settings_manager.sync_manager.server_address,
            username=self.settings_manager.sync_manager.username,
            password=self.settings_manager.sync_manager.password,
            certificate=self.settings_manager.sync_manager.certificate)
        self.settings_window.finished.connect(self.sync_clicked)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate domain passwords from your masterpassword.")
    parser.add_argument('-u', '--update-sync-settings',
                        action='store_const', const=True,
                        help="Ask for server settings before synchronization.")
    parser.add_argument('--master-password', help="Prefill the masterpassword field.")
    parser.add_argument('-d', '--domain', help="Prefill the domain field.")
    args = parser.parse_args()
    app = QApplication([])
    QCoreApplication.setOrganizationName("c't")
    QCoreApplication.setOrganizationDomain("ct.de")
    QCoreApplication.setApplicationName("ctSESAM-pyside")
    window = MainWindow()
    if type(args.master_password) is str and args.master_password:
        window.set_masterpassword(args.master_password)
        window.masterpassword_changed()
        window.masterpassword_entered()
    if type(args.domain) is str and args.domain:
        window.set_domain(args.domain)
        window.domain_changed()
    if args.update_sync_settings:
        window.show_sync_settings()
    app.exec_()
