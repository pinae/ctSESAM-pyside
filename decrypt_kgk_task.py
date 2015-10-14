#!/usr/bin/python3
# -*- coding: utf-8 -*-

from multiprocessing import Process, Queue
from crypter import Crypter


class DecryptKgkTask:
    def __init__(self, password, preference_manager, kgk_manager, settings_manager):
        salt = preference_manager.get_salt()
        self.kgk_manager = kgk_manager
        self.preference_manager = preference_manager
        self.settings_manager = settings_manager
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

    def is_running(self):
        return self.process.is_alive()
