import logbookentry,diabetesprofile,util
import datetime as dt
import bs4

class OtrParser(object):
    def __init__(self, raw_html):
        self.soup = bs4.BeautifulSoup(raw_html, 'html.parser')

    def get_logbook_entries(self):
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
