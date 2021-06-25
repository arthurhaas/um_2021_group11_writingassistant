#
# credits for information retrieval from HTML to
# https://github.com/otavio-s-s/data_science/tree/master/mediumScraper
#

import argparse
import csv
import datetime
import logging
import random
import requests

from bs4 import BeautifulSoup
from time import sleep

# logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
# requests
MU = 1
SIGMA = 0.5
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
}
# debug mode
DEBUG = False

def positive_gauss(mean, sigma):
    """
    Recursive call to normal distribution for positive onle values.
    """
    x = random.gauss(mean, sigma)
    return(x if x >= 0 else positive_gauss(mean,sigma))

def scraper(base_url, start_date, end_date):
    """
    Scraping medium stories based upon
        base_url: url of the medium publication, e.g. https://towardsdatascience.com/
        start_date: incl
        end_date: excl
    """

    with open('export_scraper.csv','w', encoding="utf-8") as export_file:
        # todo get line terminator by OS \n, \r\n
        writer=csv.writer(export_file, delimiter=',',lineterminator='\n', quotechar='"')
        columns = ['date', 'title', 'subtitle', 'claps', 'responses', 'author_url', 'story_url',
                'reading_time (mins)', 'number_sections', 'section_titles', 'number_paragraphs', 'paragraphs']
        writer.writerow(columns)

        current_date = start_date

        while current_date < end_date:
            date = current_date.strftime("%Y-%m-%d")
            url = f'{base_url}/archive/{current_date:%Y}/{current_date:%m}/{current_date:%d}'
            logging.info(f"Next scrape on: {url}")
            
            page = requests.get(url, headers=HEADERS)
            sleep(positive_gauss(MU, SIGMA))
            soup = BeautifulSoup(page.text, 'html.parser')

            stories = soup.find_all('div', class_='streamItem streamItem--postPreview js-streamItem')
            logging.info(f".. scraping {len(stories)} story pages")
            
            for i, story in enumerate(stories):
                logging.info(f".. {i+1} / {len(stories)}")
                each_story = scrape_stories(story)
                if each_story:
                    each_story = [current_date.strftime("%Y-%m-%d")] + each_story
                    writer.writerow(each_story)

            logging.info(f'.. done: {len(stories)} stories scraped for {current_date.strftime("%Y-%m-%d")}.')
            current_date = current_date + datetime.timedelta(days=1)



def scrape_stories(story):
    """
    Retrieves information from html with further request for page content.
    Cleans text of quoting char: double-quote "
    Returns
        []      Data for every story
        None    If reading time not exists, which is the case for articles with just a few sentences.
                Don't want them.
    """
    each_story = []

    # author
    author_box = story.find('div', class_='postMetaInline u-floatLeft u-sm-maxWidthFullWidth')
    author_url = author_box.find('a')['href']

    # reading time
    try:
        reading_time = author_box.find('span', class_='readingTime')['title']
    except:
        return None
    reading_time = reading_time.split()[0]

    # title and subtitle
    title = story.find('h3').text if story.find('h3') else '-'
    subtitle = story.find('h4').text if story.find('h4') else '-'

    # claps
    if story.find('button', class_='button button--chromeless u-baseColor--buttonNormal'
                                    ' js-multirecommendCountButton u-disablePointerEvents'):
        claps = story.find('button', class_='button button--chromeless u-baseColor--buttonNormal'
                                            ' js-multirecommendCountButton u-disablePointerEvents').text
    else:
        claps = 0

    # responses
    if story.find('a', class_='button button--chromeless u-baseColor--buttonNormal'):
        responses = story.find('a', class_='button button--chromeless u-baseColor--buttonNormal').text
    else:
        responses = '0 responses'
    responses = responses.split()[0]

    # story url
    story_url = story.find('a', class_='button button--smaller button--chromeless u-baseColor--buttonNormal')[
        'href']

    # story content: sections and paragraphs
    if DEBUG:
        (section_titles, story_paragraphs) = ([], [])
    else:
        (section_titles, story_paragraphs) = scrape_story_page(story_url)


    # report all properties
    each_story.append(title)
    each_story.append(subtitle)
    each_story.append(claps)
    each_story.append(responses)
    each_story.append(author_url)
    each_story.append(story_url)
    each_story.append(reading_time)
    each_story = list(map(lambda item: str(item).replace('"',''), each_story))

    each_story.append(len(section_titles))
    each_story.append(section_titles)
    each_story.append(len(story_paragraphs))
    each_story.append(story_paragraphs)

    return each_story


def scrape_story_page(story_url):
    """
    Request and retrieve information about story page.
    """
    story_page = requests.get(story_url, headers=HEADERS)
    sleep(positive_gauss(MU, SIGMA))
    story_soup = BeautifulSoup(story_page.text, 'html.parser')
    
    sections = story_soup.find_all('section')
    story_paragraphs = []
    section_titles = []
    for section in sections:
        paragraphs = section.find_all('p')
        for paragraph in paragraphs:
            story_paragraphs.append(paragraph.text)

        subs = section.find_all('h1')
        for sub in subs:
            section_titles.append(sub.text)

    section_titles = list(map(lambda item: str(item).replace('"',''), section_titles))
    story_paragraphs = list(map(lambda item: str(item).replace('"',''), story_paragraphs))

    return (section_titles, story_paragraphs)


if __name__ == "__main__":

    # parsing of arguments
    parser = argparse.ArgumentParser(description='Scraping for medium posts.')
    parser.add_argument('url', type=str,
                        help='The archive url from medium without date.')
    parser.add_argument('-s', '--start_date', type=datetime.date.fromisoformat, default="2020-01-01",
                        help='Starting date to scrape.')
    parser.add_argument('-e', '--end_date', type=datetime.date.fromisoformat, default="2020-01-02",
                        help='Ending date to scrape.')
    parser.add_argument('-d', '--debug', action='store_true', help="Debug mode, less requests")

    args = parser.parse_args()
    logging.info(f"Starting scraping with following arguments: {args}")
    DEBUG = args.debug

    # scraping
    scraper(args.url, args.start_date, args.end_date)
    
"""
# %%
import pickle
with open("sentences.pickle", "rb") as f:
    a = pickle.load(f)
"""
