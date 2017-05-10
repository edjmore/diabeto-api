import logbookentry
import json
import datetime as dt

class FitParser(object):
    def __init__(self, raw_json):
        self.__json = json.loads(raw_json)

    def get_logbook_entries(self):
        ''' Returns a list of FitLogbookEntry objects parsed from the raw JSON
        '''
        logbook_entries = []
        activity_metric = self.__json.keys()[0].split('-')[1]
        fullday_key = format('activities-%s' % activity_metric)
        intraday_key = format('%s-intraday' % fullday_key)
        fullday_arr = self.__json[fullday_key]
        if len(fullday_arr) > 1:
            # Fitbit API returns daily summary when multiple dates are
            # requested; meaning no intraday logbook entries
            pass
        else:
            entry_date = dt.datetime.strptime(fullday_arr[0]['dateTime'], '%Y-%m-%d').date()
            for json_entry in self.__json[intraday_key]['dataset']:
                entry_time = dt.datetime.strptime(json_entry['time'], '%H:%M:%S').time()
                entry = logbookentry.FitLogbookEntry(
                    entry_date, entry_time, activity_metric, json_entry['value']
                    )
                logbook_entries.append(entry)
        return logbook_entries

if __name__ == '__main__':
    raw_json = '''{"activities-steps":[{"dateTime":"2017-05-10","value":"6141"}],"activities-steps-intraday":{"dataset":[{"time":"00:00:00","value":7},{"time":"00:15:00","value":0},{"time":"00:30:00","value":0},{"time":"00:45:00","value":133},{"time":"01:00:00","value":33},{"time":"01:15:00","value":0},{"time":"01:30:00","value":118},{"time":"01:45:00","value":40},{"time":"02:00:00","value":0},{"time":"02:15:00","value":9},{"time":"02:30:00","value":34},{"time":"02:45:00","value":105},{"time":"03:00:00","value":36},{"time":"03:15:00","value":31},{"time":"03:30:00","value":0},{"time":"03:45:00","value":0},{"time":"04:00:00","value":0},{"time":"04:15:00","value":0},{"time":"04:30:00","value":0},{"time":"04:45:00","value":0},{"time":"05:00:00","value":0},{"time":"05:15:00","value":0},{"time":"05:30:00","value":0},{"time":"05:45:00","value":0},{"time":"06:00:00","value":0},{"time":"06:15:00","value":0},{"time":"06:30:00","value":0},{"time":"06:45:00","value":0},{"time":"07:00:00","value":0},{"time":"07:15:00","value":0},{"time":"07:30:00","value":0},{"time":"07:45:00","value":0},{"time":"08:00:00","value":0},{"time":"08:15:00","value":0},{"time":"08:30:00","value":0},{"time":"08:45:00","value":0},{"time":"09:00:00","value":0},{"time":"09:15:00","value":0},{"time":"09:30:00","value":0},{"time":"09:45:00","value":0},{"time":"10:00:00","value":0},{"time":"10:15:00","value":0},{"time":"10:30:00","value":0},{"time":"10:45:00","value":19},{"time":"11:00:00","value":0},{"time":"11:15:00","value":0},{"time":"11:30:00","value":0},{"time":"11:45:00","value":0},{"time":"12:00:00","value":126},{"time":"12:15:00","value":40},{"time":"12:30:00","value":249},{"time":"12:45:00","value":31},{"time":"13:00:00","value":293},{"time":"13:15:00","value":791},{"time":"13:30:00","value":890},{"time":"13:45:00","value":967},{"time":"14:00:00","value":1066},{"time":"14:15:00","value":839},{"time":"14:30:00","value":132},{"time":"14:45:00","value":25},{"time":"15:00:00","value":12},{"time":"15:15:00","value":18},{"time":"15:30:00","value":45},{"time":"15:45:00","value":52},{"time":"16:00:00","value":0},{"time":"16:15:00","value":0}],"datasetInterval":15,"datasetType":"minute"}}'''
    parse = FitParser(raw_json)
    print('\n'.join(map(str, parse.get_logbook_entries())))
