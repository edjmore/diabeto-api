import requests

if __name__ == '__main__':
    data = {
        'username': 'ejmoore2',
        'password': 'onetouch2013'
        }
    response = requests.post('http://127.0.0.1:5000/otr-logbook/20170319/20170419', data=data)
    print(response.text)
