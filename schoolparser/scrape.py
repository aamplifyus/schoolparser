import re
from urllib.parse import urlparse, urljoin

import colorama
import requests
from bs4 import BeautifulSoup as bs
from requests_html import HTMLSession

from email_validator import validate_email, EmailNotValidError


from schoolparser.base import logger

# init the colorama module
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET

# email address links
url = "https://www.randomlists.com/email-addresses"
EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""

# different regex patterns for phone numbers
# PHONE_REGEX = r"""\(?\b[2-9][0-9]{2}\)?[-][2-9][0-9]{2}[-][0-9]{4}\b"""
PHONE_REGEX = r"""(\(?\d{3}\)?[-]\d{3}\D{0,3}\d{4}).*?"""

# social media regex to grab urls
TWITTER_REGEX = r"""http(s)?:\/\/(.*\.)?twitter\.com\/[A-z0-9_]+\/?"""
LINKEDIN_REGEX = r"""http(s)?:\/\/([\w]+\.)?linkedin\.com\/in\/[A-z0-9_-]+\/?"""
FACEBOOK_REGEX = r"""http(s)?:\/\/(www\.)?(facebook|fb)\.com\/[A-z0-9_\-\.]+\/?"""
INSTAGRAM_REGEX = r"""https?:\/\/(www\.)?instagram\.com\/([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)"""


class Crawler(object):
    """Web-crawler for url links, and social media.

    To run crawler, initialize class and run ``crawl()`` function.
    """

    def __init__(self):
        self.internal_urls = set()
        self.external_urls = set()

    def reset(self):
        """Reset internal and external urls."""
        self.internal_urls = set()
        self.external_urls = set()

    def get_urls(self):
        """Return internal/external urls found as a dictionary."""
        return {
            "internal_urls": self.internal_urls,
            "external_urls": self.external_urls,
        }

    def crawl(self, url, max_urls=50, verbose=True):
        """
        Crawls a web page and extracts all links.

        You'll find all links in `external_urls` and `internal_urls` global set variables.

        Parameters
        ----------
        url : str
            The url to start crawling down.
        max_urls : int
            number of max urls to crawl, default is 30.
        verbose : bool
            Verbosity
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
        """Get all website links at a specific url.

        Parameters
        ----------
        url : str
            The url to search for website links.

        Returns
        -------
        urls : set
            A set of urls found.
        """
        # all URLs of `url`
        urls = set()
        # domain name of the URL without the protocol
        domain_name = urlparse(url).netloc

        try:
            soup = bs(
                requests.get(url).content, "html.parser", from_encoding="iso-8859-1"
            )
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
        """Get all social media links at specified url.

        Parameters
        ----------
        url : str
            Url to search for social media links.

        Returns
        -------
        handle_list : list
            A list of social media handles found.
        """
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


def _is_valid(url):
    """Check whether `url` is a valid URL."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def read_contactinfo_from_webpage(url, verbose=False):
    """Read email addresses and phone numbers from a webpage.

    Parameters
    ----------
    url : str
        URL to search for contact information from.

    Returns
    -------
    email_list : list
        List of found email addresses.
    phone_list : list
        List of found phone numbers.
    """
    # initiate an HTTP session
    session = HTMLSession()

    # get the HTTP Response
    response = session.get(url)

    # for JAVA-Script driven websites
    response.html.render(timeout=20)

    if verbose:
        print(f'[*] Crawling {url}...')

    # search for emails
    email_list = set()
    for re_match in re.finditer(EMAIL_REGEX, response.html.raw_html.decode()):
        email_found = re_match.group()
        if "familylink" in email_found:
            continue
        if not email_found.endswith('.org'):
            continue

        # check email
        is_new_account = True # False for login pages
        try:
            # Check that the email address is valid.
            validation = validate_email(email_found, check_deliverability=is_new_account)

            # Take the normalized form of the email address
            # for all logic beyond this point (especially
            # before going to a database query where equality
            # may not take into account Unicode normalization).  
            email_found = validation.email
        except EmailNotValidError as e:
            # Email is not valid.
            # The exception message is human-readable.
            print(str(e))
            continue
        email_list.add(email_found)

    # search for phone numbers
    phone_list = set()
    for re_match in re.finditer(PHONE_REGEX, response.html.raw_html.decode()):
        phone_found = re_match.group()
        phone_list.add(phone_found)

    return email_list, phone_list


def _scrape_contact_from_url(url, school_emails, school_phones, verbose=False):
    try:
        email_list, phone_list = read_contactinfo_from_webpage(url, verbose=verbose)
        # store in dictionary
        school_emails[url] = email_list
        school_phones[url] = phone_list
    except Exception as e:
        print(f'Problematic url: ', url)
    

