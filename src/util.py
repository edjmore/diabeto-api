import abc,json


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
        return format('%s-%s' % (self.lo,self.hi))


class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


class ICsvObj(object):
    ''' Interface for classes that can be exported to CSV strings
    '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractclassmethod
    def get_csv_headers(cls):
        raise NotImplementedError

    @abc.abstractmethod
    def to_csv(self):
        return self.__str__()


class IJsonObj(object):
    ''' Interface for classes that can be converted to JSON
    '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class AbstractDiabetoError(Exception):
    __metaclass__ = abc.ABCMeta

    def __init__(self, msg, status_code=None, payload=None):
        Exception.__init__(self)
        self.msg = msg
        self.status_code = self.__class__.__default_status_code() if status_code is None else status_code
        self.payload = payload

    @abc.abstractclassmethod
    def __default_status_code(cls):
        return 400

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['msg'] = self.msg
        return rv
