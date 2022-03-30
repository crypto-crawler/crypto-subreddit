import datetime
import json
import logging
import os
from typing import Dict, List, Optional, Union

logging.basicConfig(level=logging.WARN)

EPOCH_TIME = datetime.datetime(1970,1,1)

with open('../config.json', 'rt') as f:
  SUBREDDIT_LIST = json.loads(f.read())

def utc_day_to_rfc3339(utc_day: int) -> str:
  timestamp = EPOCH_TIME + datetime.timedelta(days=utc_day)
  return timestamp.isoformat() + "Z"

def read_last_line(file_path: str) -> Optional[str]:
  if not os.path.exists(file_path):
    logging.warning(f"{file_path} does not exist")
    return None
  with open(file_path, 'rt') as f:
    last_line = None
    for line in f:
      last_line = line
    return last_line

def get_historical_subscribers(name: str)->Optional[List[Dict[str, Union[int, str]]]]:
  file_path = f'{os.path.expanduser("~")}/github/soulmachine/subredditstats/data/{name}.json'
  last_line = read_last_line(file_path)
  if last_line is None: return None
  obj = json.loads(last_line)
  return [{"subscribers": x['count'], "timestamp": utc_day_to_rfc3339(x['utcDay'])} for x in obj['subscriberCountTimeSeries']]

def already_merged(name: str) -> bool:
  file_path = os.path.join("../data", name + ".json")
  if not os.path.exists(file_path): return False
  with open(file_path, 'rt') as f:
    first_line = json.loads(f.readline())
    return 'accounts_active' not in first_line

# Merge data from subredditstats
def merge(name: str)->None:
  if already_merged(name):
    logging.info(f"{name} already merged")
    return
  subscribers_history = get_historical_subscribers(name)
  if not subscribers_history: return

  file_path = os.path.join("../data", name + ".json")
  with open(file_path, 'rt') as f:
    first_line = json.loads(f.readline())
    first_timestamp: str = first_line['timestamp']

  subscribers_history = [x for x in subscribers_history if x['timestamp'][:10]<first_timestamp[:10]]

  # prepend to file
  with open(file_path, 'rt') as original: old_data = original.read()
  with open(file_path, 'wt') as modified:
    for x in subscribers_history:
      info = {
        "subreddit": name,
        "subscribers": x['subscribers'],
        "timestamp": x['timestamp'],
      }
      modified.write(json.dumps(info) + "\n")
    modified.write(old_data)

if __name__ == "__main__":
  for name in SUBREDDIT_LIST:
    logging.info(name)
    merge(name)
