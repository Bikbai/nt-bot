import datetime

s = "12.11.22"

d = datetime.datetime.strptime(s, "%d.%m.%y")
print(d)