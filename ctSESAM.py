#!/usr/bin/python3
# -*- coding: utf-8 -*-

from hashlib import pbkdf2_hmac

import sys
from PySide.QtGui import QApplication, QWidget, QBoxLayout, QFont, QIcon
from PySide.QtGui import QLabel, QLineEdit, QCheckBox, QSlider, QPushButton
from PySide.QtCore import Qt


class MainWindow(QWidget):
    # noinspection PyUnresolvedReferences
    def __init__(self, clipboard):
        super().__init__()
        self.clipboard = clipboard
        self.setWindowIcon(QIcon('Logo_rendered_edited.png'))
        self.layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.generator = CtSesam()
        self.iterations = 4096
        # Master password
        self.master_password_label = QLabel("&Master-Passwort:")
        self.maser_password_edit = QLineEdit()
        self.maser_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.maser_password_edit.textChanged.connect(self.reset_iterations)
        self.maser_password_edit.returnPressed.connect(self.move_focus)
        self.maser_password_edit.setMaximumHeight(28)
        self.master_password_label.setBuddy(self.maser_password_edit)
        self.layout.addWidget(self.master_password_label)
        self.layout.addWidget(self.maser_password_edit)
        # Domain
        self.domain_label = QLabel("&Domain:")
        self.domain_edit = QLineEdit()
        self.domain_edit.textChanged.connect(self.reset_iterations)
        self.domain_edit.returnPressed.connect(self.move_focus)
        self.domain_edit.setMaximumHeight(28)
        self.domain_label.setBuddy(self.domain_edit)
        self.layout.addWidget(self.domain_label)
        self.layout.addWidget(self.domain_edit)
        # Username
        self.username_label = QLabel("&Username:")
        self.username_edit = QLineEdit()
        self.username_edit.textChanged.connect(self.reset_iterations)
        self.username_edit.returnPressed.connect(self.move_focus)
        self.username_edit.setMaximumHeight(28)
        self.username_label.setBuddy(self.username_edit)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_edit)
        # Checkboxes
        self.special_characters_checkbox = QCheckBox("Sonderzeichen")
        self.special_characters_checkbox.setChecked(True)
        self.special_characters_checkbox.stateChanged.connect(self.reset_iterations)
        self.layout.addWidget(self.special_characters_checkbox)
        self.letters_checkbox = QCheckBox("Buchstaben")
        self.letters_checkbox.setChecked(True)
        self.letters_checkbox.stateChanged.connect(self.reset_iterations)
        self.layout.addWidget(self.letters_checkbox)
        self.digits_checkbox = QCheckBox("Zahlen")
        self.digits_checkbox.setChecked(True)
        self.digits_checkbox.stateChanged.connect(self.reset_iterations)
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
        # Iteration display
        self.message_label = QLabel()
        self.message_label.setTextFormat(Qt.RichText)
        self.message_label.setVisible(False)
        self.layout.addWidget(self.message_label)
        # Window layout
        self.layout.addStretch()
        self.setGeometry(0, 30, 300, 400)
        self.setWindowTitle("c't SESAM")
        self.maser_password_edit.setFocus()
        self.show()

    def length_slider_changed(self):
        self.length_display.setText(str(self.length_slider.sliderPosition()))
        self.reset_iterations()

    def reset_iterations(self):
        self.iterations = 4096
        self.message_label.setVisible(False)
        self.password.setText('')
        self.clipboard.setText('')

    def move_focus(self):
        line_edits = [self.maser_password_edit, self.domain_edit, self.username_edit]
        for i, edit in enumerate(line_edits):
            if edit.hasFocus() and i + 1 < len(line_edits):
                line_edits[(i + 1)].setFocus()
                return True
        self.generate_button.setFocus()

    def generate_password(self):
        if len(self.domain_edit.text()) <= 0:
            self.reset_iterations()
            self.message_label.setText(
                '<span style="font-size: 10px; color: #aa0000;">Bitte geben Sie eine Domain an.</span>')
            self.message_label.setVisible(True)
            return False
        if self.letters_checkbox.isChecked() or \
           self.digits_checkbox.isChecked() or \
           self.special_characters_checkbox.isChecked():
            self.generator.set_password_characters(
                use_letters=self.letters_checkbox.isChecked(),
                use_digits=self.digits_checkbox.isChecked(),
                use_special_characters=self.special_characters_checkbox.isChecked())
        else:
            self.reset_iterations()
            self.message_label.setText(
                '<span style="font-size: 10px; color: #aa0000;">Bei den aktuellen Einstellungen ' +
                'kann kein Passwort berechnet werden.</span>')
            self.message_label.setVisible(True)
            return False
        password = self.generator.generate(
            master_password=self.maser_password_edit.text(),
            domain=self.domain_edit.text(),
            username=self.username_edit.text(),
            length=self.length_slider.sliderPosition(),
            iterations=self.iterations
        )
        self.password.setText(password)
        self.password.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.clipboard.setText(password)
        self.message_label.setText(
            '<span style="font-size: 10px; color: #888888;">Das Passwort wurde ' + str(self.iterations) +
            ' mal gehasht <br />und in die Zwischenablage kopiert.</span>')
        self.message_label.setVisible(True)
        self.iterations += 1


class CtSesam(object):
    def __init__(self):
        self.password_characters = []
        self.set_password_characters()
        self.salt = "pepper".encode('utf-8')

    def set_password_characters(self, use_letters=True, use_digits=True, use_special_characters=True):
        if not use_letters and not use_digits and not use_special_characters:
            use_letters = True
            use_digits = True
            use_special_characters = True
        lower_case_letters = list('abcdefghijklmnopqrstuvwxyz')
        upper_case_letters = list('ABCDEFGHJKLMNPQRTUVWXYZ')
        digits = list('0123456789')
        special_characters = list('#!"§$%&/()[]{}=-_+*<>;:.')
        self.password_characters = []
        if use_letters:
            self.password_characters += lower_case_letters + upper_case_letters
        if use_digits:
            self.password_characters += digits
        if use_special_characters:
            self.password_characters += special_characters

    def convert_bytes_to_password(self, digest, length):
        number = int.from_bytes(digest, byteorder='big')
        password = ''
        while number > 0 and len(password) < length:
            password = password + self.password_characters[number % len(self.password_characters)]
            number //= len(self.password_characters)
        return password

    def generate(self, master_password, domain, username='', length=10, iterations=4096):
        hash_string = domain + username + master_password
        hashed_bytes = pbkdf2_hmac('sha512', hash_string.encode('utf-8'), self.salt, iterations)
        return self.convert_bytes_to_password(hashed_bytes, length)


app = QApplication(sys.argv)
window = MainWindow(app.clipboard())
app.exec_()
