from praw import Reddit
from praw.reddit import Comment, Submission, Subreddit, RedditAPIException
from os import getenv
from dotenv import load_dotenv
from json import load
from time import sleep
import traceback

import openai 
 
load_dotenv()

config = load(open('config.json')) # Load config and convert it to dict.
api_url = "https://animekizi.org/download/%s/%s?utm_source=benanimekiziyim" # %1: Subreddit, %2: Post Id
openai.api_key = getenv('OPENAI_APIKEY')
template = \
"""
# [İndir!]({})
---
^(Bip bop! Ben video indirici asko bot!.)
"""
english_template = \
"""
# [Download!]({})
---
^(Bip bop! I am a anime girl bot!.)
"""

class Client:
    def __init__(self, client_id, username, password, client_secret) -> None:
        self.client = Reddit(
            client_id=client_id,
            username=username,
            password=password,
            client_secret=client_secret,
            user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
        )
        self.mention = ""
        self.start()

    
    def start(self):
        self.client.inbox.mark_all_read() # Mark read all objects in inbox.

        print("[INFO] Started as" , self.client.user.me())

        self.mention = 'u/%s' % (self.client.user.me())

    def check_mail_box(self) -> None:
        try:
            for i in self.client.inbox.unread(): # Get inbox
                if type(i) == Comment: # If inbox item is Comment
                    submission: Submission = i.submission
                    if submission.domain == 'v.redd.it': # If it is coming from an video
                        if i.body == self.mention:
                            i.reply(template.format(api_url) % (submission.subreddit, submission.id)) # Send a reply
                            print("[INFO] Sent link answer to", i.id)
                            i.mark_read()
                        elif self.mention not in i.body and i.author != "AutoModerator":
                            copy: str = i.body
                            msg: str = i.body
                            msg = msg.replace(self.mention, "")
                            msg = open("personality.txt").read().format(msg)

                            completion = openai.Completion.create(
                                engine="text-davinci-003",
                                prompt=msg,
                                max_tokens=400,
                                n=1,
                                stop=None,
                                temperature=0.5
                            )
                            answer = completion.choices[0].text.lower()
                            answer = answer.replace("?", '').replace("Cevap:", '').replace("{}:".format('u/benanimekiziyim'.capitalize()), '').replace(',', '').replace('!', '').replace('.', '').replace(':', '')\
                                .replace('answer', '').replace('"', '')\
                                    .replace('your response', '').replace(copy, '').replace(')', '')
                            
                            i.reply(answer)
                            i.mark_read()
                            print("[INFO] Sent AI answer to", i.id)
                        else: i.mark_read()
                    else:
                        i.mark_read()
                else:
                    pass
        except Exception as api_exception:
            print("--------------------")
            traceback.print_exc()
            print("--------------------")
            sleep(20) #Sleep 5 minutes to evade rate-limit

    def parse_ids(self) -> list[str]:
        return open('sent.txt').read().split()

    def append_id(self, id: str) -> None:
        open('sent.txt', 'a+').write(id+'\n')

    def check_subreddits(self) -> None:
        try:
            for submission in self.client.subreddit('+'.join(config["subreddits"])).new(limit=10): # Get submissions from subreddits that defined in config.json
                submission: Submission # Convert it to Submission object so intellisense detect it.
                if submission.domain == 'v.redd.it' and submission.id not in self.parse_ids():
                    submission.reply(template.format(api_url) % (submission.subreddit, submission.id))
                    self.append_id(submission.id)
                    print("[INFO] Sent link answer to", submission.id)
                else:
                    #print("[ERROR] Video already exists in sent.txt", submission.id)
                    continue
        except RedditAPIException as ratelimit:
            print("[ERROR] Reddit API Error")
            sleep(60*5) # Sleep 5 minutes to evade rate-limit
            pass
    
    def check_english_subreddits(self) -> None:
        try:
            for submission in self.client.subreddit('+'.join(config["english_subreddits"])).new(limit=10): # Get submissions from subreddits that defined in config.json
                submission: Submission # Convert it to Submission object so intellisense detect it.
                if submission.domain == 'v.redd.it' and submission.id not in self.parse_ids():
                    submission.reply(english_template.format(api_url) % (submission.subreddit, submission.id))
                    self.append_id(submission.id)
                    print("[INFO] Sent link answer to", submission.id)
                else:
                    #print("[ERROR] Video already exists in sent.txt", submission.id)
                    continue
        except RedditAPIException as ratelimit:
            print("[ERROR] Reddit API Error")
            sleep(60*5) # Sleep 5 minutes to evade rate-limit
            pass
    
    def loop(self):
        while True:
            self.check_mail_box() # Check Inbox
            self.check_subreddits() # Check Subreddit Submissions
            self.check_english_subreddits() # Check english subreddits
            sleep(5) # Sleep for block rate-limit and be cpu friendly.


def main():
    reddit_client = Client(
        client_id=getenv("APP_ID"),
        username=getenv("USERNAME"),
        password=getenv("PASSWORD"),
        client_secret=getenv("SECRET")
    )

    reddit_client.loop()



main()
