#!/usr/bin/env python
"""Get follower stats for our Twitter accounts & add them to a database"""

# Import the required Python modules
import os
import sys
import ConfigParser
import sqlite3
from twitter import *

# Get configuration file
base_path = os.path.expanduser('~/.twitter-stats')
config_file_path = os.path.join(base_path, 'config')
config = ConfigParser.ConfigParser()
config.read(config_file_path)

# Read the Twitter authentication info from config file
section = 'twitter-auth'
consumer_key = config.get(section, 'consumer_key')
consumer_secret = config.get(section, 'consumer_secret')
token = config.get(section, 'token')
token_secret = config.get(section, 'token_secret')

# Read the list of Twitter users to track from config file
section = 'twitter'
user_list = config.get(section, 'user_list')

# Create the Twitter authentication object
authobject = OAuth(
    consumer_key = consumer_key,
    consumer_secret = consumer_secret,
    token = token,
    token_secret = token_secret
)

# Create the Twitter object we use for queries
t = Twitter(auth=authobject)

# Get the latest count of followers for the requested Twitter accounts
result_list = None
result_list = t.users.lookup(screen_name=user_list)

# Exit if we don't have a valid result
if not result_list:
    print 'Something went wrong when querying twitter.  Exiting'
    sys.exit(1)

# Open the database (auto created on the fly if it doesn't exist)
db_filename = 'stats.db'
db_path = os.path.join(base_path, 'db', db_filename)
conn = sqlite3.connect(db_path)

# Connect to the database
c = conn.cursor()

# Create a SQLite3 table to hold the data if it doesn't already exist
sql = ('CREATE TABLE IF NOT EXISTS twitter_followers '
       '(user TEXT, date TEXT, followers INTEGER, followers_change INTEGER)')
c.execute(sql)
conn.commit()

# Retrieve the current date from the database
sql = "SELECT date('now')"
c.execute(sql)
sql_results = c.fetchall()
today = sql_results[0][0]

# Insert the new and changed follower counts into the database
for profile in result_list:
    screen_name = profile[u'screen_name']
    current_count = int(profile[u'followers_count'])

    # Retrieve the previous followers count (if one exists)
    sql = ("SELECT date, followers FROM twitter_followers WHERE user = '{0}' "
           'ORDER BY date DESC LIMIT 1'.format(screen_name))
    c.execute(sql)
    sql_results = c.fetchall()
    num_rows = len(sql_results)
    if num_rows > 0:
        previous_date = sql_results[0][0]
        previous_count = int(sql_results[0][1])
    else:
        previous_count = 0

    # Calculate the change in followers
    followers_change = current_count - previous_count

    # Insert the current number of followers into the database
    sql =('INSERT INTO twitter_followers '
          '(user, date, followers, followers_change) VALUES '
          "('{0}', date('now'), {1}, {2})").format(screen_name,
                                                   current_count,
                                                   followers_change)
    c.execute(sql)
    conn.commit()

    # Output the Twitter user and follower counts to stdout
    print '@{0}'.format(screen_name)
    if previous_count > 0:
        print '{0}: {1}'.format(previous_date, previous_count)
    if followers_change > 0:
        print '{0}: {1} (+{2})'.format(today,
                                       current_count,
                                       followers_change)
    elif followers_change < 0:
        print '{0}: {1} ({2})'.format(today,
                                      current_count,
                                      followers_change)
    else:
        print '{0}: {1}'.format(today, current_count)
    print

# Close the database connection
c.close()
