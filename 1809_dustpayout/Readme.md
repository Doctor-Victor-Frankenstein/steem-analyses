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
# query SteemSQL
python get_steemsql_data.py
# analyze each day of data separately and in parallel
make -j10
# plot results
python plot.py
```
