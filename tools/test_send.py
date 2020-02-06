#!./../env/bin/python
import sys
import requests
import magic

if __name__ == '__main__':
    headers = {
        'X-Authentication': 'f9bf78b9a18ce6d46a0cd2b0b86df9da',
        'User-agent': 'Mozilla/5.0'
    }
    arg = sys.argv[1:]
    mime = magic.Magic(mime=True)
    content_type = mime.from_file(arg[1])
    url = 'http://0.0.0.0:8080/' + arg[0]

    r = requests.get(url, headers=headers)
    print(r.text, r.status_code)

    r = requests.head(url, headers=headers)
    print(r.text, r.status_code)

    files = {'file': (arg[1], open(arg[1], 'rb'), content_type)}
    r = requests.post(url, headers=headers, files=files)
    print(r.text, r.status_code)

    files = {'file': (arg[1], open(arg[1], 'rb'), content_type)}
    r = requests.put(url, headers=headers, files=files)
    print(r.text, r.status_code)

    r = requests.delete(url, headers=headers)
    print(r.text, r.status_code)

    r = requests.delete(url, headers=headers)
    print(r.text, r.status_code)
