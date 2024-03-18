import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

schoolparser_log_name = Path(os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../", "logs", "schoolparser.log"
    )
))
schoolparser_log_name.parent.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)

# set logging level
logger.setLevel(logging.DEBUG)

# add file handler
file_handler = RotatingFileHandler(
    schoolparser_log_name, maxBytes=2000000, backupCount=10
)
formatter = logging.Formatter(
    "%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.propagate = True

# list of school urls
SCHOOL_URLS = {
    'Gunderson hs': 'https://gunderson.sjusd.org/student-resources/college-career/',
    'Leland hs': 'https://leland.sjusd.org/student-resources/academic-counseling/',
    'Pioneer hs': 'https://www.pioneerschools.org/o/phs/page/guidance-office',
    'Willow Glen hs': 'https://wghs.sjusd.org/student-resources/college-career/',
    'Aragon hs': 'https://www.smuhsd.org/Page/1591',
    "Burton hs": "https://burtonhighschool.net/",
    "Capuchino hs": "https://www.smuhsd.org/capuchinohigh",
    "BALBOA HS": "https://www.sfusd.edu/school/balboa-high-school",
    "DOWNTOWN HS": "https://www.sfusd.edu/school/downtown-high-school",
    "CASTLEMONT HS": "https://www.ousd.org/castlemont",
    "SCHOOL LOOP": "https://echs.schoolloop.com/",
    "El Camino hs": "https://sites.google.com/ssfusd.org/elcaminocounseling/",
    # 'Galileo hs': 'https://sites.google.com/sfusd.edu/galileocounselingdepartment/contact-us?authuser=0',,
    "Ida B Wells hs": "https://www.sfusd.edu/school/ida-b-wells-high-school/",
    "Independence hs": "https://www.sfusd.edu/school/independence-high-school",
    # 'Jefferson hs':
    #     'https://www.juhsd.net/Page/553'
    # ,
    "John O'Connell hs": "https://www.sfusd.edu/school/john-oconnell-high-school/",
    # 'June Jordan hs': ,
    "Abraham Lincoln hs": "https://www.sfusd.edu/school/abraham-lincoln-high-school",
    "Lowell hs": "https://www.sfusd.edu/school/lowell-high-school/",
    'Mills hs': 'https://www.smuhsd.org/domain/840',
    "Mission hs": "https://www.sfusd.edu/school/mission-high-school/",
    'Oakland hs': 'https://www.ousd.org/',
    'Oceana hs': 'https://www.juhsd.net/domain/50',
    # 'Raoul Wallenberg Traditional hs': 'https://www.sfusd.edu/school/raoul-wallenberg-traditional-high-school/',
    "Ruth Asawa San Francisco School of the Arts hs": "https://www.sfusd.edu/school/ruth-asawa-san-francisco-school-arts/",
    'San Mateo hs': 'https://www.smuhsd.org/',
    "Sequoia hs": "https://www.sequoiahs.org/",
    # 'South San Francisco hs':
    #     'https://ssfhs.schoolloop.com/job_listings',
    # ,
    "St. Ignatius hs": "https://www.siprep.org/si-academics/",
    # 'Terra Nova hs':
    #     'https://www.juhsd.net/Page/703',
    # ,
    "Thurgood Marshall hs": "https://www.sfusd.edu/school/thurgood-marshall-academic-high-school/",
    'Washington hs':
        'https://sites.google.com/sfusd.edu/counseling/counselors/'
    ,
    'Westmoor hs': 'https://www.juhsd.net/',
}

SCHOOL_SOCIAL_URLS = {
    'Gunderson hs': ['https://gunderson.sjusd.org/student-resources/college-career/'],
    'Leland hs': ['https://leland.sjusd.org/student-resources/academic-counseling/'],
    'Pioneer hs': ['https://www.pioneerschools.org/o/phs/page/guidance-office'],
    'Willow Glen hs': ['https://wghs.sjusd.org/student-resources/college-career/'],
    'Aragon hs': ['https://www.smuhsd.org/Page/1591'],
    "Burton hs": [
        "https://burtonhighschool.net/departments/socialsciences.html",
        "https://burtonhighschool.net/departments/counseling.html",
    ],
    "Capuchino hs": [
        "https://www.smuhsd.org/domain/661",
        "https://www.smuhsd.org/domain/225",
    ],
    "Balboa hs": [
        "https://www.sfusd.edu/school/balboa-high-school/students/counseling-department"
    ],
    "Castlemont hs": ["https://www.ousd.org/domain/4032"],
    "Downtown hs": ["https://www.sfusd.edu/school/downtown-high-school"],
    "El Camino hs": [
        "https://sites.google.com/ssfusd.org/elcaminocounseling/contact?authuser=0",
    ],
    "Galileo hs": [
        "https://sites.google.com/sfusd.edu/galileocounselingdepartment/contact-us?authuser=0",
    ],
    "Ida B Wells hs": [
        "https://www.sfusd.edu/school/ida-b-wells-high-school/about-our-school/staff-directory",
    ],
    "Independence hs": ["https://www.sfusd.edu/school/independence-high-school"],
    "Jefferson hs": ["https://www.juhsd.net/Page/553"],
    "John O'Connell hs": [
        "https://www.sfusd.edu/school/john-oconnell-high-school/student-services/counseling-services"
    ],
    "June Jordan hs": ["https://www.jjse.org/"],
    "Skyline hs": ["https://www.ousd.org/skyline.about.faculty-staff"],
    "Oakland Technical hs": ["https://oaklandtech.com/staff/counseling/"],
    "Abraham Lincoln hs": ["https://www.sfusd.edu/school/abraham-lincoln-high-school"],
    "Lowell hs": [
        "https://www.sfusd.edu/school/lowell-high-school/school-information/contact-information"
    ],
    "Mills hs": [
        "https://www.smuhsd.org/domain/840",
        "https://www.smuhsd.org/domain/206",
    ],
    "Mission hs": [
        "https://www.sfusd.edu/school/mission-high-school/our-teams/counselors",
        "https://www.sfusd.edu/school/mission-high-school/our-teams/teachers/social-studies-department",
    ],
    "Oakland hs": [
        "https://www.ousd.org/domain/1723",
        "https://www.ousd.org/Page/5634",
    ],
    "Oceana hs": [
        "https://www.juhsd.net/domain/50",
    ],
    "Raoul Wallenberg Traditional hs": [
        "https://www.sfusd.edu/school/raoul-wallenberg-traditional-high-school/school-info/departments/social-studies",
        "https://www.sfusd.edu/school/raoul-wallenberg-traditional-high-school/students/counseling",
    ],
    "Ruth Asawa San Francisco School of the Arts hs": [
        "https://www.sfusd.edu/school/ruth-asawa-san-francisco-school-arts/academics/academic-counseling",
    ],
    "San Mateo hs": [
        "https://www.smuhsd.org/domain/722",
        "https://www.smuhsd.org/domain/221",
    ],
    "Sequoia hs": ["https://www.sequoiahs.org/DEPARTMENT/Social-Studies/index.html"],
    "South San Francisco hs": [
        "https://ssfhs.schoolloop.com/job_listings",
    ],
    "St. Ignatius hs": [
        "https://www.siprep.org/si-academics/academic-departments/counseling/counseling/meet-your-counselors",
    ],
    "Terra Nova hs": [
        "https://www.juhsd.net/Page/703",
    ],
    "Thurgood Marshall hs": [
        "https://www.sfusd.edu/school/thurgood-marshall-academic-high-school/student/counseling-department/meet-counselors"
    ],
    "Washington hs": ["https://sites.google.com/sfusd.edu/counseling/counselors/"],
    "Westmoor hs": [
        "https://www.juhsd.net/Page/940",
        "https://www.juhsd.net/domain/209",
    ],
}
