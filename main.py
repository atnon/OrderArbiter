import csv
import ConfigParser
import farnell

def parse(FileName):
    with open(FileName, "rb") as doc:
        Reader = csv.reader(doc)
        Orders = dict()
        UniqueSku = set()
        for Row in Reader:
            if Row:
                # Remove pesky whitespace. It may not play with us.
                Row = [Item.strip() for Item in Row]
                # row[0] = sku, row[1] = amount, row[2] = OrderId
                # Abuse set properties. Sets only contain one of each val.
                UniqueSku.add(Row[0])
                if Row[2] in Orders:
                    # OrderId exists, append to list.
                    Orders[Row[2]].append({'sku' : Row[0], 'amount' : int(Row[1])})
                else:
                    # OrderId does not exist, create list.
                    Orders[Row[2]] = [{'sku': Row[0], 'amount' : int(Row[1])}]
        return (Orders, UniqueSku)
    
def printDues(OrderList):
    template = "| {sku:9} | {amount:<6} | {PriceEach:<10} | {PriceTot:<9} | {PriceCorrTot:<11} | {PriceDiff:<7} | {Comment:<35} |"
    divider = "+-----------+--------+------------+-----------+-------------+---------+-------------------------------------+"
    for OrderId in OrderList:
        print "Order ID: %s" % OrderId
        print divider
        print template.format(sku="SKU", amount="Amount", PriceEach="Price Each", PriceTot="Total", PriceCorrTot="Corr. Total", PriceDiff="Diff", Comment="Comment")
        print divider
        TotalSumDue = 0.0
        for Item in OrderList[OrderId]:
            for key in ("sku", "amount", "PriceEach", "PriceTot", "PriceCorrTot", "PriceDiff", "Comment"):
                Item.setdefault(key, "")
            TotalSumDue = TotalSumDue + Item["PriceCorrTot"]
            print template.format(**Item)
        print divider
        print "If you ordered less than the minimum amount of any item, this was adjusted the minimum amount."
        print "Amount due: %skr (%s ex. VAT)" % ((TotalSumDue * 1.25), TotalSumDue) 
        print "Payable to bg: 5930-5680, mark the payment with %s" % OrderId
        print ""

def main():
    # Read the configuration file.
    Config = ConfigParser.ConfigParser()
    Config.read("config.conf")
    
    # Init stuff.
    OrderList = dict()
    FarnellHandler = farnell.Farnell(Config)
    
    # Parse all waiting files and build lists of skus and orders.
    for FileName in ['order(1).txt']:
        (Orders, UniqueSku) = parse(FileName)
        OrderList.update(Orders)
        FarnellHandler.QueueSkuSet(UniqueSku) #Build set of SKUs to fetch.
        
    # Fetch updated prices from farnell.
    Prices = FarnellHandler.FetchSkus()
    
    for OrderId in OrderList:
        for Item in OrderList[OrderId]:
            ItemPrices = Prices[Item["sku"]]
            # Determine volume discount
            for DiscountLevel in range(0, len(ItemPrices)):
                PriceSet = ItemPrices[DiscountLevel]
                if(DiscountLevel == 0 and (PriceSet["from"] > Item["amount"])):
                    # This happens if the ordered amount is below the minimum amount.
                    # We must adjust the amount to the minimum amount.
                    CommentString = "Ordered amount %s, adjusted to %s" % (Item["amount"], PriceSet["from"] )
                    Item.update({"Comment" : CommentString})
                    Item.update({"amount" : PriceSet["from"]})
                
                if(PriceSet["from"] <= Item["amount"] <= PriceSet["to"]):
                    PriceTot = Item["amount"]*PriceSet["cost"]
                    PriceCorrTot = Item["amount"]*ItemPrices[-1]["cost"]
                    PriceDiff = PriceTot - PriceCorrTot
                    PriceEach = PriceSet["cost"]
                    Item.update({'PriceTot' : PriceTot})
                    Item.update({'PriceCorrTot' : PriceCorrTot})
                    Item.update({'PriceDiff' : PriceDiff})
                    Item.update({'PriceEach' : PriceEach})
                    break
                else:
                    pass
    
    printDues(OrderList)
    
    
if __name__ == '__main__':
    main()