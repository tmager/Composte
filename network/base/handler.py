
class Stateful:
def __init__(self, handler, state):
    """
    handler must be callable in the following fashion:
        handler(message, state)
    handler must return the following:
        (result, new_state)
    """
    self.__handler = handler
    self.__state = state

    def __call__(self, message):
        (res, new_state) = self.__handler(message, self.__state)
        self.__state = new_state
        return res

