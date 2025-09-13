import datetime as dt

s = '2029-10-10 12:00'

date_obj = dt.datetime.strptime(s, '%Y-%m-%d %H:%M')

print(date_obj)