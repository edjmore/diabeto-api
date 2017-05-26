from .. import common
import datetime as dt


class LogbookEntry(common.ICsvObj):
    def __init__(self, entry_date, entry_time):
        self.entry_date = entry_date
        self.entry_time = entry_time

    @classmethod
    def get_csv_headers(cls):
        return 'entry_date,entry_time'

    def __str__(self):
        return format('%s,%s' % (
            self.entry_date.strftime('%m/%d/%Y'),
            self.entry_time.strftime('%I:%M %p'),
            ))


class OtrLogbookEntry(LogbookEntry):
    def __init__(self, entry_date, entry_time, otr_comments):
        super(OtrLogbookEntry, self).__init__(entry_date, entry_time)
        self.otr_comments = otr_comments

    @classmethod
    def get_csv_headers(cls):
        return super(OtrLogbookEntry, cls).get_csv_headers() + ',otr_comments'

    def __str__(self):
        return super(OtrLogbookEntry, self).__str__() + (',"%s"' % self.otr_comments)


class OtrGlucoseEntry(OtrLogbookEntry):
    def __init__(self, entry_date, entry_time, otr_comments, bg_value):
        super(OtrGlucoseEntry, self).__init__(entry_date, entry_time, otr_comments)
        self.bg_value = bg_value

    @classmethod
    def get_csv_headers(cls):
        return super(OtrGlucoseEntry, cls).get_csv_headers() + ',bg_value'

    def __str__(self):
        return super(OtrGlucoseEntry, self).__str__() + ',' + str(self.bg_value)


class OtrPatternEntry(OtrLogbookEntry):
    def __init__(self, entry_date, entry_time, otr_comments):
        super(OtrPatternEntry, self).__init__(entry_date, entry_time, otr_comments)

    def __str__(self):
        return super(OtrPatternEntry, self).__str__()


class FitCaloriesEntry(LogbookEntry):
    def __init__(self, entry_date, entry_time, calories):
        super(FitCaloriesEntry, self).__init__(entry_date, entry_time)
        self.calories = calories

    @classmethod
    def get_csv_headers(cls):
        return super(FitCaloriesEntry, cls).get_csv_headers() + ',calories'

    def __str__(self):
        return super(FitCaloriesEntry, self).__str__() + ',' + str(self.calories)


class FitStepsEntry(LogbookEntry):
    def __init__(self, entry_date, entry_time, steps):
        super(FitStepsEntry, self).__init__(entry_date, entry_time)
        self.steps = steps

    @classmethod
    def get_csv_headers(cls):
        return super(FitStepsEntry, cls).get_csv_headers() + ',steps'

    def __str__(self):
        return super(FitStepsEntry, self).__str__() + ',' + str(self.steps)


class FitDistanceEntry(LogbookEntry):
    def __init__(self, entry_date, entry_time, distance):
        super(FitDistanceEntry, self).__init__(entry_date, entry_time)
        self.distance = distance

    @classmethod
    def get_csv_headers(cls):
        return super(FitDistanceEntry, cls).get_csv_headers() + ',distance'

    def __str__(self):
        return super(FitDistanceEntry, self).__str__() + ',' + str(self.distance)

def get_fit_logentry_constructor(activity_metric):
    ''' Returns the appropriate Fitbit LogbookEntry constructor for the given activity metric
        e.g. 'steps' => FitStepsEntry
    '''
    constructor = None
    if activity_metric == 'calories':
        constructor = FitCaloriesEntry
    elif activity_metric == 'steps':
        constructor = FitStepsEntry
    elif activity_metric == 'distance':
        constructor = FitDistanceEntry
    return constructor
