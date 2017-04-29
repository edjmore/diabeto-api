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
        #todo: parse bg ranges
        timeslots_sched = self.__get_timeslots_sched()
        return diabetesprofile.OtrDiabetesProfile(
            1, 2, 3, 4, timeslots_sched
            )

    def __get_timeslots_sched(self):
        '''parses an otr timeslots sched from html
        '''
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
