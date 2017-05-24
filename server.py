from src.api import *
from src.model import *
import multiprocessing,os
import flask

app = flask.Flask(__name__)
app.secret_key = os.environ['DIABETO_SECRET_KEY']

fit_api = fitapi.FitApi(
    os.environ['FITBIT_CLIENT_ID'],
    os.environ['FITBIT_CLIENT_SECRET'],
    'http://localhost:5000/fitbit-redirect'
    )

@app.route('/fitbit-login', methods=['GET', 'POST'])
def fitbit_login():
    """ Begin Fitbit login process. Browsers get redirected to auth page,
    other clients get the URL of the auth page.
    """
    url =  fit_api.get_auth_page_url()
    if flask.request.method == 'GET':
        return flask.redirect(url)
    else:
        return url

@app.route('/fitbit-redirect', methods=['GET', 'POST'])
def flask_redirect():
    """ Redirect page to which the Fitbit auth code is returned; returns JSON
    representation of user credentials on success.
    """
    auth_code = flask.request.args['code']
    fit_user = fit_api.login(auth_code)
    return fit_user.to_json()

@app.route('/fitbit-activity/<activity_metric>/<start_date>', methods=['POST'])
@app.route('/fitbit-activity/<activity_metric>/<start_date>/<end_date>/<start_time>/<end_time>/<high_detail>', methods=['POST'])
def fitbit_activity(activity_metric, start_date, end_date=None, start_time=None, end_time=None, high_detail=None):
    """ Returns the intraday activity time series for the given metric. See
    FitApi.get_activity_time_series() for more information. If no valid user
    credentials are provided redirects to the login page.
    """
    fit_user = __get_fit_user(flask.request.form)
    if fit_user is None:
        return flask.redirect(flask.url_for('fitbit_login'))
    raw_json = None
    if end_date is None:
        raw_json = fit_api.get_activity_time_series(fit_user, activity_metric, start_date)
    else:
        raw_json = fit_api.get_activity_time_series(
            fit_user,
            activity_metric,
            start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            high_detail=high_detail
            )
    parser = fitapi.FitParser(raw_json)
    logbook_entries = parser.get_logbook_entries()
    fname = format('fitbit-%s_%s.csv' % (activity_metric,start_date))
    csv = ''
    if len(logbook_entries) > 0:
        csv += logbook_entries[0].__class__.get_csv_headers() + '\n'
        csv += '\n'.join(map(lambda e: e.to_csv(), logbook_entries))
    return __csv_download(csv, fname)

def __get_fit_user(request_form):
    # Attempts to create an authorized FitUser object; refreshing access token if necessary.
    chk = lambda k: k in request_form
    if chk('user_id') and chk('access_token') and chk('auth_exp_time') and chk('refresh_token') and chk('scope'):
        fit_user = fitapi.FitUser(
            request_form['user_id'],
            request_form['access_token'],
            request_form['auth_exp_time'],
            request_form['refresh_token'],
            request_form['scope'],
            )
        if fit_user.is_auth_expired():
            fit_api.refresh_token(fit_user)
        return fit_user
    return None

@app.route('/otr-logbook/<start_date>/<end_date>', methods=['POST'])
def otr_logbook(start_date, end_date):
    """ Returns OneTouchReveal logbook entries for the given period. """
    otr_user = __do_otr_login(flask.request.form)
    raw_html = otr_user.get_data_list_report(start_date, end_date)
    fname = format('%s_otr-logbook_%s-%s.csv' % (
        otr_user.username,start_date,end_date
        ))
    otr_user.logout()
    parser = otrapi.OtrParser(raw_html)
    csv = logbook.OtrGlucoseEntry.get_csv_headers() + '\n' \
        + '\n'.join(map(lambda e: e.to_csv(), parser.get_logbook_entries()))
    return __csv_download(csv, fname)

@app.route('/otr-profile', methods=['POST'])
def otr_profile():
    """ Returns the user's OneTouchReveal diabetes profile. """
    otr_user = __do_otr_login(flask.request.form)
    raw_html = otr_user.get_profile()
    fname = format('%s_otr-profile.csv' % otr_user.username)
    otr_user.logout()
    parser = otrapi.OtrParser(raw_html)
    csv = parser.get_diabetes_profile().to_csv()
    return __csv_download(csv, fname)

def __do_otr_login(request_form):
    if 'username' in request_form and 'password' in request_form:
        username = request_form['username']
        password = request_form['password']
        otr_user = otrapi.OtrApi(username, password)
        try:
            otr_user.login()
        except:
            flask.abort(401) # todo: OTR login failed page
        return otr_user
    flask.abort(401) # todo: invalid request error page

def __csv_download(csv, fname):
    return flask.Response(
        csv,
        mimetype='text/csv',
        headers={
            'Content-disposition': format('attachment; filename=%s' % fname)
        })

if __name__ == '__main__':
    app.run()
