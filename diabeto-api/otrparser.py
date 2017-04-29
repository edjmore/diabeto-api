import logbookentry,diabetesprofile,util
import datetime as dt
import bs4

class OtrParser(object):
    def __init__(self, raw_html):
        self.soup = bs4.BeautifulSoup(raw_html, 'html.parser')

    def get_logbook_entries(self):
        '''returns a list of logbook entries parsed from the html
        '''
        logbook_entries = []
        for tbl_row in self.soup.find_all('tr')[1:]:
            cells = tbl_row.find_all('div')
            entry_date = dt.datetime.strptime(cells[0].get_text(), '%m/%d/%Y').date()
            entry_time = dt.datetime.strptime(cells[1].get_text(), '%I:%M %p').time()
            entry_type = cells[3].get_text()
            otr_comments = cells[6].get_text()
            if entry_type == 'Glucose':
                bg_value = int(cells[4].get_text().split(' ')[0])
                logbook_entries.append(logbookentry.OtrGlucoseEntry(entry_date, entry_time, otr_comments, bg_value))
            elif entry_type == 'BG Pattern':
                pass
                logbook_entries.append(logbookentry.OtrPatternEntry(entry_date, entry_time, otr_comments))
            else:
                print('*** OtrParser: unknown entry type "%s" ***' % entry_type)
        return logbook_entries

    def get_diabetes_profile(self):
        '''parses the user\'s diabetes profile
        '''
        diabetes_type = self.__get_diabetes_type()
        bg_tgt_range,bg_severe_range,bg_before_meal_range,bg_after_meal_range = \
            self.__get_bg_ranges()
        timeslots_sched = self.__get_timeslots_sched()
        return diabetesprofile.OtrDiabetesProfile(
            diabetes_type,
            bg_tgt_range, bg_severe_range,
            bg_before_meal_range, bg_after_meal_range,
            timeslots_sched
            )

    def __get_diabetes_type(self):
        # returns text indicating the user's diabetes type; e.g. Type 1, Type 2, or Gestational
        div = self.soup.find(id='targetsDisplay')
        p = div.find('p')
        return p.find('strong').get_text().strip()

    def __get_bg_ranges(self):
        # finds the four target bg ranges in user profile
        range_tbl = self.soup.find('table', 'targetRanges')
        tgt_rngs = lambda tr: util.Range(float(tr.find('td', 'target-range-low').get_text().strip()),float(tr.find('td', 'target-range-high').get_text().strip()))
        bg_before_meal_range,bg_after_meal_range,bg_tgt_range = \
            map(tgt_rngs, range_tbl.find_all('tr')[:3])
        sev_low = float(range_tbl.find('td', 'severe-low').get_text().strip())
        sev_high = float(range_tbl.find('td', 'severe-high').get_text().strip())
        bg_severe_range = util.Range(sev_low, sev_high)
        return bg_tgt_range,bg_severe_range,bg_before_meal_range,bg_after_meal_range

    def __get_timeslots_sched(self):
        # parses an otr timeslots sched from html
        sched_tbl = self.soup.find(id='schedulePrefsDisplay')
        names_row,times_row = sched_tbl.find_all('tr')[:2]
        names = map(lambda td: td.get_text().strip(), names_row.find_all('td'))
        times = map(lambda td: td.get_text(), times_row.find_all('td'))
        t = lambda s: dt.datetime.strptime(s, '%I:%M %p').time()
        raw_sched = []
        for name,time in zip(names, times):
            start,end = map(lambda tok: tok.strip(), time.split('-'))
            time_range = util.Range(t(start), t(end))
            raw_sched.append((name,time_range))
        return diabetesprofile.OtrTimeslotsSched(raw_sched)
