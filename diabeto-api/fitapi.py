import base64,time,urllib
import requests

class FitApi(object):
    def __init__(self, client_id, client_secret, redirect_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_url

    def get_auth_page_url(self):
        data = {
			'response_type': 'code',
			'client_id'    : self.client_id,
			'redirect_uri' : self.redirect_uri,
			'scope'        : ' '.join([
				'activity', 'heartrate', 'location',
				'nutrition', 'profile', 'settings',
				'sleep', 'social', 'weight'
				])
			}
        data = urllib.urlencode(data).replace('+', '%20')
        return format('%s?%s' % (FitApi.__auth_url(dest='authorize'),data))

    def login(self, auth_code):
        headers = self.__basic_headers()
        data = {
			'client_id'   : self.client_id,
			'grant_type'  : 'authorization_code',
			'redirect_uri': self.redirect_uri,
			'code'        : auth_code
			}
        response = requests.get(FitApi.__url(dest='token'), headers=headers, data=data)
        response = json.loads(response.text)
        return fit_user(
            response['user_id'],
            response['access_token'],
            time() + int(response['expires_in']),
            response['refresh_token'],
            response['scope']
            )

    def refresh_login(self, fit_user):
        headers = self.__bearer_headers(fit_user)
        data = {
            'grant_type'   : 'refresh_token',
			'refresh_token': fit_user.refresh_token
            }
        response = requests.get(FitApi.__url(dest='token'), headers=headers, data=data)
        fit_user.access_token = response['access_token']
        fit_user.auth_exp_time = time() + int(response['expires_in'])
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
    def __auth_url(dest=''):
        return format('https://www.fitbit.com/oauth2/%s' % dest)

class FitUser(object):
    def __init__(self, user_id, access_token, auth_exp_time, refresh_token, scope):
        self.user_id = user_id
        self.access_token = access_token
        self.auth_exp_time = auth_exp_time
        self.refresh_token = refresh_token
        self.scope = scope

    def is_auth_expired(self):
        return self.auth_exp_time <= time()
