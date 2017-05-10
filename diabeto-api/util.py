
class Range(object):
    ''' Represents a range given by two values
    @lo     the lower value
    @hi     the higher value
    '''

    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def contains(self, v):
        ''' Returns True iff the given value is within the range
        @v  the value to test
        '''
        return self.lo <= v and v <= self.hi

    def __str__(self):
        return format('%s - %s' % (self.lo,self.hi))
