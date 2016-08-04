The code depends on these libraries:  

twitter
PyYAML

The best way to get them is usually: 

$ pip install <library>

Before running, edit the creds.yaml file to reflect relevant credentials.  You can find these values at https://apps.twitter.com/app/<your_app_id>/keys 

To run: 

$ python top_tweets.py

For help on options:

$ python top_tweets.py -h

There are two modes, rolling and static.  Rolling increments the max and min value of the tweet window in tandem, while static only increases the max value.  The default is rolling.

Notes:
- Curses doesn't support unicode all the time, so unicode chars are filtered out of the tweets before displaying them in curses.
- If curses tries to draw outside of the bounds of the terminal window, the program will crash (so, for instance, don't set the number of tweets to display too high; the defaults should work fine in a normal terminal).
