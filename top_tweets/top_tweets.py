#!/usr/bin/env python

"""Performs a rolling frequency count of top Twitter retweets
via the Twitter streaming API and displays rolling updates 
in the terminal window"""

__author__ = 'Danny Colligan'
__email__ = 'dannycolligan@gmail.com'

import twitter
import curses
import argparse
import yaml
import datetime


class Context(object):
   """Container class for a number of variables"""

   def __init__(self):
      self.debug = False


class Status(object):
   """Container class for tracking the status of the process"""

   def __init__(self):
      self.num_tweets_processed = 0
      self.num_retweets_processed = 0


class RetweetCacheBase(object):
   """A cache of the most frequently retweeted tweets - base"""

   def __init__(self):
      self.cache = {}

   def process_tweet(self, retweet_id, retweet_text, retweet_date):
      """Increment the count of a retweet in the cache, if applicable"""
      raise NotImplementedError

   def get_top_n(self, n):
      """Return the top n retweets"""
      return sorted(self.cache.values(), key=lambda retweet: retweet.get_count(), reverse=True)[:n]

   def purge_redundant(self):
      """Get rid of data in the cache that is redundant"""
      raise NotImplementedError


class RetweetCacheRolling(RetweetCacheBase):
   """A cache of the most frequently retweeted tweets - rolling"""

   def __init__(self):
      super(RetweetCacheRolling, self).__init__()

   def process_tweet(self, retweet_id, retweet_text, retweet_date):
      """Increment the count of a retweet in the cache, if applicable"""
      now = datetime.datetime.utcnow()
      if retweet_date < now - context.delta:
         return
      if retweet_id in self.cache:
         self.cache[retweet_id].dates.append(retweet_date)
      else:
         self.cache[retweet_id] = RetweetRolling(retweet_id, retweet_text, retweet_date)

   def purge_redundant(self):
      """Get rid of tweet dates that are expired"""
      now = datetime.datetime.utcnow()
      for key, retweet in self.cache.items():
         new_dates = []
         for date in retweet.dates:
            if date >= now - context.delta:
               new_dates.append(date)
         if not new_dates:
            del self.cache[key]
         else:
            self.cache[key].dates = new_dates


class RetweetCacheStatic(RetweetCacheBase):
   """A cache of the most frequently retweeted tweets - static"""

   def __init__(self):
      super(RetweetCacheStatic, self).__init__()

   def process_tweet(self, retweet_id, retweet_text, retweet_date):
      """Increment the count of a retweet in the cache, if applicable"""
      if retweet_date < context.start_date:
         return
      if retweet_id in self.cache:
         self.cache[retweet_id].count += 1
      else:
         self.cache[retweet_id] = RetweetStatic(retweet_id, retweet_text)

   def purge_redundant(self):
      """Can't purge anything in static mode"""


class RetweetBase(object):
   """The base class for retweets in the cache"""

   def __init__(self, retweet_id, text):
      self.retweet_id = retweet_id
      self.text = text.encode('utf-8')

   def get_count(self):
      """Returns the count of this tweet"""
      raise NotImplementedError


class RetweetRolling(RetweetBase):
   """A retweet in the cache - rolling mode"""

   def __init__(self, retweet_id, text, date):
      super(RetweetRolling, self).__init__(retweet_id, text)
      self.dates = [date] 

   def get_count(self):
      return len(self.dates)


class RetweetStatic(RetweetBase):
   """A retweet in the cache - static mode"""

   def __init__(self, retweet_id, text):
      super(RetweetStatic, self).__init__(retweet_id, text)
      self.count = 1

   def get_count(self):
      return self.count


def refresh_window(window, top_retweets):
   # Headers
   window.addstr(0, 0, 'Running... press CTRL-C to halt')
   window.addstr(1, 0, 'Tweets seen: %s' % status.num_tweets_processed)
   window.addstr(2, 0, 'Retweets seen: %s' % status.num_retweets_processed)
   if context.mode == 'static':
      window_start = context.start_date
   elif context.mode == 'rolling':
      window_start = datetime.datetime.now() - context.delta
   window_end = datetime.datetime.now()
   window.addstr(3, 0, 'Window start: %s' % window_start)
   window.addstr(4, 0, 'Window end: %s' % window_end)


   format_str = '%6s%30s%10s%30s'
   window.addstr(6, 0, format_str % ('rank', 'id', 'count', 'text'))

   # Data
   row_index = 7
   for i, tweet in enumerate(top_retweets):
      tweet_format_str = '%6s%30s%10s%30s'
      # curses doesn't play nice with unicode, so remove those chars
      # also, remove newlines because they screw up formatting
      tweet_str_text = ''.join([x for x in tweet.text.replace('\n', ' ') if ord(x) < 128][:20]) + '...'
      tweet_str = tweet_format_str % (i + 1, tweet.retweet_id, tweet.get_count(), tweet_str_text)
      window.addstr(row_index, 0, tweet_str)
      row_index += 1

   # Debug 
   if context.debug:
      window.addstr(row_index, 0, str(len(retweet_cache.cache)))
   window.refresh()

def process_tweet(tweet, window):
   try:
      # retweet_count field (how many times current tweet was retweeted) 
      # always is zero (at least, in the thousands of tweets I have seen)
      # so I have disregarded it
      if 'retweeted_status' in tweet:
         retweet = tweet['retweeted_status']
         retweet_id = retweet['id']
         retweet_text = retweet['text']
         retweet_created_at = retweet['created_at']
         retweet_date = datetime.datetime.strptime(retweet_created_at,'%a %b %d %H:%M:%S +0000 %Y')
         retweet_cache.process_tweet(retweet_id, retweet_text, retweet_date)
         status.num_retweets_processed += 1
   except KeyError as e:
      pass
   status.num_tweets_processed += 1
   if status.num_tweets_processed % context.reporting_gap:
      top_retweets = retweet_cache.get_top_n(context.num_tweets)
      retweet_cache.purge_redundant()
      refresh_window(window, top_retweets)

def parse_args():
   parser = argparse.ArgumentParser(description='Displays the top N retweeted tweets from a stream of tweets')
   parser.add_argument('mode', type=str, nargs='?',
      help='the mode to run in', choices=['static', 'rolling'], default='rolling')
   parser.add_argument('--num-tweets', metavar='N', type=int,
      help='the number of tweets to display (default 10)', default=10)
   parser.add_argument('--creds-filepath', metavar='F', type=str,
      help='the location of the creds file', default='creds.yaml')
   parser.add_argument('--reporting-gap', metavar='R', type=int,
      help='how many tweets to process before refreshing display', default=100)
   parser.add_argument('--minutes-ago', metavar='M', type=int,
      help='minutes before which tweets should be disregarded', default=10)
   args = parser.parse_args()

   context.num_tweets = args.num_tweets
   context.reporting_gap = args.reporting_gap
   context.minutes_ago = args.minutes_ago
   context.mode = args.mode

   now = datetime.datetime.utcnow()
   delta = datetime.timedelta(minutes=context.minutes_ago)
   context.delta = delta
   context.start_date = now - delta

   # parse YAML file
   f = file(args.creds_filepath)
   cred_data = yaml.load(f)
   f.close()
   context.token = cred_data['token']
   context.token_key = cred_data['token_key']
   context.con_secret = cred_data['con_secret']
   context.con_secret_key = cred_data['con_secret_key']

def main(window):
   refresh_window(window, [])
   auth = twitter.OAuth(context.token, context.token_key, context.con_secret, context.con_secret_key)
   stream = twitter.TwitterStream(auth=auth)
   iterator = stream.statuses.sample()
   for tweet in iterator:
      process_tweet(tweet, window)


status = Status()
context = Context()
if __name__ == '__main__':
   parse_args()
   if context.mode == 'static':
      retweet_cache = RetweetCacheStatic()
   elif context.mode == 'rolling':
      retweet_cache = RetweetCacheRolling()
   try:
      curses.wrapper(main)
   except KeyboardInterrupt:
      pass
