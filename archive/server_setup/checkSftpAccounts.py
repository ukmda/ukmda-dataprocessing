import pandas as pd
import datetime


data=open('/home/ubuntu/prod/data/reports/stationlogins.txt').readlines()
camlist = []
not_live = []
still_upl = []
not_upl = []
livenames = []

livedate = datetime.datetime.now() - datetime.timedelta(days=10)
for li in data:
	if 'Last Upload' in li:
		continue
	lastup = li[:19]
	lastlo = li[21:40]
	loc = li[42:61]
	gmnid = li[64:73]
	via = li[76:].strip()
	camlist.append([lastup, lastlo, loc, gmnid, via])

	if ">" in lastup and ">" in lastlo:
		not_live.append([loc, gmnid, lastup, lastlo, via])

	elif ">" not in lastup:
		lastupdt = datetime.datetime.strptime(lastup, '%Y-%m-%dT%H:%M:%S')
		if lastupdt >= livedate:
			still_upl.append([loc, gmnid, lastup, lastlo, via])
			livenames.append(loc)
		else:
			if '>' in lastlo:
				not_live.append([loc, gmnid, lastup, lastlo, via])
			else:
				lastlodt = datetime.datetime.strptime(lastlo, '%Y-%m-%dT%H:%M:%S')
				if lastlodt >= livedate:
					not_upl.append([loc, gmnid, lastup, lastlo, via])
				else:
					not_live.append([loc, gmnid, lastup, lastlo, via])
	else: # '>' not in lastlo
		lastlodt = datetime.datetime.strptime(lastlo, '%Y-%m-%dT%H:%M:%S')
		if lastlodt >= livedate:
			not_upl.append([loc, gmnid, lastup, lastlo, via])
		else:
			not_live.append([loc, gmnid, lastup, lastlo, via])

with open('still-live.txt','w') as outf:
	for cam in still_upl:
		outf.write(','.join(cam) + '\n')

with open('not_uploading.txt','w') as outf:
	for cam in not_upl:
		outf.write(','.join(cam) + '\n')

with open('not_live.txt','w') as outf:
	for cam in not_live:
		outf.write(','.join(cam) + '\n')

donelist = open('done.txt', 'r').readlines()
with open('todo.txt', 'w') as outf:
	for nam in livenames:
		if nam not in donelist:
			print('done list is missing', nam)
			outf.write(f'{nam}\n')