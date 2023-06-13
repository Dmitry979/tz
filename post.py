import requests

url = "http://127.0.0.1:3000/query-example/4"
my = {"questions_num": 1}
res = requests.post(url=url, json=my)

print(res)
if res.ok:
    print(res.json())
