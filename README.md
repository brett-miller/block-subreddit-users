Block Subreddit Users

* Create an app (https://www.reddit.com/prefs/apps)
* Create .env file with the following settings:

```
REDDIT_USERNAME=my_username
REDDIT_CLIENT_ID=axc0293adfc
REDDIT_CLIENT_SECRET=fafdsaMDAfas0321fsdazxc
REDDIT_PASSWORD=12345

# optional logging settings
COLOREDLOGS_AUTO_INSTALL=true
COLOREDLOGS_LOG_LEVEL=WARNING
```

Install / run with [pipenv](https://pipenv.readthedocs.io/en/latest/)

```
pipenv install

pipenv run blocker.py --help

# usage: blocker.py [-h] [-l BLOCK_LIST] [-s SUBBREDDIT]
# 
# Block users that post to one or more subreddits
# 
# optional arguments:
#   -h, --help            show this help message and exit
#   -l BLOCK_LIST, --block-list BLOCK_LIST
#   -s SUBBREDDIT, --subbreddit SUBBREDDIT

pipenv run blocker.py --subbreddit parkhorse

pipenv run blocker.py --block-list block-list-example.txt
```