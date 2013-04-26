''' 
FINDING PRIVATE SELLERS WHO MAY BE ACTING AS DEALERS

This is a program to search through armslist's for sale forums and
	Find private sellers in a given location selling a given type of gun then
	Find out how many other items they have for sale.
This can then be used to go and find out more about the private sellers who are busy, and whether they're legit.
By Fergus Pitt 


'''



from urllib import urlopen
import re
import time

#Set up 
DirectoryURLsToSearch={}
upperlimitsales=4
busySellers=[]

#Produce the list of directories to examine, note: Private seller is hardcoded into the function.
def makeURLs(city,category,DirectoriesNumber):
	i=1
	DirectoryURLs={}
	while i<DirectoriesNumber+1:
		DirectoryURL='http://www.armslist.com/classifieds/search?location='+city+'&category='+category+'&sellertype=1&page='+str(i)
		DirectoryURLs[DirectoryURL]={}
		key=city+category
		DirectoryURLsToSearch[key]=DirectoryURLs
		i=i+1

#this could be automated, but I can't be bothered being lazy.
makeURLs('illinois','handguns',5)
makeURLs('illinois','shotguns',5)
makeURLs('illinois','nfa-firearms',5)
makeURLs('louisiana','handguns',5)
makeURLs('louisiana','shotguns',5)
makeURLs('louisiana','nfa-firearms',5)

'''
Get Unlicensed Dealers (network analysis)
 and have many other sales. (other sales found through scraping the URL with '?relatedto'. If the subsequent URL has many items, then possible dealer=true.)
'''

'''For each directory URL, 
	isolate the URL of each individual advertisement, 
	For each advertisement, get the URL listing the other advertistments by the seller (aka network).
	For each network, count the number of other items for sale.
	If the number is greater than the upper limit (which is set at the top of this .py file), add the networkURL to a list of "busy sellers"

'''
for DirectoryURL in DirectoryURLsToSearch.values()[0].keys():
	time.sleep(1)
	
	#print DirectoryURL
	data = urlopen(DirectoryURL).read()
	match1=re.search(r'-->\r\n+.+\r\n.+',data)
	if match1:
		#print match1.group(0)
		SoupOfItems=match1.group(0)
		itemURLs=re.findall(r'/[a-z]+/[0-9]+/[a-z0-9-]+',SoupOfItems)
		itemURLDict={}
		i=0
		for itemURL in itemURLs:
			itemURLs[i]='http://www.armslist.com'+itemURLs[i]
			itemURLDict[itemURLs[i]]='put network count here'
			networkURLSoup=urlopen(itemURLs[i]).read()
			# Got get the network
			match=re.search(r'href="/classifieds/search\?relatedto=.+">Listings by this user</a>',networkURLSoup)
			if match:
				networkURL=match.group(0)
				networkURL=networkURL.replace('">Listings by this user</a>','')
				networkURLArray=networkURL.split('"')
				networkURL=networkURLArray[0].replace('href=','http://www.armslist.com')+networkURLArray[1]
				#print 'found listings by user, at: '+networkURL
				
				#FOR EACH ADVERTISER'S NETWORK, OPEN THE URL OF OTHER LISTINGS AND COUNT THEIR OTHER ADVERTS
				networkDataSoup=urlopen(networkURL).read()
				match2=re.search(r'HACK FOR EDS -->\r\n+.+\r\n.+',networkDataSoup)
				if match2:
					#print 'loaded network URL, found some soup of other listings'
					SoupForSale=match2.group(0)
					numberofSales=SoupForSale.count('class=\'title\'')
					print numberofSales
					itemURLDict[itemURLs[i]]=str(numberofSales)
					if numberofSales>upperlimitsales:
						busySellers.append(networkURL+" has " +str(numberofSales)+" items for sale")
			i=i+1
		#SAVE THE DATA	
		DirectoryURLsToSearch.values()[0][DirectoryURL]=itemURLDict

''' 
List the busy Sellers
'''

busySellers