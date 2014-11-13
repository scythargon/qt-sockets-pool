import threading
from PyQt4 import QtCore
import time


def run():
    count = 0
    while count < 3:
        time.sleep(1)
        print "Increasing"
        count += 1

class AThread(QtCore.QThread):

    def run(self):
    	run()

def create_qthread():
    thread = AThread()
    thread.start()
    #app = QtCore.QCoreApplication([])
    run()


t = threading.Thread(target = create_qthread)
t.start()