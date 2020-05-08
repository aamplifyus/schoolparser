import collections
import datetime
import logging
import random
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin
import socials
import colorama
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from joblib import Parallel, delayed
from requests_html import HTMLSession
from tqdm import tqdm

from schoolparser.base import SCHOOL_SOCIAL_URLS, SCHOOL_URLS, timed

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
PHONE_REGEX = r"""(\(?\d{3}\)?[-]\d{3}\D{0,3}\d{4}).*?"""
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

        try:
            soup = bs(requests.get(url).content, "html.parser", from_encoding="iso-8859-1")
        except Exception as e:
            print(e)
            return []

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

        try:
            # for JAVA-Script driven websites
            response.html.render()
        except Exception as e:
            print(url, e)
            return []

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

    # for JAVA-Script driven websites
    response.html.render()

    # search for emails
    email_list = set()
    for re_match in re.finditer(EMAIL_REGEX, response.html.raw_html.decode()):
        email_found = re_match.group()
        if 'familylink' in email_found:
            continue
        email_list.add(email_found)

    # search for phone numbers
    phone_list = set()
    for re_match in re.finditer(PHONE_REGEX, response.html.raw_html.decode()):
        phone_found = re_match.group()
        phone_list.add(phone_found)

    return email_list, phone_list


def generate_contact_email_table(emails, output_fpath):
    # generate list of dictionaries
    rows = []
    for school, url_list in emails.items():
        for url, email_list in url_list.items():
            for email in email_list:
                row = collections.OrderedDict()
                row['school'] = school
                row['url'] = url
                row['email'] = email
                row['date'] = datetime.datetime.now()
                rows.append(row)

    # create the dataframe
    school_df = pd.DataFrame(rows)
    school_df['Owner'] = ''
    school_df['Notes'] = ''
    print(school_df)
    school_df.to_excel(output_fpath, index=None)

def generate_contact_phone_table(phones, output_fpath):
    pass


def _scrape_contact_from_url(url, school_emails, school_phones):
    email_list, phone_list = read_emails_from_webpage(url)
    # store in dictionary
    school_emails[url] = email_list
    school_phones[url] = phone_list
    return email_list, phone_list


if __name__ == '__main__':
    MAX_URLS = 50
    verbose = True

    crawler = Crawler()
    emails = collections.defaultdict(dict)
    phones = collections.defaultdict(dict)

    ''' SCRAPE SOCIAL HANDLES '''
    social_handles = dict()
    for school_id, url in SCHOOL_URLS.items():
        print(f"Looking thru {url} now...")
        crawler.crawl(url, MAX_URLS, verbose)

        # get results
        all_school_urls = crawler.get_urls()
        internal_urls = all_school_urls['internal_urls']

        HANDLES = ['twitter', 'instagram', 'linkedin', 'facebook']
        social_handles[school_id] = dict.fromkeys(HANDLES)
        for url in internal_urls:
            handle_list = crawler.get_social_media_links(url)
            if len(handle_list) > 0:
                handle_dict = socials.extract(handle_list).get_matches_per_platform()
                social_handles[school_id].update(**handle_dict)
                if all(key in social_handles[school_id].keys() for key in HANDLES):
                    break

        # reset crawler
        crawler.reset()

        # print(all_school_urls)
        # break
    print(social_handles)

    ''' SCRAPE CONTACT INFO '''
    # go through each school and scrape contact data
    # _schools = []
    # _urls = []
    # for school, urls in SCHOOL_SOCIAL_URLS.items():
    #     _schools.extend([school] * len(urls))
    #     _urls.extend(urls)
    #
    # # run parallel scraping
    # results = Parallel()(
    #     delayed(_scrape_contact_from_url)
    #     (url, emails[_schools[i]], phones[_schools[i]])
    #     for i, url in enumerate(tqdm(_urls))
    # )
    #
    # # create data frame of output
    # datadir = "/Users/adam2392/Google Drive - aamplify/AAMPLIFY/Marketing/Summer Program Outreach - Students and Schools/Bay Area High School Outreach"
    # output_fpath = Path(Path(datadir) / 'school_tables.xlsx')
    # school_df = generate_contact_email_table(emails, output_fpath)

    # school_df = pd.read_excel(output_fpath, index_col=None)
    # already_sent_emails = pd.read_excel(output_fpath, index_col=None,
    #                                     sheet_name='personalized')
    # already_sent_emails = already_sent_emails['emails'].tolist()
    # old_emails = []
    # for emails in already_sent_emails:
    #     split_emails = re.split(',|\n| ', emails)
    #     split_emails = [email for email in split_emails if email not in ['']]
    #     # print(split_emails)
    #     old_emails.extend(split_emails)
    # # print(old_emails)
    #
    # new_emails = [email for email in school_df['email'].tolist() if email not in old_emails]
    # print(*new_emails, sep=',')

