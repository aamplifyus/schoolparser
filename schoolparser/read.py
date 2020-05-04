import logging
import re
from requests_html import HTMLSession
import requests
import random
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup as bs
import colorama

from schoolparser.base import SCHOOL_URLS, SCHOOL_SOCIAL_URLS, timed

from pprint import pprint

logger = logging.getLogger(__name__)
# scrapinghub crawlera
url = "http://icanhazip.com"
proxy_host = "proxy.crawlera.com"
proxy_port = "8010"
proxy_auth = "<APIKEY>:"
proxies = {
       "https": f"https://{proxy_auth}@{proxy_host}:{proxy_port}/",
       "http": f"http://{proxy_auth}@{proxy_host}:{proxy_port}/"
}
# r = requests.get(url, proxies=proxies, verify=False)

# email address links
url = "https://www.randomlists.com/email-addresses"
EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
PHONE_REGEX = r"""\(?\b[2-9][0-9]{2}\)?[-][2-9][0-9]{2}[-][0-9]{4}\b"""
PHONE_REGEX = r"""(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?"""
TWITTER_REGEX = r"""http(s)?:\/\/(.*\.)?twitter\.com\/[A-z0-9_]+\/?"""
LINKEDIN_REGEX = r"""http(s)?:\/\/([\w]+\.)?linkedin\.com\/in\/[A-z0-9_-]+\/?"""
FACEBOOK_REGEX = r"""http(s)?:\/\/(www\.)?(facebook|fb)\.com\/[A-z0-9_\-\.]+\/?"""
INSTAGRAM_REGEX = r"""https?:\/\/(www\.)?instagram\.com\/([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)"""

def _get_phone(soup, response):
    try:
        phone = soup.select("a[href*=callto]")[0].text
        return phone
    except:
        pass

    try:
        phone = re.findall(r'\(?\b[2-9][0-9]{2}\)?[-][2-9][0-9]{2}[-][0-9]{4}\b', response.text)[0]
        return phone
    except:
        pass

    try:
       phone = re.findall(r'\(?\b[2-9][0-9]{2}\)?[-. ]?[2-9][0-9]{2}[-. ]?[0-9]{4}\b', response.text)[-1]
       return phone
    except:
        phone = ''
        return phone

# init the colorama module
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET

def _is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_free_proxies():
    url = "https://free-proxy-list.net/"
    # get the HTTP response and construct soup object
    soup = bs(requests.get(url).content, "html.parser")
    proxies = []
    for row in soup.find("table", attrs={"id": "proxylisttable"}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies

def get_session(proxies):
    # construct an HTTP session
    session = requests.Session()
    # choose one random proxy
    proxy = random.choice(proxies)
    session.proxies = {"http": proxy, "https": proxy}
    return session


class Crawler(object):
    def __init__(self):
        self.internal_urls = set()
        self.external_urls = set()

    def reset(self):
        self.internal_urls = set()
        self.external_urls = set()

    def get_urls(self):
        return {
            'internal_urls': self.internal_urls,
            'external_urls': self.external_urls,
        }

    @timed
    def crawl(self, url, max_urls=50, verbose=True):
        """
        Crawls a web page and extracts all links.

        You'll find all links in `external_urls` and `internal_urls` global set variables.

        Parameters
        ----------
        url :
        max_urls : int
            number of max urls to crawl, default is 30.
        verbose :

        Returns
        -------

        """
        # initialize total urls
        total_urls_visited = 0

        # get all links from a website
        links = self.get_all_website_links(url)

        if verbose:
            print(f"Found {len(links)} website links at {url}.")

        for link in links:
            if total_urls_visited > max_urls:
                break
            self.crawl(link, max_urls=max_urls, verbose=verbose)

    def get_all_website_links(self, url):
        # all URLs of `url`
        urls = set()
        # domain name of the URL without the protocol
        domain_name = urlparse(url).netloc
        soup = bs(requests.get(url).content, "html.parser")

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue

            # join the URL if it's relative (not absolute link)
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not _is_valid(href):
                # not a valid URL
                continue
            if href in self.internal_urls:
                # already in the set
                continue
            if domain_name not in href:
                # external link
                if href not in self.external_urls:
                    logger.info(f"{GRAY}[!] External link: {href}{RESET}")
                    self.external_urls.add(href)
                continue
            logger.info(f"{GREEN}[*] Internal link: {href}{RESET}")
            urls.add(href)
            self.internal_urls.add(href)
        return urls

    def get_social_media_links(self, url):
        # initiate an HTTP session
        session = HTMLSession()

        # get the HTTP Response
        response = session.get(url)

        # for JAVA-Script driven websites
        response.html.render()

        social_media_regex = [
            TWITTER_REGEX,
            FACEBOOK_REGEX,
            INSTAGRAM_REGEX,
            LINKEDIN_REGEX,
        ]
        handle_list = []
        for regex in social_media_regex:
            for re_match in re.finditer(regex, response.html.raw_html.decode()):
                handle_found = re_match.group()
                handle_list.append(handle_found)
        return handle_list

@timed
def read_emails_from_webpage(url):
    # initiate an HTTP session
    session = HTMLSession()

    # get the HTTP Response
    response = session.get(url)

    # get the SOUP
    soup = bs(response.text, 'html.parser')

    # for JAVA-Script driven websites
    response.html.render()

    # search for emails
    email_list = set()
    for re_match in re.finditer(EMAIL_REGEX, response.html.raw_html.decode()):
        email_found = re_match.group()
        email_list.add(email_found)

    # search for phone numbers
    phone_list = set()
    for re_match in re.finditer(PHONE_REGEX, response.html.raw_html.decode()):
        phone_found = re_match.group()
        phone_list.add(phone_found)

    return email_list, phone_list

def generate_contact_email_table(emails, phone_numbers, urls, ):
    import pandas as pd
    school_df = pd.DataFrame((schools, urls, emails, phones, socials, date))
    pass

if __name__ == '__main__':
    MAX_URLS = 50
    verbose = True

    crawler = Crawler()
    # emails = dict()
    # phones = dict()
    # socials = dict()
    #
    # for school, urls in SCHOOL_SOCIAL_URLS.items():
    #     for url in urls:
    #         print(f"Looking thru {url} now...")
    #         email_list, phone_list = read_emails_from_webpage(url)
    #         social_handles = crawler.get_social_media_links(url)
    #
    #         # store in dictionary
    #         emails[school] = email_list
    #         phones[school] = phone_list
    #         socials[school] = social_handles
    #
    #         pprint(social_handles)
    #         pprint(emails)
    #         pprint(phones)
            # break

    for url in SCHOOL_URLS:
        print(f"Looking thru {url} now...")
        crawler.crawl(url, MAX_URLS, verbose)

        # get results
        all_school_urls = crawler.get_urls()

        # reset crawler
        crawler.reset()

        print(all_school_urls)
        break
