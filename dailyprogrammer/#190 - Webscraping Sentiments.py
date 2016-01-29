from urllib import request

from bs4 import BeautifulSoup

positive_words = open("../Words/positive_words.txt", encoding="ISO-8859-1").read()
negative_words = open("../Words/negative_words.txt", encoding="ISO-8859-1").read()


def scan_video(url, count):
    lst = [x for y in [['p' if w in positive_words else 'n' for w in c.get_text().split()] for c in BeautifulSoup(request.urlopen("https://plus.googleapis.com/u/0/_/widget/render/comments?first_party_property=YOUTUBE&href=" + url).read(), 'html.parser').find_all('div', class_='Ct', limit=count)] for x in y]
    return "From a sample size of " + str(count) + " persons. It contained " + str(lst.count('p')) + " amount of happy keywords and " + str(lst.count('n')) + " amount of sad keywords. The general feelings towards this video were " + ("Happy" if lst.count('p') >= lst.count('n') else "Sad") + "."

print(scan_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ", 10))
