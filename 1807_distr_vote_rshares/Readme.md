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
# query the blockchain for all accounts
python get_all_accounts.py
# analyze the account data. This writes out graphs as png files
python analyze_accounts.py
# query SteemSQL for all posts
python get_all_votes.py
# process votes
python analyze_votes.py
# plot results
python plot_votes.py
```
