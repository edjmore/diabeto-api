import logbookentry

class DiabetesProfile(object):
    def __init__(self, diabetes_type, bg_tgt_range, bg_severe_range):
        self.diabetes_type = diabetes_type
        self.bg_tgt_range = bg_tgt_range
        self.bg_severe_range = bg_severe_range

class OtrDiabetesProfile(DiabetesProfile):
    def __init__(self, diabetes_type, bg_tgt_range, bg_severe_range, bg_before_meal_range, bg_after_meal_range, otr_timeslots_sched):
        super(OtrDiabetesProfile, self).__init__(diabetes_type, bg_tgt_range, bg_severe_range)
        self.bg_before_meal_range = bg_before_meal_range
        self.bg_after_meal_range = bg_after_meal_range
        self.otr_timeslots_sched = otr_timeslots_sched

class OtrTimeslotsSched(object):
    def __init__(self, raw_sched):
        ''' initializes an OtrTimeslotsSched
        @raw_sched: a list of tuples of the form (name, time range)
        '''
        self.__sorted_sched = sorted(raw_sched, key=lambda tup: tup[1].start)

    def get_otr_timeslot(self, otr_logbook_entry):
        return __get_otr_timeslot(otr_logbook_entry.entry_time, 0, len(self.__sorted_sched)-1)

    def __get_otr_timeslot(self, entry_time, lo_idx, hi_idx):
        # finds timeslot name via binary search on sorted sched
        if lo_idx > hi_idx:
            return None
        mid_idx = (lo_idx+hi_idx)/2
        name,time_range = self.__sorted_sched[mid_idx]
        if time_range.contains(entry_time):
            return name
        if entry_time < time_range.lo:
            return self.__get_otr_timeslot(entry_time, lo_idx, mid_idx-1)
        else:
            return self.__get_otr_timeslot(entry_time, mid_idx+1, hi_idx)
