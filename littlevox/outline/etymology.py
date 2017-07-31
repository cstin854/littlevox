from bs4 import BeautifulSoup
import urllib.request
from html.parser import HTMLParser

def strip_tags(text):
    text = str(text)
    while '<' in text:
        text = strip_first_tag(text)
    return text

def strip_first_tag(string):
    string = str(string)
    temp = ''
    if '<' in string:
        return string[0:string.index('<')]+string[string.index('>')+1:]
    else:
        return string

def get_etymology(word):
    #Scrapes Wordnik to get the etymology of a word.
    page_url = 'http://www.wordnik.com/words/' + str(word)

    with urllib.request.urlopen(page_url) as url:
        r = url.read()

    soup = BeautifulSoup(r, "html.parser")

    etys = soup.find_all("div", class_="sub-module")

    index = 0

    if len(etys)>1:
        index = 1

    et = strip_tags(etys)

    if et[0] == '[':
        et = et[1:]

    if et[-1] == ']':
        et = et[:-1]

    return et
