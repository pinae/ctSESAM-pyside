# ctSESAM-pyside
c't SESAM password manager with Qt interface

[![License](https://img.shields.io/badge/license-GPLv3-blue.svg "read the terms of the GPLv3")](http://choosealicense.com/licenses/gpl-3.0/)
[![Documentation](https://readthedocs.org/projects/ctsesam-python/badge/ "go to the documentation")](http://ctsesam-python.readthedocs.org/en/latest)
[![Build Status](https://travis-ci.org/pinae/ctSESAM-pyside.svg?branch=master)](https://travis-ci.org/pinae/ctSESAM-pyside)

Installation
============

Make sure you have installed Pyside.

On Linux do ``pip install pyside``. On Windows its ``python -m pip install pyside``. If python is not in your path 
you have to do this from the Python directory.

Usage
=====

Run c't SESAM with ``python3 ctSESAM.py``.

The focus will land in the masterpassword field. You have to enter your masterpassword before doing anything else.

If you started the application the first time you have two options:

 1. Load settings from a sync server using the sync button in the header bar.
 2. Create a new set of settings.

The first path leads you to a window where you can enter the url and credentials for your sync server. A button in 
this dialogue lets you download the certificate for your server. Self-signed CAs are perfectly ok as you always have
to check the fingerprint of the certificate. After entering the settings you can go back with the back button in the
upper left corner. Synchronization of the settings starts when the window closes. You only have to enter the sync
settings once. They are saved with all other settings in an encrypted container in ``~/.ctSESAM.pws``.

If you have settings they pop up in the combo box for the domain. You can also enter any domain you want to add in
this field.

The username is completely optional but may help you to remember different sets of credentials.

The strength field is self-explanatory once you start clicking in it. To the right the passwords get longer to the
top they consist of more different characters. The color helps you not to pick insecure passwords. 10 characters 
should be your minimum length for numerical pins (the bottom line) they should be much longer.

While dragging the selection in the strength field or changing the username a new salt is generated for every change.
If you don't like the password just change something and you get another one. Please be careful not to change 
passwords you are already using somewhere. There is no backup copy of the old settings. All changes are saved 
immediately.

After a password was generated it can be copied to the clipboard with the copy button in the header bar.
