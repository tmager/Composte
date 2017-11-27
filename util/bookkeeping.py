
class Pool:
    """
    Pool objects to hopefully reduce the number of copies floating around in
    memory. Does some manual reference counting, which may be a bad idea.
    """

    __objects = {}

    def __init__(self):
        pass

    def get(self, tag, contructor):
        have = Pool.__objects.get(tag, None)

        if have is None:
            Pool.__objects[tag] = (constructor(), 1)
        else:
            (obj, count) = have
            Pool.__objects[tag] = (obj, count + 1)

        return Pool.__objects[tag]

    def put(self, tag):
        have = Pool.__objects.get(tag, None)

        if have is None:
            return

        (obj, count) = have

        if count > 1:
            Pool.__objects[tag] = (obj, count - 1)
        elif count == 1:
            del Pool.__objects[tag]

        return count

