#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from PyQt4 import QtCore
import spynner
from SocketServer import ThreadingMixIn
import SocketServer
from Queue import Queue
import threading, socket
import time




class ThreadPoolMixIn(ThreadingMixIn):
    '''
    use a thread pool instead of a new thread on every request
    '''
    numThreads = 10
    allow_reuse_address = True  # seems to fix socket.error on server restart


    def serve_forever(self):
        '''
        Handle one request at a time until doomsday.
        '''
        # set up the threadpool
        self.requests = Queue(self.numThreads)

        # Subclassing QThread
        # http://qt-project.org/doc/latest/qthread.html
        class AThread(QtCore.QThread):

            def run(this):
                print 'Qthread is running'
                while True:
                    print 'got request'
                    ThreadingMixIn.process_request_thread(self, *self.requests.get())
        threads = []
        for x in range(self.numThreads):
            #t = threading.Thread(target = self.process_request_thread)
            #t.setDaemon(1)
            #t.start()
            thread = AThread()
            thread.start()
            threads.append(thread)
        #for x in threads:
        #    x.wait()

        # server main loop
        while True:
            self.handle_request()
        print 'wtf'    
        self.server_close()

    
    def handle_request(self):
        '''
        simply collect requests and put them on the queue for the workers.
        '''
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        print 'working'
        if self.verify_request(request, client_address):
            self.requests.put((request, client_address))

class EchoRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # Echo the message back to the client
        url = self.request.recv(1024)
        browser = spynner.Browser()
        browser.load(url, load_timeout=120)
        ret = browser.webframe.toHtml()
        ret = str(ret).replace("\00","")
        self.request.send(ret)
        return


if __name__ == '__main__':
    from SocketServer import TCPServer
    
    class ThreadedServer(ThreadPoolMixIn, TCPServer):
        pass

    def test(HandlerClass = EchoRequestHandler,
            protocol="HTTP/1.0"):
        '''
        Test: Run an HTTP server on port 8002
        '''

        port = 8002
        server_address = ('', port)

        httpd = ThreadedServer(server_address, HandlerClass)

        sa = httpd.socket.getsockname()
        browser = spynner.Browser()  # just init all the things
        browser.load('http://google.com/', load_timeout=120)
        del browser
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        httpd.serve_forever()
    app = QtCore.QCoreApplication([])
    test()