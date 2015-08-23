import threading


class MyThread(threading.Thread):
    def run(self,x):
        self.x = x
        for i in xrange(100):
            print self.x

    def changex(self,x):
        self.x = x

a = MyThread()
a.start(5)
a.changex(6)
