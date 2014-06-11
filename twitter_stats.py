#!/usr/bin/env python
"""Get follower stats for our Twitter accounts & add them to a database"""

# Import the required Python modules
import os
import sys
import getopt
import getpass
import ConfigParser
import sqlite3
from twitter import *

def usage(error_string=None):
    prog_name = sys.argv[0]
    if error_string:
        print 'ERROR: {0}'.format(error_string)
        print
    print 'Usage:'
    print
    print '{0}'.format(prog_name)
    print '{0} [options]'.format(prog_name)
    print
    print '  -d | --dir <string>    Directory to write the output file in'
    print '  -f | --file            Outputs the results to file'
    print '  -h | --help            Display usage'
    print
    print 'To display the twitter stats on stdout, use:'
    print
    print '  {0}'.format(prog_name)
    print
    print 'To write the results to a file, use this:'
    print
    print '  {0} --file'.format(prog_name)
    print
    print 'The file will be named YYYY-MM-DD.txt in the current directory'
    print
    print 'To save the file in a different directory, use this:'
    print
    print '  {0} -f -d /path/to/some/other/dir/'.format(prog_name)
    print

# Check the command line
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:fh',
                               ['dir=', 'file', 'help'])

except getopt.GetoptError as err:
    # There was something wrong with the command line options
    usage(err)
    sys.exit(2)

# Parse any command line options and arguments
output_dir = None
output_file = None
for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-d", "--dir"):
        output_dir = a
    elif o in ("-f", "--cile"):
        output_file = True
    else:
        assert False, "Unknown command line option"

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

# If requested, write the followers report to a file
if output_file:
    if output_dir:
        file_path = os.path.join(output_dir, str(today) + '.txt')
    else:
        file_path = str(today) + '.txt'
    report_file = open(file_path, 'w+')

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

    # If requested, write the followers report to a file
    if output_file:
        report_file.write('@{0}\n'.format(screen_name))
        if previous_count > 0:
            report_file.write('{0}: {1}\n'.format(previous_date,
                                                previous_count))
        if followers_change > 0:
            report_file.write('{0}: {1} (+{2})\n'.format(today,
                                                       current_count,
                                                       followers_change))
        elif followers_change < 0:
            report_file.write('{0}: {1} ({2})\n'.format(today,
                                                      current_count,
                                                      followers_change))
        else:
            report_file.write('{0}: {1}\n'.format(today, current_count))
        report_file.write('\n')

    else:
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


# Close the output file if we're using one
if output_file:
    report_file.close()


# Close the database connection
c.close()
