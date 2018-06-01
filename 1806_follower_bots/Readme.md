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
# query SteemSQL for all posts and follow-ops:
python get_all_posts.py

# analyze the post/follow data. This writes out grpahs and the follower bot list
python analyze.py

# get account information on the follower bots directly from the blockchain
python get_account_data.py

# analyze the account data and create more graphs
python analyze_accounts.py
```
