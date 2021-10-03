import requests
baseurl = "https://cloud.iexapis.com/stable/stock/"

#https://cloud.iexapis.com/stable/stock/BAC/intraday-prices?token=pk_ad177e18d7ed43ec8876c733d83a9510&chartLast=1

token= "pk_ad177e18d7ed43ec8876c733d83a9510"

def realvalue(stock):
    url= baseurl + stock + "/lastprice?token=" + token
    data= requests.get(url).content
    if(data=="Unknown symbol"):
        return "Error Unknown Symbol"
    else:
        print(data)
    return data[0]


def intraday(stock):
    url= baseurl + stock + "/intraday-prices?token=" + token +"&chartLast=1"
    data= requests.get(url)
    data1= data.content
    #print(str(data1))
    if(str(data1)=="b'Unknown symbol'"):
        return -1
    else:
        data = data.json()[0]
        #print(type(data)) # by hit and try i was able to find that it works

        #data= data[0] #converting list to dictionary now we have dictionary so we have these many thing
        #print(data)

        '''
        {'date': '2021-10-01', 'minute': '15:59', 'label': '3:59 PM', 'high': 60.95, 'low': 60.87, 'open': 60.925, 'close': 60.95, 'average': 60.915, 'volume': 11673, 'notional': 711057.145, 'numberOfTrades': 81}

        '''
        #print(data[0]["date"])
    return float(data["average"]) # returns the averag price of the stockkkkkkkk yay


def prevday(stock):
    pass


def symbols():
   url = "https://cloud.iexapis.com/beta/ref-data/symbols?token="+ token
   data = requests.get(url)
   try:
       data = data.json()
   except:
       return -1
   return data
