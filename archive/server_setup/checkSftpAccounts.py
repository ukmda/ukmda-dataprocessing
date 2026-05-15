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
			livenames.append(loc.strip())
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

with open('inactive.txt','w') as outf:
	for cam in not_live:
		outf.write(','.join(cam) + '\n')

donelist = open('moved.txt', 'r').readlines()
donelist = [x.strip() for x in donelist]
with open('todo.txt', 'w') as outf:
	for nam in livenames:
		if nam.strip() not in donelist:
			print('done list is missing', nam)
			outf.write(f'{nam}\n')


moved = open('moved.txt').readlines()
pending = open('pending.txt').readlines()
switched = open('switched.txt').readlines()

# accounts in the 'pending' list that are not in the moved list 
# are ones that i need to migrate urgently! 
pendingnotmoved = [x for x in pending if x not in moved]
if len(pendingnotmoved) > 0:
	print('stations marked pending but not moved - check if need done')
	print(pendingnotmoved)

# accounts i have moved that are neither in the switched nor pending lists
# these are probably accounts i know need to move but are currently offline
movednotpending = [x for x in moved if x not in pending and x not in switched]
if len(movednotpending) > 0:
	print('stations moved but not connecting - check on these too')
	print(movednotpending)
with open('notpending.txt', 'w') as outf:
	for nam in movednotpending:
		outf.write(f'{nam}\n')
print("")