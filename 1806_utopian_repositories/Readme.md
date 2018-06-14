* create a file named config.py with your SteemSQL credentials:
```python
#!/usr/bin/python
driver = '{ODBC Driver 17 for SQL Server}'
server = 'vip.steemsql.com,1433'
database = 'DBSteem'
uid = 'your-steemsql-username
pwd = 'your-steemsql-password'
```
* Sequence
```bash
# query SteemSQL for all posts
python query.py

# analyze the post data. This writes out graphs as png files
python analyze.py
```
