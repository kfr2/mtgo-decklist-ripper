import logging
from time import sleep

import requests
from BeautifulSoup import BeautifulSoup


logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname)s --> %(name)s] %(asctime)s:  %(message)s')
logger.setLevel(logging.INFO)


class Deck(object):
    def __init__(self):
        self.tournament_id = None  # fk -> Tournament
        self.num = None  # the deck's number within its tournament
        self.category = None  # 'Red Deck Wins', 'Team America', etc
        self.content = None

    def __str__(self):
        return 'Deck %s-%s' % (self.tournament_id, self.num)

    @property
    def url(self):
        """
        Returns a URL to the .dek file for this deck.
        """
        return 'http://www.wizards.com/magic/mtgdigitalmagiconlinetourn%sx%s.dek?x=mtg/digital/magiconline/tourn/%s&decknum=%s' % (
            self.tournament_id, self.num, self.tournament_id, self.num)

    def retrieve(self):
        """
        Retrieves this Deck's .dek file and stores it in `content`
        """
        try:
            logger.info('Retrieving %s' % self)
            self.content = requests.get(self.url).content
        except:
            logger.error('Error loading requested dek: %s' % self)

    def save(self, filename=None):
        """
        Writes this deck's `content` to the specified filename or 
        `output/deks/` with the filename tournament_id-num.dek if
        filename is not specified.
        """
        if filename is None:
            filename = 'output/deks/%s-%s.dek' % (self.tournament_id, self.num)
        if self.content:
            fh = open(filename, 'w')
            fh.write(self.content + '\n')
            fh.close()
            logger.info('%s has been written to %s' % (self, filename))
        else:
            logger.info('%s has no content.  Not writing.' % self)


class Tournament(object):
    def __init__(self):
        # hyperlink_id stores the Wizard's tournament ID
        self.hyperlink_id = None
        # format refers to the tournament type -- 'Momir Basic', 'Pauper', etc
        self.tournament_format = None
        self.tournament_date = None
        self._content = None
        self._num_decks = None
        self._decks = []

    def __str__(self):
        return 'Tournament %s' % self.hyperlink_id

    @property
    def url(self):
        """
        Returns a URL containing deck information for this tournament.
        """
        return 'http://www.wizards.com/magic/Digital/MagicOnlineTourn.aspx?x=mtg/digital/magiconline/tourn/%s'\
            % self.hyperlink_id

    @property
    def content(self):
        """
        Returns the HTML of this tournament if it has already been retrieved;
        otherwise, it retrieves the content, sets it to _content, and returns it.
        """
        if not self._content:
            try:
                logger.info('Retrieving the content of %s' % self)
                self._content = requests.get(self.url).content
            except:
                logger.error('Error loading requested tournament page: %s' % self.url)
                exit()
        return self._content

    @property
    def num_decks(self):
        """
        Parses the tournament's `content` to determine the number of deck results
        contained within it.
        """
        if not self._num_decks:
            html = BeautifulSoup(self.content)
            try:
                # Find the number of rows in the results table (-1 to remove the header row).
                self._num_decks = len(html.find('table', width='90%').findAll('tr')) - 1
            except:
                logger.error('Error locating the Standings table in the tournament content.')
                exit()
        return self._num_decks

    @property
    def decks(self):
        """
        Returns the list of Decks within this tournament, first retrieving them if necessary.
        """
        if not self._decks:
            logger.info('Retrieving %s decks for %s' % (self.num_decks, self))
            for i in xrange(1, self.num_decks):
                deck = Deck()
                deck.tournament_id = self.hyperlink_id
                deck.num = i
                deck.retrieve()
                self._decks.append(deck)
                sleep(0.2) 
        return self._decks

