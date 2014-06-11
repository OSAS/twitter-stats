## Setup ##

1. Ensure you have Python's package manager "pip" installed.

2. Install the Python module dependencies using pip:

        $ pip install sqlite3
        $ pip install twitter

3. Create the directory for holding the database and config info

        $ mkdir -p ~/.twitter-stats/db

4. Copy and edit the config file

        $ cp config ~/.twitter-stats/
        $ vi ~/.twitter-stats/config

The Twitter authentication info in the config file needs to be
updated with your own details.  Info for creating your own
developer account details are on https://dev.twitter.com.

Setup is now complete.

You can either run the script adhoc, or set it to run in cron.

## Accessing the SQL data directly ##

If you want to access the SQL data directly, you can use either
the sqlite3 CLI, or use a GUI tool such as [SQLite Database
Browser] (http://sqlitebrowser.org).
