#!/usr/bin/env python3

from src import common
from src.api import *
from src.model import *
from util import *
import multiprocessing,os
import flask,requests

app = flask.Flask(__name__)
app.secret_key = os.environ['DIABETO_SECRET_KEY']
app.config['SERVER_NAME'] = 'localhost:5000'

fit_api = fitapi.FitApi(
    os.environ['FITBIT_CLIENT_ID'],
    os.environ['FITBIT_CLIENT_SECRET'],
    'http://%s/fitbit-redirect' % app.config['SERVER_NAME']
    )

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return flask.render_template('index.html', session_dump_str=str(flask.session))

@app.route('/fitbit-login', methods=['GET'])
def fitbit_login():
    """ Begin Fitbit login process. Browsers get redirected to auth page,
    other clients get the URL of the auth page.
    """
    url =  fit_api.get_auth_page_url()
    return flask.redirect(url)

@app.route('/fitbit-redirect', methods=['GET'])
def fitbit_redirect():
    """ Redirect page to which the Fitbit auth code is returned; returns JSON
    representation of user credentials on success.
    """
    auth_code = flask.request.args['code']
    fit_user = fit_api.login(auth_code)
    sessionize_fit_user(fit_user)
    redirect_url = flask.session.pop('redirect', None)
    if redirect_url:
        # Redirect back to original destination page
        return flask.redirect(redirect_url)
    return flask.redirect('index')

@app.route('/fitbit-activity/<activity_metric>/<start_date>', methods=['GET'])
@app.route('/fitbit-activity/<activity_metric>/<start_date>/<end_date>/<start_time>/<end_time>/<high_detail>', methods=['GET'])
def fitbit_activity(activity_metric, start_date, end_date=None, start_time=None, end_time=None, high_detail=None):
    """ Returns the intraday activity time series for the given metric. See
    FitApi.get_activity_time_series() for more information. If no valid user
    credentials are provided redirects to the login page.
    """
    fit_user = load_fit_user(flask.session)
    if fit_user is None:
        # Redirect back to this page after login
        flask.session['redirect'] = flask.request.path
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
    return csv_download(csv, fname)

@app.route('/otr-login', methods=['GET', 'POST'])
def otr_login():
    if flask.request.method == 'GET':
        return flask.render_template('otr-login.html')
    else:
        otr_user = load_otr_user(flask.request.form)
        sessionize_otr_user(otr_user)
        redirect_url = flask.session.pop('redirect', None)
        if redirect_url:
            # Redirect back to original destination page
            return flask.redirect(redirect_url)
        return flask.redirect('index')

@app.route('/otr-logbook/<start_date>/<end_date>', methods=['GET'])
def otr_logbook(start_date, end_date):
    """ Returns OneTouchReveal logbook entries for the given period. """
    otr_user = load_otr_user(flask.session)
    if otr_user is None:
        # Redirect back to this page after login
        flask.session['redirect'] = flask.request.path
        return flask.redirect(flask.url_for('otr_login'))
    otr_user.login()
    raw_html = otr_user.get_data_list_report(start_date, end_date)
    otr_user.logout()
    fname = format('%s_otr-logbook_%s-%s.csv' % (
        otr_user.username,start_date,end_date
        ))
    parser = otrapi.OtrParser(raw_html)
    csv = logbook.OtrGlucoseEntry.get_csv_headers() + '\n' \
        + '\n'.join(map(lambda e: e.to_csv(), parser.get_logbook_entries()))
    return csv_download(csv, fname)

@app.route('/otr-profile', methods=['GET'])
def otr_profile():
    """ Returns the user's OneTouchReveal diabetes profile. """
    otr_user = load_otr_user(flask.session)
    if otr_user is None:
        # Redirect back to this page after login
        flask.session['redirect'] = flask.request.path
        return flask.redirect(flask.url_for('otr_login'))
    otr_user.login()
    raw_html = otr_user.get_profile()
    otr_user.logout()
    fname = format('%s_otr-profile.csv' % otr_user.username)
    parser = otrapi.OtrParser(raw_html)
    csv = parser.get_diabetes_profile().to_csv()
    return csv_download(csv, fname)

@app.errorhandler(common.AbstractApiError)
def handle_api_error(e):
    response = flask.jsonify(e.to_dict())
    response.status_code = e.status_code
    return response

if __name__ == '__main__':
    app.run()
