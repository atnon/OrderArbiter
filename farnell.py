
import urllib2
import json

class Farnell(object):
    def __init__(self, config, log=None):
        
        self.APIKey = config.get("farnell", "APIKey")
        self.APIStoreUrl = config.get("farnell", "APIStoreUrl")
        self.APIUrl =   "https://api.element14.com/catalog/products?" \
                        "callInfo.responseDataFormat=JSON" \
                        "&storeInfo.id=%(APIStoreUrl)s" \
                        "&callInfo.apiKey=%(APIKey)s" \
                        "&resultsSettings.responseGroup=Prices" % \
                        {"APIStoreUrl" : self.APIStoreUrl, "APIKey" : self.APIKey }
        self.APIRateLimit = config.get("farnell", "APIRateLimit")
        
        self.__JobList = set()
    
    def QueueSku(self, sku):
        self.__JobList.add(str(sku))
        
    def FetchSkus(self):
        Results = {}
        for Sku in self.__JobList:
            # Fetch json data from Farnell.
            SkuUrl = "".join([self.APIUrl, "&term=id:", Sku])
            RequestHandler = urllib2.urlopen(SkuUrl)
            ReturnedJson = json.load(RequestHandler)
            # Extract the prices from the json data.
            Prices = ReturnedJson["premierFarnellPartNumberReturn"]["products"][0]["prices"]
            Results[Sku] = Prices
        
        return Results
        

if __name__ == "__main__":
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read("config.conf")
    
    FarnellHandler = Farnell(config)
    FarnellHandler.QueueSku(9779272)
    FarnellHandler.QueueSku(1379812)
    FarnellHandler.QueueSku("1652316RL")
    print repr(FarnellHandler.FetchSkus())