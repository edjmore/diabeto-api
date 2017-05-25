from src.api import *
import flask

def sessionize_fit_user(fit_user, session=flask.session):
    session['user_id'] = fit_user.user_id
    session['access_token'] = fit_user.access_token
    session['auth_exp_time'] = fit_user.auth_exp_time
    session['refresh_token'] = fit_user.refresh_token
    session['scope'] = fit_user.scope

def load_fit_user(dictlike):
    # Attempts to create an authorized FitUser object
    chk = lambda k: k in dictlike
    if chk('user_id') and chk('access_token') and chk('auth_exp_time') and chk('refresh_token') and chk('scope'):
        return fitapi.FitUser(
            dictlike['user_id'],
            dictlike['access_token'],
            dictlike['auth_exp_time'],
            dictlike['refresh_token'],
            dictlike['scope'],
            )
    return None

def sessionize_otr_user(otr_user, session=flask.session):
    session['username'] = otr_user.username
    session['password'] = otr_user.password

def load_otr_user(dictlike):
    if 'username' in dictlike and 'password' in dictlike:
        username = dictlike['username']
        password = dictlike['password']
        return otrapi.OtrApi(username, password)
    return None

def csv_download(csv, fname):
    return flask.Response(
        csv,
        mimetype='text/csv',
        headers={
            'Content-disposition': format('attachment; filename=%s' % fname)
        })
