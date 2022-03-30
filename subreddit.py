import gzip
import json
import logging
import os
from datetime import datetime
from typing import Dict, Union

import praw

USERAGENT = "crypto-subreddit:v0.1 by /u/s0ulmachine"

logging.basicConfig(level=logging.INFO)

# https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example
# create an app of script type at https://www.reddit.com/prefs/apps
reddit = praw.Reddit(
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    user_agent=USERAGENT,
)

with open("config.json", "rt") as f:
    SUBREDDIT_LIST = json.loads(f.read())


def get_subreddit_info(name: str) -> Dict[str, Union[str, int]]:
    try:
        # https://www.reddit.com/r/Bitcoin/about.json
        subreddit = reddit.subreddit(name)
        assert name == subreddit.display_name.lower()
        return {
            "subreddit": name,
            "subscribers": subreddit.subscribers,
            "accounts_active": subreddit.accounts_active,
            "timestamp": datetime.utcnow().isoformat() + "Z",  # RFC3339 format
        }
    except Exception as ex:
        logging.error(name)
        logging.error(ex)
        return {}


if __name__ == "__main__":
    for name in SUBREDDIT_LIST:
        logging.info(name)
        info = get_subreddit_info(name)
        if info:
            with gzip.open(os.path.join("./data", name + ".json.gz"), "at") as f_out:
                f_out.write(json.dumps(info) + "\n")
