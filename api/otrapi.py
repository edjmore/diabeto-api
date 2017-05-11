import logbook,diaprofile,util
import datetime as dtjson,time
import bs4,requests

class OtrApi(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers = OtrApi.__raw_headers_to_dict('res/headers.txt')
        self.session.cookies = requests.cookies.cookiejar_from_dict(
            OtrApi.__raw_cookies_to_dict('res/cookies.txt')
            )

    @staticmethod
    def __raw_headers_to_dict(filename):
        # Read in session headers from file
        #
        headers = {}
        with open(filename, 'r') as f:
            for l in f.readlines():
                tokens = l.strip().split(': ')
                key = tokens[0]
                val = ''.join(tokens[1:])
                headers[key] = val
        return headers

    @staticmethod
    def __raw_cookies_to_dict(filename):
        # Read in initial session cookies from file
        #
        cookies = {}
        with open(filename, 'r') as f:
            for l in f.readline().strip().split('; '):
                tokens = l.split('=')
                key = tokens[0]
                val = ''.join(tokens[1:])
                cookies[key] = val
        return cookies

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def login(self):
        ''' Logs in to the otr site, raises error on failure
        '''
        print('login POST')
        ajax_request = format(
            '[{"moduleName":"Account","methodCall":"login","params":[{"username":"%s","password":"%s","clientTime":"%s"}]}]'
                % (self.username,self.password,time.strftime('%Y-%m-%d %H:%M', time.localtime()))
            )
        data = {'ajaxRequest': ajax_request}
        response = self.session.post(OtrApi.__url(), data=data)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

    def logout(self):
        ''' Logs out of the otr site, raises error on failure
        '''
        print('logout POST')
        data = {'ajaxRequest': '[{"moduleName":"Account","methodCall":"logout"}]'}
        response = self.session.post(OtrApi.__url(), data=data)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

    def get_data_list_report(self, start_date, end_date):
        ''' Returns a raw html report of logbook entries for the given period
        @start_date     start of period, date string formatted as "%Y%m%d"
        @end_date       end of period, ^same format as @start_date
        '''
        print('get_data_list_report POST')
        ajax_request = format(
            '[{"moduleName":"Report","methodCall":"getSingleHTMLReport","params":[{"reportId":"DATA_LIST","numberDays":"0","startDt":"%s","endDt":"%s","options":{},"sortAscending":true,"patientClinicId":""}]}]'
                % (start_date,end_date)
            )
        data = {'ajaxRequest': ajax_request}
        response = self.session.post(OtrApi.__url(), data=data)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        return json.loads(response.text)['response']['report']

    def get_profile(self):
        ''' Returns the raw html from user's profile page
        '''
        print('get_profile GET')
        response = self.session.get(OtrApi.__url('settings/profile/'))
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        return response.text

    @staticmethod
    def __url(dest='a/'):
        return format('https://onetouchreveal.com/%s' % dest)

class OtrParser(object):
    def __init__(self, raw_html):
        self.__soup = bs4.BeautifulSoup(raw_html, 'html.parser')

    def get_logbook_entries(self):
        ''' Returns a list of logbook entries parsed from the html
        '''
        logbook_entries = []
        for tbl_row in self.__soup.find_all('tr')[1:]:
            cells = tbl_row.find_all('div')
            entry_date = dt.datetime.strptime(cells[0].get_text(), '%m/%d/%Y').date()
            entry_time = dt.datetime.strptime(cells[1].get_text(), '%I:%M %p').time()
            entry_type = cells[3].get_text()
            otr_comments = cells[6].get_text()
            if entry_type == 'Glucose':
                bg_value = int(cells[4].get_text().split(' ')[0])
                logbook_entries.append(logbook.OtrGlucoseEntry(entry_date, entry_time, otr_comments, bg_value))
            elif entry_type == 'BG Pattern':
                pass
                logbook_entries.append(logbook.OtrPatternEntry(entry_date, entry_time, otr_comments))
            else:
                print('*** OtrParser: unknown entry type "%s" ***' % entry_type)
        return logbook_entries

    def get_diabetes_profile(self):
        ''' Parses the user's diabetes profile
        '''
        diabetes_type = self.__get_diabetes_type()
        bg_tgt_range,bg_severe_range,bg_before_meal_range,bg_after_meal_range = \
            self.__get_bg_ranges()
        timeslots_sched = self.__get_timeslots_sched()
        return diaprofile.Otrdiaprofile(
            diabetes_type,
            bg_tgt_range, bg_severe_range,
            bg_before_meal_range, bg_after_meal_range,
            timeslots_sched
            )

    def __get_diabetes_type(self):
        # Returns text indicating the user's diabetes type; e.g. Type 1, Type 2, or Gestational
        #
        div = self.__soup.find(id='targetsDisplay')
        p = div.find('p')
        return p.find('strong').get_text().strip()

    def __get_bg_ranges(self):
        # Finds the four target bg ranges in user profile
        #
        range_tbl = self.__soup.find('table', 'targetRanges')
        tgt_rngs = lambda tr: util.Range(float(tr.find('td', 'target-range-low').get_text().strip()),float(tr.find('td', 'target-range-high').get_text().strip()))
        bg_before_meal_range,bg_after_meal_range,bg_tgt_range = \
            map(tgt_rngs, range_tbl.find_all('tr')[:3])
        sev_low = float(range_tbl.find('td', 'severe-low').get_text().strip())
        sev_high = float(range_tbl.find('td', 'severe-high').get_text().strip())
        bg_severe_range = util.Range(sev_low, sev_high)
        return bg_tgt_range,bg_severe_range,bg_before_meal_range,bg_after_meal_range

    def __get_timeslots_sched(self):
        # Parses an otr timeslots sched from html
        #
        sched_tbl = self.__soup.find(id='schedulePrefsDisplay')
        names_row,times_row = sched_tbl.find_all('tr')[:2]
        names = map(lambda td: td.get_text().strip(), names_row.find_all('td'))
        times = map(lambda td: td.get_text(), times_row.find_all('td'))
        t = lambda s: dt.datetime.strptime(s, '%I:%M %p').time()
        raw_sched = []
        for name,time in zip(names, times):
            start,end = map(lambda tok: tok.strip(), time.split('-'))
            time_range = util.Range(t(start), t(end))
            raw_sched.append((name,time_range))
        return diaprofile.OtrTimeslotsSched(raw_sched)
