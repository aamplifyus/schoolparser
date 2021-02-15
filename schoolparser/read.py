import collections
import logging
import re

import pandas as pd
import socials

from schoolparser.base import SCHOOL_URLS
from schoolparser.scrape import _scrape_contact_from_url
from schoolparser.write import scraped_emails_to_df

logger = logging.getLogger(__name__)
# scrapinghub crawlera
url = "http://icanhazip.com"
proxy_host = "proxy.crawlera.com"
proxy_port = "8010"
proxy_auth = "<APIKEY>:"
proxies = {
    "https": f"https://{proxy_auth}@{proxy_host}:{proxy_port}/",
    "http": f"http://{proxy_auth}@{proxy_host}:{proxy_port}/",
}


def _get_phone(soup, response):
    try:
        phone = soup.select("a[href*=callto]")[0].text
        return phone
    except:
        pass

    try:
        phone = re.findall(
            r"\(?\b[2-9][0-9]{2}\)?[-][2-9][0-9]{2}[-][0-9]{4}\b", response.text
        )[0]
        return phone
    except:
        pass

    try:
        phone = re.findall(
            r"\(?\b[2-9][0-9]{2}\)?[-. ]?[2-9][0-9]{2}[-. ]?[0-9]{4}\b", response.text
        )[-1]
        return phone
    except:
        phone = ""
        return phone


if __name__ == "__main__":
    MAX_URLS = 50
    verbose = True

    crawler = Crawler()
    emails = collections.defaultdict(dict)
    phones = collections.defaultdict(dict)

    """ SCRAPE SOCIAL HANDLES """
    social_handles = dict()
    for school_id, url in SCHOOL_URLS.items():
        print(f"Looking thru {url} now...")
        crawler.crawl(url, MAX_URLS, verbose)

        # get results
        all_school_urls = crawler.get_urls()
        internal_urls = all_school_urls["internal_urls"]

        HANDLES = ["twitter", "instagram", "linkedin", "facebook"]
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

    """ SCRAPE CONTACT INFO """
    # go through each school and scrape contact data
    _schools = []
    _urls = []
    for school, urls in SCHOOL_SOCIAL_URLS.items():
        _schools.extend([school] * len(urls))
        _urls.extend(urls)

    # run parallel scraping
    results = Parallel()(
        delayed(_scrape_contact_from_url)(url, emails[_schools[i]], phones[_schools[i]])
        for i, url in enumerate(tqdm(_urls))
    )

    # create data frame of output
    datadir = "/Users/adam2392/Google Drive - aamplify/AAMPLIFY/Marketing/Summer Program Outreach - Students and Schools/Bay Area High School Outreach"
    output_fpath = Path(Path(datadir) / "school_tables.xlsx")
    school_df = scraped_emails_to_df(emails, output_fpath)

    school_df = pd.read_excel(output_fpath, index_col=None)
    already_sent_emails = pd.read_excel(
        output_fpath, index_col=None, sheet_name="personalized"
    )
    already_sent_emails = already_sent_emails["emails"].tolist()
    old_emails = []
    for emails in already_sent_emails:
        split_emails = re.split(",|\n| ", emails)
        split_emails = [email for email in split_emails if email not in [""]]
        # print(split_emails)
        old_emails.extend(split_emails)
    # print(old_emails)

    new_emails = [
        email for email in school_df["email"].tolist() if email not in old_emails
    ]
    print(*new_emails, sep=",")
