from bs4 import BeautifulSoup
import urllib.request

def strip_tags(text):
    text = str(text)
    while '<' in text:
        text = strip_first_tag(text)
    return text


def strip_first_tag(string):
    string = str(string)
    if '<' in string:
        return string[0:string.index('<')]+string[string.index('>')+1:]
    else:
        return string


def get_etymology(word):
    word = word.strip().lower().replace(' ','%20')
    # Scrapes Wordnik to get the etymology of a word.
    page_url = 'http://www.wordnik.com/words/' + str(word)

    with urllib.request.urlopen(page_url) as url:
        r = url.read()

    soup = BeautifulSoup(r, "html.parser")
    etys = soup.find_all("div", class_="sub-module")
    et = strip_tags(etys)

    if et[0] == '[':
        et = et[1:]

    if et[-1] == ']':
        et = et[:-1]

    return et
