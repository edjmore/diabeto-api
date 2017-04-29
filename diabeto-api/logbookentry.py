import datetime as dt

class LogbookEntry(object):
    def __init__(self, entry_date, entry_time):
        self.entry_date = entry_date
        self.entry_time = entry_time

class OtrLogbookEntry(LogbookEntry):
    def __init__(self, entry_date, entry_time, otr_comments):
        super(OtrLogbookEntry, self).__init__(entry_date, entry_time)
        self.otr_comments = otr_comments

class OtrGlucoseEntry(OtrLogbookEntry):
    def __init__(self, entry_date, entry_time, otr_comments, bg_value):
        super(OtrGlucoseEntry, self).__init__(entry_date, entry_time, otr_comments)
        self.bg_value = bg_value

    def __str__(self):
        return format('%s, %s, %d mg/dL, %s' % (
            self.entry_date.strftime('%m/%d/%Y'),
            self.entry_time.strftime('%I:%M %p'),
            self.bg_value,
            self.otr_comments if self.otr_comments else '<none>'
            ))

class OtrPatternEntry(OtrLogbookEntry):
    def __init__(self, entry_date, entry_time, otr_comments):
        super(OtrPatternEntry, self).__init__(entry_date, entry_time, otr_comments)
        self.pattern = otr_comments

    def __str__(self):
        return format('%s, %s' % (
            self.entry_date.strftime('%m/%d/%Y'),
            self.otr_comments if self.otr_comments else '<none>'
            ))
