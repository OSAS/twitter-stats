## Setup ##

1. Ensure you have Python's package manager "pip" installed.

2. Install the Python module dependencies using pip:

    $ pip install sqlite3
    $ pip install twitter

3. Create the directory for holding the database and config info

    $ mkdir -p ~/.twitter-stats/db

4. Copy and edit the config file

You'll need to update the Twitter authentication fields with
your own info. Info for creating them is on dev.twitter.com.

    $ cp config ~/.twitter-stats/
    $ vi ~/.twitter-stats/config

Setup complete.

You can either run the script adhoc, or set it to run in cron.

## Accessing the SQL data directly ##

If you want to access the SQL data directly, you can use either
the sqlite3 CLI, or use a GUI tool such as [SQLite Database
Browser] (http://sqlitebrowser.org).
