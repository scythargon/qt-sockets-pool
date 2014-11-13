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

        for x in range(self.numThreads):
            t = threading.Thread(target = self.process_request_thread)
            t.setDaemon(1)
            t.start()

        # server main loop
        while True:
            self.handle_request()
            
        self.server_close()

    
    def process_request_thread(self):
        '''
        obtain request from queue instead of directly from server socket
        '''
        while True:
            ThreadingMixIn.process_request_thread(self, *self.requests.get())

    
    def handle_request(self):
        '''
        simply collect requests and put them on the queue for the workers.
        '''
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            self.requests.put((request, client_address))

class EchoRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # Echo the back to the client
        data = self.request.recv(1024)
        time.sleep(5)
        self.request.send(data.upper())
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
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        httpd.serve_forever()

    test()