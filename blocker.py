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
POST_LIMIT=int(os.getenv("POST_LIMIT"))

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     password=REDDIT_PASSWORD,
                     user_agent=NAME,
                     username=REDDIT_USERNAME)

class Blocker():
    def __init__(self):
        self.blocked_total = 0    

    def get_blocked_users(self):
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
    

    def get_subbreddit_authors(self, subreddit_name):
        authors = None
        try:
            subreddit = reddit.subreddit(subreddit_name)
            authors = set([submission.author.name for submission in subreddit.new(limit=POST_LIMIT) if submission.author ])
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

    def block_redditor(self, subreddit_name, redditor_name):
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
            self.blocked_total += 1
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

    def block_subreddits(self, subbreddits_to_block):
        for subreddit_name in subbreddits_to_block: 
            authors = self.get_subbreddit_authors(subreddit_name)
            if not authors:
                continue
            self.blocked_total = 0
            author_total = len(authors)
            print(f"Blocking {author_total} users from r/{subreddit_name}")
            for author in authors:
                self.block_redditor(subreddit_name, author)
            print(f"Blocked {self.blocked_total} users of {author_total} from r/{subreddit_name}")

def run(event, context):
    subbreddits_to_block = open("block-list.txt").read().splitlines()
    blocker = Blocker()
    blocker.block_subreddits(subbreddits_to_block)


if __name__ == "__main__":
    args = parser.parse_args() 
    subbreddits_to_block=[]
    if args.block_list:
        subbreddits_to_block.extend(args.block_list.read().splitlines())
    if args.subbreddit:
        subbreddits_to_block.append(args.subbreddit)
    blocker = Blocker()
    blocker.block_subreddits(subbreddits_to_block)
