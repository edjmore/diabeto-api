import otrapi,otrparser
import multiprocessing
import Flask

app = flask.Flask(__name__)

@app.route('/logbook/<start_date>/<end_date>')
def logbook(start_date, end_date):
    raw_html = otr.get_data_list_report(start_date, end_date)
    parse = otrparser.OtrParser(raw_html)
    return '<pre>' + '\n'.join(map(str, parse.get_logbook_entries())) + '</pre>'

@app.route('/profile')
def profile():
    raw_html = otr.get_profile()
    parse = otrparser.OtrParser(raw_html)
    return '<pre>' + str(parse.get_diabetes_profile()) + '</pre>'

if __name__ == '__main__':
    with otrapi.OtrApi(raw_input('username:\t').strip(), raw_input('password:\t').strip()) as otr_inst:
        global otr
        otr = otr_inst
        global flask_proc
        flask_proc = multiprocessing.Process(target=app.run)
        flask_proc.start()
        _ = raw_input()
        flask_proc.terminate()
        flask_proc.join()
