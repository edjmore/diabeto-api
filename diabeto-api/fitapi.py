import base64,json,time,urllib
import requests

class FitApi(object):
    def __init__(self, client_id, client_secret, redirect_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url

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
