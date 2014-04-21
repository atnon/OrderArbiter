import urllib2
import json
import time

class Farnell(object):
    def __init__(self, config):
        """
        Constructor. Reads the config and sets proper values.
        See config.conf.template for an example configuration file.
        
        Args:
            config: Object containing the configuration.
        """
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
        """
        Appends an individual SKU to the joblist.
        
        Args:
            sku: A SKU Number.
        """
        self.__JobList.add(str(sku))
        
    def QueueSkuSet(self, SkuSet):
        """
        Appends a set of SKUs to the joblist.
        
        Args:
            SkuSet: A set of SKUs
        """
        self.__JobList.update(SkuSet)
        
    def FetchSkus(self):
        """
        Fetches all the queued SKUs from the given API URL.
        The function includes a rate limiting algorithm stolen from/inspired by
        http://stackoverflow.com/questions/667508/whats-a-good-rate-limiting-algorithm
        
        Returns:
            A dictionary containing the prices of all SKUs queued.
        """
        Results = {}
        LastTimeCalled = [0.0]
        MinInterval = 1.0 / float(self.APIRateLimit)
        ItemsToFetch = len(self.__JobList)
        print "Entries to fetch: %s" % ItemsToFetch
        Count = 0
        for Sku in self.__JobList:
            Elapsed = time.clock() - LastTimeCalled[0]
            LeftToWait = MinInterval - Elapsed
            if LeftToWait > 0:
                time.sleep(LeftToWait)
            Count = Count + 1
            print "Fetching sku %s, %s to go." % (Sku, (ItemsToFetch - Count))
            Results[Sku] = self.FetchSku(Sku) # Save result.
            LastTimeCalled[0] = time.clock()
            
        
        return Results
    
    def FetchSku(self, Sku):
        """
        Fetches data for a given SKU.
        
        Args:
            Sku: The article number of the item.
            
        Returns:
            A dictionary of prices for the given SKU.
        """
        # Fetch json data from Farnell.
        SkuUrl = "".join([self.APIUrl, "&term=id:", Sku])
        
        try:
            RequestHandler = urllib2.urlopen(SkuUrl)
            ReturnedJson = json.load(RequestHandler)
        except urllib2.HTTPError, e:
            # TODO : Farnell sends a 500 Internal Server Error, 
            # which trips the HTTPError exception.
            # We must bypass this somehow and still get the data.
            if e.code == 503:
                time.sleep(1.0 / float(self.APIRateLimit)) # Wait a bit and...
                return self.FetchSku(Sku) # ...try again, for great glory!
            else:
                print "HTTPError: %s, triggered on URL %s" % (e, SkuUrl)
        except urllib2.URLError, e:
            print "URLError: %s, triggered on URL %s" % (e, SkuUrl)
        
        # Extract the prices from the json data.
        try:
            Prices = ReturnedJson["premierFarnellPartNumberReturn"]["products"][0]["prices"]
        except KeyError, e:
            if ReturnedJson["Fault"]:
                print "Faulty Query to Farnell at sku %s" % Sku
            else:
                print "Exception: %s" % e
        return Prices
        

if __name__ == "__main__":
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read("config.conf")
    
    FarnellHandler = Farnell(config)
    FarnellHandler.QueueSku(9779272)
    FarnellHandler.QueueSku(1379812)
    FarnellHandler.QueueSku("1652316RL")
    print repr(FarnellHandler.FetchSkus())