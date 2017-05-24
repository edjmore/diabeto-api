import webbrowser
import requests

if __name__ == '__main__':
    url = requests.post('http://127.0.0.1:5000/fitbit-login').text
    webbrowser.open(url)
