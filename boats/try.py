from currency_converter import CurrencyConverter, RateNotFoundError
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
from currency_converter import CurrencyConverter, RateNotFoundError


mydict = {'a': 'url1', 'b': 'url2', 'c': 'url3', 'd': 'url4', 'e': 'url5'}

mylist = [25, 76, 3, 8, 0]

result_list, result_dict = zip(*sorted(zip(mylist, mydict.items())))

#print(result_list)
#print(dict(result_dict))

print(*sorted((zip(mylist, mydict.items()))))

print(list(zip(*sorted((zip(mylist, mydict.items()))))))

