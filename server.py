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

fit_user_manager = None
try:
    # todo: connect to PostgreSQL database
    db_conn = None
    fit_user_manager = fitapi.FitUserManager(db_conn)
except NotImplementedError:
    fit_user_manager = fitapi.DebugFitUserManager()

@app.route('/fitbit-login', methods=['GET', 'POST'])
def fitbit_login():
    if flask.request.method == 'POST':
        if 'user_id' in flask.request.form and 'access_token' in flask.request.form:
            fit_user = fit_user_manager.get_user(
                flask.request.form['user_id'],
                flask.request.form['access_token']
                )
            if fit_user is not None:
                __flask_session_login(fit_user)
                return flask.redirect('fitbit_login_status')
    return flask.redirect(fit_api.get_auth_page_url())

@app.route('/fitbit-redirect', methods=['GET'])
def fitbit_redirect():
    auth_code = flask.request.args['code']
    fit_user = fit_api.login(auth_code)
    fit_user_manager.store_user(fit_user)
    __flask_session_login(fit_user)
    return flask.redirect(flask.url_for('fitbit_login_status'))

@app.route('/fitbit-logout', methods=['GET', 'POST'])
def fitbit_logout():
    __flask_session_logout()
    return flask.redirect(flask.url_for('fitbit_login_status'))

@app.route('/fitbit-login-status', methods=['GET'])
def fitbit_login_status():
    fit_user = __flask_session_get_user()
    if fit_user is None:
        return '<pre>Not logged in</pre>'
    return format('<pre>Logged in as %s:\n%s</pre>' % (fit_user.user_id,str(fit_user)))

def __flask_session_login(fit_user):
    flask.session['user_id'] = fit_user.user_id
    flask.session['access_token'] = fit_user.access_token

def __flask_session_get_user():
    if 'user_id' in flask.session and 'access_token' in flask.session:
        if 'auth_exp_time' in flask.session and 'refresh_token' in flask.session and 'scope' in flask.session:
            return fitapi.FitUser(
                flask.session['user_id'],
                flask.session['access_token'],
                flask.session['auth_exp_time'],
                flask.session['refresh_token'],
                flask.session['scope']
                )
        return fit_user_manager.get_user(
            flask.session['user_id'],
            flask.session['access_token']
            )
    return None

def __flask_session_logout():
    flask.session.pop('user_id', None)
    flask.session.pop('access_token', None)

@app.route('/otr-logbook/<start_date>/<end_date>', methods=['POST'])
def otr_logbook(start_date, end_date):
    otr_user = __do_otr_login(flask.request.form)
    if not otr_user:
        flask.abort(401)
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
    otr_user = __do_otr_login(flask.request.form)
    if not otr_user:
        flask.abort(401)
    raw_html = otr_user.get_profile()
    fname = format('%s_otr-profile.csv' % otr_user.username)
    otr_user.logout()
    parser = otrapi.OtrParser(raw_html)
    csv = parser.get_diabetes_profile().to_csv()
    return __csv_download(csv, fname)

def __do_otr_login(request_form):
    username = request_form['username']
    password = request_form['password']
    otr_user = otrapi.OtrApi(username, password)
    try:
        otr_user.login()
    except:
        otr_user = None
    return otr_user

def __csv_download(csv, fname):
    return flask.Response(
        csv,
        mimetype='text/csv',
        headers={
            'Content-disposition': format('attachment; filename=%s' % fname)
        })

if __name__ == '__main__':
    global flask_proc
    flask_proc = multiprocessing.Process(target=app.run)
    flask_proc.start()
    _ = input()
    flask_proc.terminate()
    flask_proc.join()
