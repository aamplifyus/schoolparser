import logging
import os
from logging.handlers import RotatingFileHandler

schoolparser_log_name = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../", "logs", "schoolparser.log"
    )
)

logger = logging.getLogger(__name__)

# set logging level
logger.setLevel(logging.DEBUG)

# add file handler
file_handler = RotatingFileHandler(schoolparser_log_name, maxBytes=2000000, backupCount=10)
formatter = logging.Formatter(
    "%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.propagate = True

# list of school urls
SCHOOL_URLS = [
    'https://burtonhighschool.net/',

    'https://www.smuhsd.org/capuchinohigh',

    'https://www.sfusd.edu/school/balboa-high-school',
    'https://www.sfusd.edu/school/downtown-high-school',

    'https://www.ousd.org/castlemont',
    'https://echs.schoolloop.com/',
]

SCHOOL_SOCIAL_URLS = {
    'Burton hs': [
        'https://burtonhighschool.net/departments/socialsciences.html',
        'https://burtonhighschool.net/departments/counseling.html',
    ],
    'El Camino hs': [
        'https://sites.google.com/ssfusd.org/elcaminocounseling/contact?authuser=0',
    ],
    'Capuchino hs': [
        'https://www.smuhsd.org/domain/661',
        'https://www.smuhsd.org/domain/225',
    ],
    'Balboa hs': [
        'https://www.sfusd.edu/school/balboa-high-school/students/counseling-department'
    ],
    'Castlemont hs': [
        'https://www.ousd.org/domain/4032'
    ],
    'Downtown hs': [
        'https://www.sfusd.edu/school/downtown-high-school'
    ],
}
