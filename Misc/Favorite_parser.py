from bs4 import BeautifulSoup
import os
import re
import eventlet
from eventlet.green.urllib import request

from flask import Flask
app = Flask(__name__)

image_id_pattern = re.compile("/([0-9]+)/")
image_link_pattern = re.compile("contentUrl\": \"(.+)\",")
image_type_pattern = re.compile("(\.[a-zA-Z]+)$")
image_index_pattern = re.compile("([0-9]+)\.[a-zA-Z]+$")

replace_chars = ['.', '/']
download_directory = "/Users/mac/Documents/Misc/Imagefap/"
max_threads = 50
pool = eventlet.GreenPool()


@app.route('/download/<name>/<gallery_id>')
def browser_callback(name, gallery_id):
    get_image_links(name, gallery_id)


def fetch(url):
    return BeautifulSoup(request.urlopen(url).read(), 'html.parser')


def download(url, dst):
    request.urlretrieve(url, dst)
    return re.search(image_index_pattern, dst).group(1)


def get_gallery_links():
    for file in os.listdir("/Users/mac/Downloads/Map"):
        galleries = BeautifulSoup(''.join(open("/Users/mac/Downloads/Map/{}".format(file), 'r').readlines()),
                                  'html.parser').find_all(id="lnk_")

        for gallery in galleries:
            get_image_links(str(gallery.string), "{}&view=2".format(gallery['href']))


def get_image_links(name, link):
    for char in replace_chars:
        name = name.replace(char, "")

    if os.path.isdir(download_directory + name):
        return

    if len(link) < 20:
        link = "http://www.imagefap.com/gallery.php?gid=" + link + "&view=2"

    os.mkdir(download_directory + name)

    image_links = [[]]

    images = BeautifulSoup(request.urlopen(link).read(), 'html.parser').find_all('img')
    image_count = 0

    image_index = 0
    batch_index = 0

    for image in images:
        if image.attrs.get('alt') and image.attrs.get('height'):
            if image_index >= max_threads:
                image_index = 0
                image_links.append([])
                batch_index += 1

            image_id = re.search(image_id_pattern, str(image.parent['href'])).group(1)
            image_links[batch_index].append("http://imagefap.com/photo/{}".format(image_id))

            image_index += 1
            image_count += 1

    print("\nGallery: {}. Images: {}".format(name.strip(), image_count), end="")

    for batch in range(len(image_links)):
        download_links = []
        download_locations = []

        for page in pool.imap(fetch, image_links[batch]):
            image_link = re.search(image_link_pattern, str(page)).group(1)
            file_type = re.search(image_type_pattern, image_link).group(1)
            index = str(int(page.find(id="navigation")['data-idx']) + 1)

            download_links.append(image_link)
            download_locations.append("{}{}/{}{}".format(download_directory, name, index, file_type))

        for index in pool.imap(download, download_links, download_locations):
            print("\rGallery: {}\t\tDownloaded: {} of {} images".format(name.strip(), index, image_count), end="")

    print('\n')

app.run()