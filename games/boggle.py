#!/usr/bin/env python

"""Simulates games of Boggle"""

__author__ = 'Danny Colligan'
__email__ = 'dannycolligan@gmail.com'

import string
import random
import pprint

default_dictionary_filename = 'dictionary.txt'
default_rows = 5
default_cols = 5

class PrefixTree(object):
   """A tree of all words in the dictionary, one letter per level"""

   end_of_word_key = 'xxx' # can't be a word in the dictionary
    
   def __init__(self, dictionary_filename):
      self.d = self._new_dict()
      f = file(dictionary_filename)
      lines = f.readlines()
      f.close()
      for line in lines:
         self.add_word(line[:-1])

   def add_word(self, word):
      """Adds a word to the tree"""
      cur = self.d
      for letter in word:
         if not letter in cur:
            cur[letter] = self._new_dict()
         cur = cur[letter]
      cur[self.end_of_word_key] = True
        
   def is_prefix(self, prefix):
      """Returns true if prefix is a prefix of any word in the dictionary, false otherwise"""
      return self._traverse(prefix, False)
        
   def is_word(self, word):
      """Returns true if word is a word in the dictionary, false otherwise"""
      return self._traverse(word, True)
      # note: to save time, we could store a set of all dictionary words
      # and just do a membership lookup here at the expense of storing the dictionary words twice

   def _traverse(self, word, b):
      cur = self.d
      for letter in word:
         if letter in cur:
            cur = cur[letter]
         else:
            return False
      return cur[self.end_of_word_key] == b

   def _new_dict(self):
      return { self.end_of_word_key : False }
        

class BoggleBoard(object):
   """A Boggle board"""

   def __init__(self, num_rows, num_cols):
      self.num_rows = num_rows
      self.num_cols = num_cols
      self.b = [[random.choice(string.ascii_lowercase) for _ in xrange(num_cols)] for _ in xrange(num_rows)]

   def __str__(self):
      return pprint.pformat(self.b)


class BoggleGame(object):
   """A Boggle game"""

   def __init__(self, num_rows, num_cols, dictionary_filename):
      self.board = BoggleBoard(num_rows, num_cols)
      self.tree = PrefixTree(dictionary_filename)

   def find_words(self):
      """Find the words in the Boggle board"""
      results = set()
      for i, row in enumerate(self.board.b):
         for j, col in enumerate(row):
            results.update(self._fw([(i, j)]))
      return results
    
   def _fw(self, pos):
      i = pos[-1][0]  
      j = pos[-1][1]  
      results = set()
      
      word = ''.join((self.board.b[p[0]][p[1]] for p in pos))
      if self.tree.is_word(word):
         results.add(word)   
           
      if not self.tree.is_prefix(word):
         return results
       
      coords = [(i + 1, j), (i, j + 1), (i - 1, j), (i, j - 1), (i + 1, j + 1), (i - 1, j - 1), (i + 1, j - 1), (i - 1, j + 1)]
      for coord in coords:
         x, y = coord[0], coord[1]
         if coord not in pos \
            and 0 <= x < self.board.num_rows \
            and 0 <= y < self.board.num_cols:
            results.update(self._fw(pos + [coord]))
               
      return results


if __name__ == '__main__':
   dictionary_filename = default_dictionary_filename
   num_rows = default_rows
   num_cols = default_cols

   game = BoggleGame(num_rows, num_cols, dictionary_filename)
   print game.board
   words = game.find_words()
   print '\nFound %s words: %s\n' % (len(words), list(words))
