* create a file named `config.py` with your SteemSQL credentials:
```python
#!/usr/bin/python
driver = '{ODBC Driver 17 for SQL Server}'
server = 'vip.steemsql.com,1433'
database = 'DBSteem'
uid = 'your-steemsql-username
pwd = 'your-steemsql-password'
```

* get the data:
```bash
$ python query.py
```

* process the data
```bash
$ python analyze.py
```
