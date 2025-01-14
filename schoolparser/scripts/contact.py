import collections
from pathlib import Path

from joblib import Parallel, delayed
from tqdm import tqdm

from schoolparser.base import SCHOOL_SOCIAL_URLS
from schoolparser.scrape import _scrape_contact_from_url
from schoolparser.write import scraped_emails_to_df


def main():
    """Script to scrape contact informations.

    Operates on school URLs that have been manually added.
    """
    # where to save output excel file to
    datadir = Path("/Users/adam2392/Downloads/")
    fname = "school_tables_new.xls"
    overwrite = False

    if not datadir.exists():
        raise RuntimeError(f'Please set the output directory for AAMPLIFY correctly. '
                           f'The current one: {datadir} does not exist.')

    # store emails/phones per school as a list inside a dictionary
    emails = collections.defaultdict(dict)
    phones = collections.defaultdict(dict)

    # go through each school and scrape contact data
    _schools = []
    _urls = []
    for school, urls in SCHOOL_SOCIAL_URLS.items():
        _schools.extend([school] * len(urls))
        _urls.extend(urls)

    # run parallel scraping
    results = Parallel()(
        delayed(_scrape_contact_from_url)(url, emails[_schools[i]], phones[_schools[i]], verbose=True)
        for i, url in enumerate(tqdm(_urls))
    )

    # create data frame of output
    output_fpath = Path(datadir) / fname
    school_df = scraped_emails_to_df(emails, output_fpath, overwrite=overwrite)

    # check if any emails overlap with what we already have
    # school_df = pd.read_excel(output_fpath, index_col=None)
    # already_sent_emails = pd.read_excel(
    #     output_fpath, index_col=None, sheet_name="personalized"
    # )
    # already_sent_emails = already_sent_emails["emails"].tolist()
    # old_emails = []
    # for emails in already_sent_emails:
    #     split_emails = re.split(",|\n| ", emails)
    #     split_emails = [email for email in split_emails if email not in [""]]
    #     # print(split_emails)
    #     old_emails.extend(split_emails)
    # # print(old_emails)
    #
    # new_emails = [
    #     email for email in school_df["email"].tolist() if email not in old_emails
    # ]
    # print(*new_emails, sep=",")


if __name__ == "__main__":
    main()
