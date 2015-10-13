#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys
from PySide.QtGui import QApplication, QWidget, QBoxLayout, QFont, QIcon
from PySide.QtGui import QLabel, QLineEdit, QCheckBox, QSlider, QPushButton
from PySide.QtCore import Qt

from password_generator import CtSesam
from preference_manager import PreferenceManager
from kgk_manager import KgkManager
from password_settings_manager import PasswordSettingsManager
from crypter import Crypter


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
        # Master password
        self.master_password_label = QLabel("&Master-Passwort:")
        self.maser_password_edit = QLineEdit()
        self.maser_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        #self.maser_password_edit.textChanged.connect(self.reset_iterations)
        self.maser_password_edit.returnPressed.connect(self.move_focus)
        self.maser_password_edit.setMaximumHeight(28)
        self.master_password_label.setBuddy(self.maser_password_edit)
        self.layout.addWidget(self.master_password_label)
        self.layout.addWidget(self.maser_password_edit)
        # Domain
        self.domain_label = QLabel("&Domain:")
        self.domain_edit = QLineEdit()
        #self.domain_edit.textChanged.connect(self.reset_iterations)
        self.domain_edit.returnPressed.connect(self.move_focus)
        self.domain_edit.setMaximumHeight(28)
        self.domain_label.setBuddy(self.domain_edit)
        self.layout.addWidget(self.domain_label)
        self.layout.addWidget(self.domain_edit)
        # Username
        self.username_label = QLabel("&Username:")
        self.username_edit = QLineEdit()
        #self.username_edit.textChanged.connect(self.reset_iterations)
        self.username_edit.returnPressed.connect(self.move_focus)
        self.username_edit.setMaximumHeight(28)
        self.username_label.setBuddy(self.username_edit)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_edit)
        # Checkboxes
        self.special_characters_checkbox = QCheckBox("Sonderzeichen")
        self.special_characters_checkbox.setChecked(True)
        #self.special_characters_checkbox.stateChanged.connect(self.reset_iterations)
        self.layout.addWidget(self.special_characters_checkbox)
        self.letters_checkbox = QCheckBox("Buchstaben")
        self.letters_checkbox.setChecked(True)
        #self.letters_checkbox.stateChanged.connect(self.reset_iterations)
        self.layout.addWidget(self.letters_checkbox)
        self.digits_checkbox = QCheckBox("Zahlen")
        self.digits_checkbox.setChecked(True)
        #self.digits_checkbox.stateChanged.connect(self.reset_iterations)
        self.layout.addWidget(self.digits_checkbox)
        # Length slider
        self.length_label = QLabel("&Länge:")
        self.length_display = QLabel()
        self.length_label_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.length_label_layout.addWidget(self.length_label)
        self.length_label_layout.addWidget(self.length_display)
        self.length_label_layout.addStretch()
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setMinimum(4)
        self.length_slider.setMaximum(20)
        self.length_slider.setPageStep(1)
        self.length_slider.setValue(10)
        self.length_display.setText(str(self.length_slider.sliderPosition()))
        self.length_slider.valueChanged.connect(self.length_slider_changed)
        self.length_label.setBuddy(self.length_slider)
        self.layout.addLayout(self.length_label_layout)
        self.layout.addWidget(self.length_slider)
        # Button
        self.generate_button = QPushButton("Erzeugen")
        self.generate_button.clicked.connect(self.generate_password)
        self.generate_button.setAutoDefault(True)
        self.layout.addWidget(self.generate_button)
        # Password
        self.password_label = QLabel("&Passwort:")
        self.password = QLabel()
        self.password.setTextFormat(Qt.PlainText)
        self.password.setAlignment(Qt.AlignCenter)
        self.password.setFont(QFont("Helvetica", 18, QFont.Bold))
        self.password_label.setBuddy(self.password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password)
        # Window layout
        self.layout.addStretch()
        self.setGeometry(0, 30, 300, 400)
        self.setWindowTitle("c't SESAM")
        self.maser_password_edit.setFocus()
        self.show()

    def length_slider_changed(self):
        self.length_display.setText(str(self.length_slider.sliderPosition()))

    def move_focus(self):
        line_edits = [self.maser_password_edit, self.domain_edit, self.username_edit]
        for i, edit in enumerate(line_edits):
            if edit.hasFocus() and i + 1 < len(line_edits):
                line_edits[i + 1].setFocus()
                return True
        self.generate_button.setFocus()

    def generate_password(self):
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
                password=self.maser_password_edit.text(),
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
