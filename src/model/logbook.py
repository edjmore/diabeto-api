import datetime as dt

class LogbookEntry(object):
    def __init__(self, entry_date, entry_time):
        self.entry_date = entry_date
        self.entry_time = entry_time

    def __str__(self):
        return format('%s,%s' % (
            self.entry_date.strftime('%m/%d/%Y'),
            self.entry_time.strftime('%I:%M %p'),
            ))

# OTR specific logbook entries

class OtrLogbookEntry(LogbookEntry):
    def __init__(self, entry_date, entry_time, otr_comments):
        super(OtrLogbookEntry, self).__init__(entry_date, entry_time)
        self.otr_comments = otr_comments

class OtrGlucoseEntry(OtrLogbookEntry):
    def __init__(self, entry_date, entry_time, otr_comments, bg_value):
        super(OtrGlucoseEntry, self).__init__(entry_date, entry_time, otr_comments)
        self.bg_value = bg_value

class OtrPatternEntry(OtrLogbookEntry):
    def __init__(self, entry_date, entry_time, otr_comments):
        super(OtrPatternEntry, self).__init__(entry_date, entry_time, otr_comments)
        self.pattern = otr_comments

# Fitbit logbook entries

class FitCaloriesEntry(LogbookEntry):
    def __init__(self, entry_date, entry_time, calories):
        super(FitCaloriesEntry, self).__init__(entry_date, entry_time)
        self.calories = calories

class FitStepsEntry(LogbookEntry):
    def __init__(self, entry_date, entry_time, steps):
        super(FitStepsEntry, self).__init__(entry_date, entry_time)
        self.steps = steps

class FitDistanceEntry(LogbookEntry):
    def __init__(self, entry_date, entry_time, distance):
        super(FitDistanceEntry, self).__init__(entry_date, entry_time)
        self.distance = distance

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
