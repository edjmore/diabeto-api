import otrparser
import json,time
import requests

# fix raw_input in python 3.x
try:
    temp = raw_input
except NameError:
    global raw_input
    raw_input = input

class OtrApi(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers = OtrApi.__raw_headers_to_dict('headers.txt')
        self.session.cookies = requests.cookies.cookiejar_from_dict(OtrApi.__raw_cookies_to_dict('cookies.txt'))

    @staticmethod
    def __raw_headers_to_dict(filename):
        # read in session headers from file
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
        # read in initial session cookies from file
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
        return self

    def login(self):
        '''logs in to the otr site, raises error on failure
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
        '''logs out of the otr site, raises error on failure
        '''
        print('logout POST')
        data = {'ajaxRequest': '[{"moduleName":"Account","methodCall":"logout"}]'}
        response = self.session.post(OtrApi.__url(), data=data)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

    def get_data_list_report(self, start_date, end_date):
        '''returns a raw html report of logbook entries for the given period
        @start_date: start of period, date string formatted as "%Y%m%d"
        @end_date:   end of period, ^same format as @start_date
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
        '''returns the raw html from user's profile page
        '''
        print('get_profile GET')
        response = self.session.get(OtrApi.__url('settings/profile/'))
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        return response.text

    @staticmethod
    def __url(dest='a/'):
        return format('https://onetouchreveal.com/%s' % dest)

if __name__ == '__main__':
    raw_html = None
    #with OtrApi(raw_input('username:\t').strip(), raw_input('password:\t').strip()) as otr:
        #raw_html = otr.get_data_list_report('20170129', '20170428')
        #parse = otrparser.OtrParser(raw_html)
        #logbook_entries = parse.get_logbook_entries()
        #raw_html = otr.get_profile()
    with open('get_profile.html', 'r') as f:
        raw_html = ''.join(f.readlines())
    parse = otrparser.OtrParser(raw_html)
    parse.get_diabetes_profile()
