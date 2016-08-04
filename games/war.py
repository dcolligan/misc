#!/usr/bin/env python

"""Simulates the card game war"""

__author__ = 'Danny Colligan'
__email__ = 'dannycolligan@gmail.com'

import random
import logging
import argparse


class Card(object):

   suit_repr = {
         'Club' : u'\u2667',
         'Diamond' : u'\u2662',
         'Spade' : u'\u2664',
         'Heart' : u'\u2661',
   }

   rank_repr = {
         2 : '2',
         3 : '3',
         4 : '4',
         5 : '5',
         6 : '6',
         7 : '7',
         8 : '8',
         9 : '9',
         10 : '10',
         11 : 'J',
         12 : 'Q',
         13 : 'K',
         14 : 'A',
   }

   def __init__(self, suit, rank):
      self.suit = suit
      self.rank = rank

   def __str__(self):
      return '%s%s' % (self.rank_repr[self.rank], self.suit_repr[self.suit].encode('utf-8'))


class Deck(object):

   suits = Card.suit_repr.keys()
   ranks = Card.rank_repr.keys()

   def __init__(self):
      self.cards = []
      for rank in self.ranks:
         for suit in self.suits:
            card = Card(suit, rank)
            self.cards.append(card)

   def shuffle(self):
      random.shuffle(self.cards)

   def __str__(self):
      s = []
      for card in self.cards:
         s.append(card.__str__())
         s.append('\n')
      return ''.join(s)


class HandEmptyError(Exception): pass


class Hand(object):

   def __init__(self):
      self.cards = []

   def take(self):
      if self.cards:
         return self.cards.pop()
      else:
         raise HandEmptyError()

   def put(self, *cards):
      for card in cards:
         self.cards.insert(0, card)

   def is_empty(self):
      return not bool(len(self.cards))

   def __len__(self):
      return len(self.cards)


class War(object):

   num_facedown = 3

   def __init__(self, args):
      self.args = args
      self.deck = Deck()
      self.deck.shuffle()
      self.hand1 = Hand()
      self.hand2 = Hand()
      while len(self.deck.cards) > 0:
         self.hand1.put(self.deck.cards.pop())
         self.hand2.put(self.deck.cards.pop())

   def winner(self):
      if self.hand1.is_empty():
         return 2
      elif self.hand2.is_empty():
         return 1
      else:
         return None

   def play(self):
      try:
         while not self.winner():
            self.checks()
            self.play_round()
            if self.args.slow:
               logging.info("(Hit return to continue game)")
               raw_input()
      except HandEmptyError, e:
         logging.info('player %s out of cards' % e.message)
      return self.winner()

   def checks(self):
      assert len(self.hand1) + len(self.hand2) == len(self.deck.suits) * len(self.deck.ranks)

   def play_round(self):
      card1 = self.hand1.take()
      card2 = self.hand2.take()
      logging.info('ROUND %s %s' % (card1, card2))
      if card1.rank > card2.rank:
         logging.info('player 1 wins')
         self.hand1.put(card1, card2)
      elif card2.rank > card1.rank:
         logging.info('player 2 wins')
         self.hand2.put(card1, card2)
      elif card1.rank == card2.rank:
         logging.info('tie')
         tie_cards = [card1, card2]
         winner = self.tie_resolution(tie_cards)
         if winner == 1:
            self.hand1.put(*tie_cards)
         if winner == 2:
            self.hand2.put(*tie_cards)
      else:
         raise Exception("Shouldn't happen")
      logging.info('p1 cards: %s p2 cards: %s' % (len(self.hand1), len(self.hand2)))

   def tie_resolution(self, tie_cards):
      logging.info('resolution')
      hand1facedown = [self.hand1.take() for _ in range(self.num_facedown)]
      hand2facedown = [self.hand1.take() for _ in range(self.num_facedown)]
      hand1card = self.hand1.take()
      hand2card = self.hand2.take()
      cards = [hand1card, hand2card] + hand1facedown + hand2facedown
      tie_cards.extend(cards)
      logging.info('%s %s' % (hand1card, hand2card))
      if hand1card.rank > hand2card.rank:
         logging.info('player 1 wins')
         return 1
      elif hand1card.rank < hand2card.rank:
         logging.info('player 2 wins')
         return 2
      elif hand1card.rank == hand2card.rank:
         return self.tie_resolution(tie_cards)
      else:
         raise Exception("Shouldn't happen")

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description="Simulates the card game War")
   parser.add_argument("--log-level", help="what level to log at", default='INFO')
   parser.add_argument("--slow", action='store_const', help="slow down the game", default=False, const=True)
   args = parser.parse_args()

   logging.basicConfig(format='%(message)s', level=getattr(logging, args.log_level))

   war = War(args)
   winner = war.play()
   logging.info('PLAYER %s WINS!' % winner)

