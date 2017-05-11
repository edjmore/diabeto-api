import logbook
import base64,datetime as dt,json,time,urllib
import requests

class FitApi(object):
    def __init__(self, client_id, client_secret, redirect_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url

    def get_activity_time_series(self, fit_user, activity_metric, start_date, end_date='1d', start_time=None, end_time=None, high_detail=False):
        ''' Returns JSON for a series of logbook entries for activity data within the specified time range on the given date
        @fit_user           an authenticated Fitbit user
        @activity_metric    one of 'calories', 'steps', or 'distance'
        @start_date         start date in yyyy-MM-dd format (or 'today')
        @end_date           analogous to @start_date
        @start_time         start time in HH:mm format
        @end_time           analogous to @start_time
        @high_detail        if True, will get an activity entry for each minute in the time
                            range, otw every 15 minutes (defaults to False)
        '''
        detail_level = '1min' if high_detail else '15min'
        url = format('https://api.fitbit.com/1/user/-/activities/%s/date/%s/%s/%s'
            % (activity_metric,start_date,end_date,detail_level)
            )
        if start_time is not None and end_time is not None:
            url += format('/time/%s/%s' % (start_time,end_time))
        url += '.json'
        headers = self.__bearer_headers(fit_user)
        response = requests.get(url, headers=headers)
        return response.text

    def get_auth_page_url(self):
        ''' Returns the URL for the Fitbit authorization page where users can login
        '''
        data = {
			'response_type': 'code',
			'client_id'    : self.client_id,
			'redirect_uri' : self.redirect_url,
			'scope'        : ' '.join([
				'activity', 'heartrate', 'location',
				'nutrition', 'profile', 'settings',
				'sleep', 'social', 'weight'
				])
			}
        data = urllib.urlencode(data).replace('+', '%20')
        return format('%s?%s' % (FitApi.__auth_url(),data))

    def login(self, auth_code):
        ''' Logs in the user and returns a FitUser object
        @auth_code      an authorization code from Fitbit to request an access token; this will have
                        been provided to our app through a request from the Fitbit servers to our
                        redirect URL
        '''
        headers = self.__basic_headers()
        data = {
			'client_id'   : self.client_id,
			'grant_type'  : 'authorization_code',
			'redirect_uri': self.redirect_url,
			'code'        : auth_code
			}
        response = requests.post(FitApi.__token_url(), headers=headers, params=data)
        response = json.loads(response.text)
        return FitUser(
            response['user_id'],
            response['access_token'],
            time.time() + int(response['expires_in']),
            response['refresh_token'],
            response['scope']
            )

    def refresh_login(self, fit_user):
        ''' Uses the refresh_token to keep the user logged in
        @fit_user   a FitUser object with a valid refresh token
        '''
        headers = self.__bearer_headers(fit_user)
        data = {
            'grant_type'   : 'refresh_token',
			'refresh_token': fit_user.refresh_token
            }
        response = requests.post(FitApi.__token_url(), headers=headers, params=data)
        fit_user.access_token = response['access_token']
        fit_user.auth_exp_time = time.time() + int(response['expires_in'])
        fit_user.refresh_token = response['refresh_token']

    def __basic_headers(self):
		b64_id_secret = base64.b64encode(format('%s:%s' % (self.client_id,self.client_secret)))
		authorization = format('Basic %s' % b64_id_secret)
		return {
			'Authorization': authorization,
			'Content-Type' : 'application/x-www-form-urlencoded'
			}

    def __bearer_headers(self, fit_user):
		authorization = format('Bearer %s' % fit_user.access_token)
		return {
			'Authorization': authorization
			}

    @staticmethod
    def __auth_url():
        return 'https://www.fitbit.com/oauth2/authorize'

    @staticmethod
    def __token_url():
        return 'https://api.fitbit.com/oauth2/token'

class FitUser(object):
    def __init__(self, user_id, access_token, auth_exp_time, refresh_token, scope):
        self.user_id = user_id
        self.access_token = access_token
        self.auth_exp_time = auth_exp_time
        self.refresh_token = refresh_token
        self.scope = scope

    def is_auth_expired(self):
        return self.auth_exp_time <= time.time()

    def __str__(self):
        return '\n'.join(map(str, [
            self.user_id,
            self.access_token,
            self.auth_exp_time,
            self.refresh_token,
            self.scope
            ]))

class FitParser(object):
    def __init__(self, raw_json):
        self.__json = json.loads(raw_json)

    def get_logbook_entries(self):
        ''' Returns a list of Fitlogbook objects parsed from the raw JSON
        '''
        logbook_entries = []
        activity_metric = self.__json.keys()[0].split('-')[1]
        fullday_key = format('activities-%s' % activity_metric)
        intraday_key = format('%s-intraday' % fullday_key)
        fullday_arr = self.__json[fullday_key]
        if len(fullday_arr) > 1:
            # Fitbit API returns daily summary when multiple dates are
            # requested; meaning no intraday logbook entries
            pass
        else:
            constructor = logbook.get_fit_logentry_constructor(activity_metric)
            entry_date = dt.datetime.strptime(fullday_arr[0]['dateTime'], '%Y-%m-%d').date()
            for json_entry in self.__json[intraday_key]['dataset']:
                entry_time = dt.datetime.strptime(json_entry['time'], '%H:%M:%S').time()
                entry = constructor(
                    entry_date, entry_time, json_entry['value']
                    )
                logbook_entries.append(entry)
        return logbook_entries
