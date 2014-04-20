import csv
import ConfigParser

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
                    Orders[Row[2]].append({Row[0] : Row[1]})
                else:
                    # OrderId does not exist, create list.
                    Orders[Row[2]] = [{Row[0] : Row[1]}]
        return (Orders, UniqueSku)

def main():
    SkuSet = set()
    OrderList = dict()
    # Parse all waiting files and build lists of skus and orders.
    for FileName in ['order.txt', 'order(1).txt']:
        (Orders, UniqueSku) = parse(FileName)
        OrderList.update(Orders)
        SkuSet.union(UniqueSku)
    # TODO: Fetch updated prices from farnell.
    # TODO: Prices + Orders = Profit!
    print repr(UniqueSku)
    print repr(OrderList)
    
if __name__ == '__main__':
    main()