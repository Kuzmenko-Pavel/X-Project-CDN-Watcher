#!./../env/bin/python
import sys
import requests
import magic

if __name__ == '__main__':
    arg = sys.argv[1:]
    print(arg)
    mime = magic.Magic(mime=True)
    content_type = mime.from_file(arg[1])
    url = 'http://0.0.0.0:8080/' + arg[0]
    r = requests.get(url)
    print(r.text, r.headers)
    r = requests.head(url)
    print(r.text, r.headers)
    files = {'file': (arg[1], open(arg[1], 'rb'), content_type)}
    values = {'async': False}
    r = requests.post(url, files=files, data=values)
    print(r.text, r.headers)
    files = {'file': (arg[1], open(arg[1], 'rb'), content_type)}
    values = {'async': False}
    r = requests.put(url, files=files, data=values)
    print(r.text, r.headers)
    values = {'async': False}
    r = requests.delete(url, data=values)
    print(r.text, r.headers)
