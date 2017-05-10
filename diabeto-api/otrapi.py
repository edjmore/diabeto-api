import json,time
import requests

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
