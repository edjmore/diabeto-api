
class Range(object):
    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def contains(self, v):
        return self.lo <= v and v <= self.hi
