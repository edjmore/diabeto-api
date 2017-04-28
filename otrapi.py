import otrparser
import json,time
import requests

class OtrApi(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers = OtrApi.__raw_headers_to_dict('headers.txt')
        self.session.cookies = requests.cookies.cookiejar_from_dict(OtrApi.__raw_cookies_to_dict('cookies.txt'))

    @staticmethod
    def __raw_headers_to_dict(filename):
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
        ajax_request = format(
            '[{"moduleName":"Account","methodCall":"login","params":[{"username":"%s","password":"%s","clientTime":"%s"}]}]'
                % (self.username,self.password,time.strftime('%Y-%m-%d %H:%M', time.localtime()))
            )
        data = {'ajaxRequest': ajax_request}
        response = self.session.post(OtrApi.__url(), data=data)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

    def logout(self):
        data = {'ajaxRequest': '[{"moduleName":"Account","methodCall":"logout"}]'}
        response = self.session.post(OtrApi.__url(), data=data)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

    def get_data_list_report(self, start_date, end_date):
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
        response = self.session.get(OtrApi.__url('settings/profile/'))
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        return response.text

    @staticmethod
    def __url(dest='a/'):
        return format('https://onetouchreveal.com/%s' % dest)

if __name__ == '__main__':
    with OtrApi('ejmoore2', 'onetouch2013') as otr:
        raw_html = otr.get_data_list_report('20170129', '20170428')
        parse = otrparser.OtrParser(raw_html)
        logbook_entries = parse.get_logbook_entries()
        print('\n'.join(map(str, logbook_entries)))
        #raw_html = otr.get_profile()
        #print raw_html
