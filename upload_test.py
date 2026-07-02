import requests

url = 'http://127.0.0.1:8000/api/v1/enrich'
files = {'file': ('test.csv', 'Company Name\nTestCo\n', 'text/csv')}
data = {'region': 'Pan-India'}

try:
    r = requests.post(url, files=files, data=data, timeout=20)
    print(r.status_code)
    print(r.headers.get('content-type'))
    print(r.text)
except Exception as exc:
    print('ERROR', repr(exc))
