import time


class maxdict(dict):
    """
    a dict with maxlength, deletes the least recently used (get or set)
    item
    """
    def __init__(self, max_length=512):
        dict.__init__(self)
        self._stack = []
        self._max_length = max_length

    def __getitem__(self, key):
        self._stack.remove(key)
        self._stack.append(key)
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if not dict.__contains__(self, key):
            if len(self._stack) >= self._max_length:
                self.__delitem__(self._stack.pop(0))
            self._stack.append(key)
        else:
            self._stack.remove(key)
            self._stack.append(key)

        dict.__setitem__(self, key, value)


class AbusiveClientFilter(object):
    # it could very well be 1000, it's the 10's of thosands that's bad
    # and I doubt legitimate use vill ever exeed this number.
    throttle = 50

    # slips a package through every 30 secounds or so at decay=10
    decay = 10

    counts = maxdict()

    def _compute_throttle(self, client):
        # client = (count, timestamp)
        new_counts = client[0] - (int(time.time() - client[1])) / self.decay
        if new_counts < 0:
            new_counts = 0
        return new_counts

    def filter_now(self, host):
        """
        a new package, filter them if too many packages is received over
        some time

        returns True if blocked
        """

        if host in self.counts:
            client = self.counts[host]
            client_count = self._compute_throttle(client) + 1
            if (client_count > self.throttle):  # blocked
                self.counts[host] = (client_count, client[1])
                return True
            else:
                self.counts[host] = (client_count, time.time())
                return False
        else:
            self.counts[host] = (0, time.time())
            return False
