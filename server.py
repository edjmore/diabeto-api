from src.api import *
import multiprocessing
import flask

app = flask.Flask(__name__)

@app.route('/logbook/<start_date>/<end_date>')
def logbook(start_date, end_date):
    raw_html = otr.get_data_list_report(start_date, end_date)
    parse = otrapi.OtrParser(raw_html)
    return '<pre>' + '\n'.join(map(str, parse.get_logbook_entries())) + '</pre>'

@app.route('/profile')
def profile():
    raw_html = otr.get_profile()
    parse = otrapi.OtrParser(raw_html)
    return '<pre>' + str(parse.get_diabetes_profile()) + '</pre>'

if __name__ == '__main__':
    with otrapi.OtrApi(input('username:\t'), input('password:\t')) as otr_inst:
        global otr
        otr = otr_inst
        global flask_proc
        flask_proc = multiprocessing.Process(target=app.run)
        flask_proc.start()
        _ = input()
        flask_proc.terminate()
        flask_proc.join()
