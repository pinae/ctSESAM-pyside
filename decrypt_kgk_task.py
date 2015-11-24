#!/usr/bin/python3
# -*- coding: utf-8 -*-

from multiprocessing import Process, Queue
from crypter import Crypter


class DecryptKgkTask(object):
    def __init__(self, password, preference_manager, kgk_manager, settings_manager, domain_edit):
        salt = preference_manager.get_salt()
        self.kgk_manager = kgk_manager
        self.preference_manager = preference_manager
        self.settings_manager = settings_manager
        self.domain_edit = domain_edit
        self.queue = Queue()
        self.process = Process(
            target=DecryptKgkTask.create_key_iv,
            args=(self.queue, password.encode('utf-8'), salt,))
        self.process.start()
        self.post_execute()

    @staticmethod
    def create_key_iv(queue, password, salt):
        queue.put(Crypter.createIvKey(password, salt))

    def post_execute(self):
        key_iv = self.queue.get()
        self.process.join()
        self.kgk_manager.decrypt_kgk(self.preference_manager.get_kgk_block(), Crypter(key_iv))
        self.settings_manager.load_local_settings(self.kgk_manager)
        for i in reversed(range(self.domain_edit.count())):
            self.domain_edit.removeItem(i)
        self.domain_edit.insertItems(0, self.settings_manager.get_domain_list())
        self.domain_edit.textChanged.emit(self.domain_edit.lineEdit().text())

    def is_running(self):
        return self.process.is_alive()
