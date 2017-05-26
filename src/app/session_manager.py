from ..api import *
import flask

class SessionManager(object):
    def __init__(self):
        pass

    def add_fit_user(self, fit_user):
        self.__add_object(fit_user)

    def add_otr_user(self, otr_user):
        self.__add_object(otr_user)

    def get_fit_user(self):
        return __get_object(fitapi.FitUser, [
            'user_id',
            'access_token',
            'auth_exp_time',
            'refresh_token',
            'scope'
            ])

    def get_otr_user(self):
        return __get_object(otrapi.OtrApi, [
            'username',
            'password'
            ])

    def remove_fit_user(self):
        fit_user = self.get_fit_user()
        if fit_user is not None:
            self.__remove_object(fit_user)

    def remove_otr_user(self):
        otr_user = self.get_otr_user()
        if otr_user is not None:
            self.__remove_object(otr_user)

    def __add_object(self, obj):
        for attr,val in obj.__dict__.items():
            flask.session[attr] = val

    def __get_object(self, cls, attrs):
        obj = cls.__new__(cls)
        for a in attrs:
            if a not in flask.session:
                obj = None
                break
            obj.__dict__[a] = flask.session[a]
        return obj

    def __remove_object(self, obj):
        for attr in obj.__dict__.keys():
            flask.session.pop(attr, None)
