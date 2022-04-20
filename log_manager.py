import logging
import threading
import queue

class LogQueue():
    logQueue = queue.Queue()
    def __init__(self) -> None:
        pass


class BotLogger(logging.Logger):

    def __init__(self, name, level = logging.NOTSET):
        self._count = 0
        #self._countLock = threading.Lock()
        self.q = queue.Queue()       

        return super(BotLogger, self).__init__(name, level)        

    @property
    def is_queue_empty(self):
        print(self.q.empty())
        return self.q.empty()


    def info(self, msg: object, *args: object) -> None:
        self.q.put(msg)
        
        return super(BotLogger, self).info(msg, *args)


logging.setLoggerClass(BotLogger)
logging.basicConfig()

logger = logging.getLogger("logger")

logQ = LogQueue.logQueue
logQ.put(1)
logQ.put(2)
logQ.put(3)
print(logQ.get())

anotherLogQ = LogQueue.logQueue
print(anotherLogQ.empty())

print(anotherLogQ.get())

print(anotherLogQ.get())

print(anotherLogQ.empty())
