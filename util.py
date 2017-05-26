import flask


def csv_download(csv, fname):
    return flask.Response(
        csv,
        mimetype='text/csv',
        headers={
            'Content-disposition': format('attachment; filename=%s' % fname)
        })
