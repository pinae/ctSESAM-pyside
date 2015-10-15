#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys
from PySide.QtGui import QApplication, QWidget, QBoxLayout, QFont, QIcon
from PySide.QtGui import QLabel, QLineEdit, QCheckBox, QSlider, QPushButton
from PySide.QtCore import Qt
from password_strength_selector import PasswordStrengthSelector

from password_generator import CtSesam
from preference_manager import PreferenceManager
from kgk_manager import KgkManager
from password_settings_manager import PasswordSettingsManager
from crypter import Crypter
from decrypt_kgk_task import DecryptKgkTask


class MainWindow(QWidget):
    # noinspection PyUnresolvedReferences
    def __init__(self, clipboard):
        super().__init__()
        self.clipboard = clipboard
        self.setWindowIcon(QIcon('Logo_rendered_edited.png'))
        self.layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.preference_manager = PreferenceManager()
        self.kgk_manager = KgkManager()
        self.kgk_manager.set_preference_manager(self.preference_manager)
        self.settings_manager = PasswordSettingsManager(self.preference_manager)
        self.setting = None
        self.setting_dirty = False
        self.decrypt_kgk_task = None
        # Master password
        self.master_password_label = QLabel("&Master-Passwort:")
        self.master_password_edit = QLineEdit()
        self.master_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.master_password_edit.textChanged.connect(self.masterpassword_changed)
        self.master_password_edit.returnPressed.connect(self.move_focus)
        self.master_password_edit.editingFinished.connect(self.masterpassword_entered)
        self.master_password_edit.setMaximumHeight(28)
        self.master_password_label.setBuddy(self.master_password_edit)
        self.layout.addWidget(self.master_password_label)
        self.layout.addWidget(self.master_password_edit)
        # Domain
        self.domain_label = QLabel("&Domain:")
        self.domain_edit = QLineEdit()
        self.domain_edit.textChanged.connect(self.domain_changed)
        self.domain_edit.returnPressed.connect(self.move_focus)
        self.domain_edit.setMaximumHeight(28)
        self.domain_label.setBuddy(self.domain_edit)
        self.layout.addWidget(self.domain_label)
        self.layout.addWidget(self.domain_edit)
        # Username
        self.username_label = QLabel("&Username:")
        self.username_label.setVisible(False)
        self.username_edit = QLineEdit()
        self.username_edit.textChanged.connect(self.username_changed)
        self.username_edit.returnPressed.connect(self.move_focus)
        self.username_edit.setMaximumHeight(28)
        self.username_edit.setVisible(False)
        self.username_label.setBuddy(self.username_edit)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_edit)
        # Password strength
        self.strength_label = QLabel("&Passwortstärke:")
        self.strength_label.setVisible(False)
        self.strength_selector = PasswordStrengthSelector()
        self.strength_selector.set_min_length(4)
        self.strength_selector.set_max_length(36)
        self.strength_selector.setMinimumHeight(60)
        self.strength_selector.strength_changed.connect(self.strength_changed)
        self.strength_selector.setVisible(False)
        self.strength_label.setBuddy(self.strength_selector)
        self.layout.addWidget(self.strength_label)
        self.layout.addWidget(self.strength_selector)
        # Button
        self.generate_button = QPushButton("Erzeugen")
        self.generate_button.clicked.connect(self.generate_password)
        self.generate_button.setAutoDefault(True)
        self.generate_button.setVisible(False)
        self.layout.addWidget(self.generate_button)
        # Password
        self.password_label = QLabel("&Passwort:")
        self.password_label.setVisible(False)
        self.password = QLabel()
        self.password.setTextFormat(Qt.PlainText)
        self.password.setAlignment(Qt.AlignCenter)
        self.password.setFont(QFont("Helvetica", 18, QFont.Bold))
        self.password.setVisible(False)
        self.password_label.setBuddy(self.password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password)
        # Window layout
        self.layout.addStretch()
        self.setGeometry(0, 30, 300, 400)
        self.setWindowTitle("c't SESAM")
        self.master_password_edit.setFocus()
        self.show()

    def masterpassword_changed(self):
        self.kgk_manager.reset()
        self.decrypt_kgk_task = None

    def masterpassword_entered(self):
        if not self.decrypt_kgk_task:
            self.decrypt_kgk_task = DecryptKgkTask(
                self.master_password_edit.text(),
                self.preference_manager,
                self.kgk_manager,
                self.settings_manager)

    def domain_changed(self):
        if len(self.domain_edit.text()) > 0:
            self.username_label.setVisible(True)
            self.username_edit.setVisible(True)
            self.strength_label.setVisible(True)
            self.strength_selector.setVisible(True)
            self.generate_button.setVisible(self.setting_dirty)
            self.password_label.setVisible(True)
            self.password.setVisible(True)
            if self.kgk_manager.has_kgk() and self.decrypt_kgk_task and not self.decrypt_kgk_task.is_running():
                if self.domain_edit.text() in self.settings_manager.get_domain_list():
                    self.domain_entered()
        else:
            self.username_label.setVisible(False)
            self.username_edit.setVisible(False)
            self.strength_label.setVisible(False)
            self.strength_selector.setVisible(False)
            self.generate_button.setVisible(False)
            self.password_label.setVisible(False)
            self.password.setVisible(False)

    def domain_entered(self):
        self.setting = self.settings_manager.get_setting(self.domain_edit.text())
        self.username_edit.setText(self.setting.get_username())
        self.strength_selector.set_length(self.setting.get_length())
        self.strength_selector.set_complexity(self.setting.get_complexity())
        self.generate_password()

    def move_focus(self):
        line_edits = [self.master_password_edit, self.domain_edit, self.username_edit]
        for i, edit in enumerate(line_edits):
            if edit.hasFocus() and i + 1 < len(line_edits):
                line_edits[i + 1].setFocus()
                return True
        self.generate_button.setFocus()

    def generate_password(self):
        generator = CtSesam(self.setting.get_domain(),
                            self.setting.get_username(),
                            self.kgk_manager.get_kgk(),
                            self.setting.get_salt(),
                            self.setting.get_iterations())
        password = generator.generate(self.setting)
        self.password.setText(password)
        self.password.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.clipboard.setText(password)

    def username_changed(self):
        if self.setting:
            self.setting.set_username(self.username_edit.text())
            self.setting_dirty = True
            self.generate_password()

    def strength_changed(self, complexity, length):
        if self.setting:
            self.setting.set_length(length)
            self.setting.set_complexity(complexity)
            self.setting_dirty = True
            self.generate_password()



    def old_generate_password(self):
        if len(self.domain_edit.text()) <= 0:
            self.message_label.setText(
                '<span style="font-size: 10px; color: #aa0000;">Bitte geben Sie eine Domain an.</span>')
            self.message_label.setVisible(True)
            return False
        if not self.letters_checkbox.isChecked() and \
           not self.digits_checkbox.isChecked() and \
           not self.special_characters_checkbox.isChecked():
            self.message_label.setText(
                '<span style="font-size: 10px; color: #aa0000;">Bei den aktuellen Einstellungen ' +
                'kann kein Passwort berechnet werden.</span>')
            self.message_label.setVisible(True)
            return False
        setting = self.settings_manager.get_setting(self.domain_edit.text())
        if not self.kgk_manager.has_kgk():
            self.kgk_manager.create_new_kgk()
            self.kgk_manager.create_and_save_new_kgk_block(self.kgk_manager.get_kgk_crypter(
                password=self.master_password_edit.text(),
                salt=Crypter.createSalt()))
        generator = CtSesam(setting.get_domain(),
                            setting.get_username(),
                            self.kgk_manager.get_kgk(),
                            setting.get_salt(),
                            setting.get_iterations())
        password = generator.generate(setting)
        self.password.setText(password)
        self.password.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.clipboard.setText(password)
        self.message_label.setText(
            '<span style="font-size: 10px; color: #888888;">Das Passwort wurde ' + str(self.iterations) +
            ' mal gehasht <br />und in die Zwischenablage kopiert.</span>')
        self.message_label.setVisible(True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate domain passwords from your masterpassword.")
    parser.add_argument('-n', '--no-sync',
                        action='store_const', const=True,
                        help="Do not synchronize with a server.")
    parser.add_argument('-u', '--update-sync-settings',
                        action='store_const', const=True,
                        help="Ask for server settings before synchronization.")
    parser.add_argument('--master-password', help="Prefill the masterpassword field.")
    parser.add_argument('-d', '--domain', help="Prefill the domain field.")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    window = MainWindow(app.clipboard())
    app.exec_()
