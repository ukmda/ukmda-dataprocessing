#
# Example showing how to use the matchdata API from Python
#

import pandas as pd 


apiurl = 'https://oaa3lqdkvf.execute-api.eu-west-1.amazonaws.com/prod'

# get all matched events for a given date
reqtyp = 'matches'
reqval = '20211121'
apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
matchlist = pd.read_json(apicall, lines=True)
print(matchlist)

# get details of one event
reqtyp = 'detail'
reqval = '20211121_032219.699_UK'
apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
evtdetail = pd.read_json(apicall, typ='series')
print(evtdetail)

# get details for the first five events in the match list
# and put them in a pandas dataframe, then sort by brightest
details=[]
for id in matchlist.head(5).orbname:
    reqval = id
    apicall = '{}?reqtyp={}&reqval={}'.format(apiurl, reqtyp, reqval)
    details.append(pd.read_json(apicall, typ='series'))
df = pd.DataFrame(details)
df = df.sort_values(by=['_mag'])
print(df)
