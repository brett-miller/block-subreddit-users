import argparse
import logging
import os
import praw
import progressbar
import sys
import time

__version__ = "0.0.1"
NAME = 'block-subreddit-users'

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Block users that post to one or more subreddits')
parser.add_argument('--version', action='version', version=f"{NAME} v{__version__}")  
parser.add_argument('-l', '--block-list', type=argparse.FileType('r'))  
parser.add_argument('-s','--subbreddit', type=str)

REDDIT_USERNAME=os.getenv("REDDIT_USERNAME")
REDDIT_CLIENT_ID=os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET=os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_PASSWORD=os.getenv("REDDIT_PASSWORD")
POST_LIMIT=os.getenv("POST_LIMIT")

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     password=REDDIT_PASSWORD,
                     user_agent=NAME,
                     username=REDDIT_USERNAME)

blocked_total = 0

def get_blocked_users():
    """
    stopped working when the number of blocked users got too high =/
    """
    try:
        blocked_users = [user.name for user in reddit.user.blocked()]
        logger.info({
            "current_user": REDDIT_USERNAME,
            "step": "get_blocked_users", 
            "success": True, 
            "blocked_user_count": len(blocked_users)
            })
        print(f"{len(blocked_users)} users blocked")
        return blocked_users
    except Exception as e:
        logger.info({
            "current_user": REDDIT_USERNAME,
            "step": "get_blocked_users", 
            "success": False, 
            "error": "_".join(str(e).split()).upper()
        })
    

def get_subbreddit_authors(subreddit_name):
    authors = None
    try:
        subreddit = reddit.subreddit(subreddit_name)
        authors = set([submission.author.name for submission in subreddit.new(limit=1000) if submission.author ])
        print(f"Fetching authors from r/{subreddit_name}")
        logger.info({
            "current_user": REDDIT_USERNAME,
            "step": "get_subbreddit_authors", 
            "success": True, 
            "subreddit_name": subreddit_name
            })
    except Exception as e:
        logger.info({
            "current_user": REDDIT_USERNAME,
            "step": "get_subbreddit_authors", 
            "success": False, 
            "subreddit_name": subreddit_name
            })
    return authors

def block_redditor(subreddit_name, redditor_name):
    success = True
    try:
        reddit.redditor(redditor_name).block()
        logger.info({
            "current_user": REDDIT_USERNAME,
            "step": "block_user", 
            "success": success, 
            "user": redditor_name, 
            "subreddit": subreddit_name
            })
        blocked_total += 1
    except Exception as e:
        success = False
        logger.info({
            "current_user": REDDIT_USERNAME,
            "step": "block_user", 
            "success": success, 
            "user": redditor_name, 
            "subreddit": subreddit_name, 
            "error": "_".join(str(e).split()).upper()
            })

def run(event, context):
    subbreddits_to_block = open("block-list.txt").read().splitlines()
    for subreddit_name in subbreddits_to_block: 
        authors = get_subbreddit_authors(subreddit_name)
        if not authors:
            continue
        blocked_total = 0
        for author in authors:
            block_redditor(subreddit_name, author)
        author_total = len(authors)
        print(f"Blocked {blocked_total} of {author_total} users from {subreddit_name}")

if __name__ == "__main__":
    args = parser.parse_args() 
    subbreddits_to_block=[]
    if args.block_list:
        subbreddits_to_block.extend(args.block_list.read().splitlines())
    if args.subbreddit:
        subbreddits_to_block.append(args.subbreddit)
    for subreddit_name in subbreddits_to_block:
        authors = get_subbreddit_authors(subreddit_name)
        if not authors:
            continue
        for author in progressbar.progressbar(authors):
            block_redditor(subreddit_name, author)
