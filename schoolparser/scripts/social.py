import collections

import socials

from schoolparser.base import SCHOOL_URLS
from schoolparser.scrape import Crawler


def main():
    """Script to scrape social media handles.

    Operates on school URLs that have been manually added.
    """
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


if __name__ == "__main__":
    main()
