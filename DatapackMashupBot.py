mc_ver = 51    # PMC uses this to select minecraft version
pack_count = 5

from urllib.request import Request, urlopen
import random
import os, ssl
from html.parser import HTMLParser
import webbrowser
import time

# fix SSL errors
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

# without these, PMC rejects with 403
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def webget(url):
    req = Request(url)
    req.headers = headers
    return urlopen(req).read()

# grabs datapack URLs off random parts of PMC's trending section
def get_packs(packs_to_use):
    class BrowsePageParser(HTMLParser):
        all_datapacks = None    # must set this before calling parse

        def handle_starttag(self, tag, attrs):
            # only care about anchor tags
            if tag == "a":
                for attr in attrs:
                    if attr[0] == "href":
                        # is this link a datapack?
                        if attr[1].startswith('/data-pack/'):
                            self.all_datapacks.append(attr[1])

    # grab the datapacks to use
    for i in range(0,pack_count):
        page_num = random.randrange(0,10)
        url = f'https://www.planetminecraft.com/data-packs/?order=order_hot&op1=51&p={page_num}'
        pmcdata = webget(url).decode('utf-8')

        all_datapacks = []
        parser = BrowsePageParser()
        parser.all_datapacks = all_datapacks
        parser.feed(pmcdata)

        # select a random datapack
        packs_to_use.append(random.choice(all_datapacks))

# download each pack
def download_packs(packs_to_use):
    class FindDownloadParser(HTMLParser):
        url = None
        def handle_starttag(self, tag, attrs):
            if self.url is None:
                # only care about anchor tags
                if tag == "a":
                    for attr in attrs:
                        if attr[0] == "href":
                            if "/download/file/" in attr[1]:
                                self.url = attr[1]

    full_urls = []
    for pack in packs_to_use:
        url = f'https://www.planetminecraft.com{pack}'
        pmcdata = webget(url).decode('utf-8')
        parser = FindDownloadParser()
        parser.feed(pmcdata)
        if parser.url is None:
            print("ERROR: Failed to find download URL. This can happen because Planet Minecraft has detected this script. Wait a few minutes, and try again.")
            exit(1)
        url = f'https://www.planetminecraft.com{parser.url}'
        full_urls.append(url)

    for url in full_urls:
        webbrowser.open_new(url)
        time.sleep(1)   # web browser often don't like it if we spam this, so throttle

def main():
    packs_to_use = []
    get_packs(packs_to_use)
    download_packs(packs_to_use)
   

if __name__ == "__main__":
    main()