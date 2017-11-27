
import time
from threading import Thread

def every(delay_in_seconds, fun):
    """
    Invoke a funcction with a delay of delay_in_seconds between the end of one
    invocation and the start of the next
    """

    def go():
        while True:
            do_continue = fun()
            if not do_continue:
                break
            time.sleep(delay_in_seconds)

    thread = Thread(target = go)
    thread.start()
    return thread

