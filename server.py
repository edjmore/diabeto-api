from src.api import *
from src.model import *
import multiprocessing
import flask

app = flask.Flask(__name__)

@app.route('/otr-logbook/<start_date>/<end_date>')
def otr_logbook(start_date, end_date):
    raw_html = otr.get_data_list_report(start_date, end_date)
    parse = otrapi.OtrParser(raw_html)
    return logbook.OtrGlucoseEntry.get_csv_headers() + '<br>' + '<br>'.join(map(lambda e: e.to_csv(), parse.get_logbook_entries()))

@app.route('/profile')
def profile():
    raw_html = otr.get_profile()
    parse = otrapi.OtrParser(raw_html)
    return '<pre>' + parse.get_diabetes_profile().to_csv() + '</pre>'

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
