#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PySide.QtCore import QUrl, QByteArray
from PySide.QtNetwork import QNetworkAccessManager, QNetworkRequest, QSslConfiguration, QSslSocket, QNetworkSession, QNetworkConfigurationManager
from base64 import b64encode
from multiprocessing import Process, Queue


class GetCertificateTask:
    ssl_errors = None

    def __init__(self, url, username, password):
        print("GetCertificateTask started ...")
        queue = Queue()
        #process = Process(
        #        target=GetCertificateTask.get_certificate_chain,
        #        args=(self, queue, url, username, password,))
        #process.start()
        #self.reply = queue.get()
        #print(self.reply)
        #self.certificate = queue.get()
        #process.join()
        self.get_certificate_chain(queue, url, username, password)

    # noinspection PyUnresolvedReferences
    def get_certificate_chain(self, queue, url, username, password):
        nam = QNetworkAccessManager()
        print(QNetworkConfigurationManager().allConfigurations())
        print(QNetworkSession(QNetworkConfigurationManager().defaultConfiguration()).State())
        print(QNetworkSession(QNetworkConfigurationManager().defaultConfiguration()).waitForOpened(1000))
        print(QNetworkSession(QNetworkConfigurationManager().defaultConfiguration()).State())
        nam.setNetworkAccessible(QNetworkAccessManager.Accessible)
        print(nam.NetworkAccessibility())
        print("Accessing: " + url + "ajax/read.php")
        req = QNetworkRequest(QUrl(url + "ajax/read.php"))
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
        req.setRawHeader("User-Agent", "ctSESAM Pyside")
        req.setRawHeader("Authorization", b64encode((username + ":" + password).encode('utf-8')))
        ssl_config = QSslConfiguration().defaultConfiguration()
        ssl_config.setCiphers(QSslSocket().supportedCiphers())
        req.setSslConfiguration(ssl_config)
        nam.finished.connect(self.on_finished)
        nam.sslErrors.connect(self.on_ssl_errors)
        nam.authenticationRequired.connect(self.test)
        nam.networkAccessibleChanged.connect(self.test)
        nam.networkSessionConnected.connect(self.test)
        nam.proxyAuthenticationRequired.connect(self.test)
        self.test("arr")
        nam.post(req, QByteArray())

    def test(self, string):
        print("Test")
        print(string)

    def on_finished(self, reply):
        print("finished")
        print(reply.sslConfiguration().peerCertificateChain())

    def on_ssl_errors(self, reply, errors):
        print("SSL errors")
        print(errors)
        print(reply.sslConfiguration().peerCertificateChain())
        #self.ssl_errors = errors
        #reply.ignoreSslErrors(errors)
