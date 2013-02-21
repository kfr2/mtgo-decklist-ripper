"""
Rips MTGO decklists from the Wizards site into objects for storage, (and eventually) parsing, and analysis.
"""
import json
import logging
import sys

import requests

from models import Tournament


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='[%(levelname)s --> %(name)s] %(asctime)s:  %(message)s')
TOURNAMENT_INFO_URL = 'http://www.wizards.com/handlers/XMLListService.ashx?dir=mtgo&type=XMLFileInfo&start=7'
PROCESSED_TOURNAMENT_FILE = 'output/processed-tournaments.txt'
DEK_INDEX_FILE = 'output/dek-index.txt'


def get_tournaments():
    """
    Parses data feed of Wizard's MTGO decklist site[1].
    Returns a list of tournament objects or an empty list if an error occurs.
    [1] http://www.wizards.com/magic/Digital/MagicOnline.aspx?x=mtg/digital/magiconline/whatshappening
    """
    try:
        logger.info('Retrieving tournament feed.')
        content = requests.get(TOURNAMENT_INFO_URL).content
        items = json.loads(content)

        logger.info('%i tournaments were found' % len(items))

        with open(PROCESSED_TOURNAMENT_FILE, 'r+') as processed_tournaments_file:
            processed_tournaments = processed_tournaments_file.read().split(',')
            if processed_tournaments == ['']:
                processed_tournaments = []

            results = []
            for item in items:
                if item['Hyperlink'] in processed_tournaments:
                    logger.info('Skipping tournament %s' % item['Hyperlink'])
                    continue
                tournament = Tournament()
                tournament.hyperlink_id = item['Hyperlink']
                tournament.tournament_format = item['Name']
                tournament.tournament_date = item['Date']
                try:
                    logger.info('Processing tournament %s' % tournament.hyperlink_id)
                    for deck in tournament.decks:
                        deck.save()
                    processed_tournaments.append(tournament.hyperlink_id)
                    results.append(tournament)
                except:
                    logger.error('Error downloading tournament-specific information for tournament %s.' % tournament.hyperlink_id)

            processed_tournaments_file.write(','.join(processed_tournaments))

            return results
    except:
        print sys.exc_info()
        logger.error('An error occurred while downloading tournament information.')
        return []


if __name__ == '__main__':
    tournaments = get_tournaments()
    fh = open(DEK_INDEX_FILE, 'w')
    for tournament in tournaments:
        logger.info('%s: %s decks' % (tournament.hyperlink_id, tournament.num_decks))
        fh.write('%s #%s %s\n' % (tournament.tournament_date, tournament.hyperlink_id, tournament.tournament_format))
        for deck in tournament.decks:
            fh.write('%s. %s-%s.dek\n' % (deck.num, deck.tournament_id, deck.num))
        fh.write('======\n')
    fh.close()
    logger.info('Done downloading dek files.')

