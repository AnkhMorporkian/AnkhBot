from collections import deque
import urllib2

import simplejson as json
import arrow

from plugin import CommandPlugin
from user_manager import permissions, ADMIN


class SubmissionGrabber(CommandPlugin):
    """
    Implements a plugin that grabs new submissions from a specific reddit.com subreddit as specified intervals.
    If there are new submissions, it will pop them off in the order they were submitted.
    """
    name = "Submission Grabber"
    loop_name = "submission_grabber"

    def __init__(self):
        self.submission_deque = deque()
        self.seen_submissions = set()
        self.allowed_channels = []
        super(SubmissionGrabber, self).__init__()

    def activate(self):
        super(SubmissionGrabber, self).activate()
        self.allowed_channels.extend(self.config['allowed_channels'])
        self.timer = self.bot.add_timer(seconds=int(self.config['fetch_time']), function=self.new_submissions,
                                        name=self.loop_name)
        self.commands = {
            "queue_status": self.queue_status
        }

    def new_submissions(self):
        self.grab_new_submissions()
        try:
            if len(self.submission_deque):
                max_length = 410
                submission = self.submission_deque.popleft()
                title, author, created_utc, id = (str(x) for x in (
                    submission["title"],
                    submission["author"],
                    submission["created_utc"],
                    submission["id"]))
                submission_url = "http://redd.it/%s" % id
                relative_date = str(arrow.get(created_utc).humanize())
                partial_length = len(title) + len(author) + len(relative_date) + len(id) + 110

                if "selftext" in submission:
                    selftext = " ".join(submission["selftext"].split("\n"))
                    if (max_length - partial_length) > len(selftext):
                        selftext = ' "%s" ' % str(selftext)
                    else:
                        selftext = ' "%s..." ' % str(selftext[:max_length - partial_length - 5])
                    if selftext == ' "" ':
                        selftext = ' '
                else:
                    selftext = ' '
                for channel in self.allowed_channels:
                    self.bot.msg(channel,
                                 '"%s" by %s, posted about %s.%sLink: %s' % (
                                     title, author, relative_date, selftext, submission_url))
        except Exception as e:  # Broad handling here so as not to interrupt the loopingcall.
            print "Exception in submission_grabber loop. %s" % str(e)

    def grab_new_submissions(self):
        """
        Fetches the new submissions from the subreddit specific in the configuration file.
        """
        url_to_fetch = "http://www.reddit.com/r/%s/new/.json?limit=100" % self.config['subreddit']
        req = urllib2.Request(url_to_fetch,
                              headers={'User-Agent': self.config['user_agent']})
        data = urllib2.urlopen(req)
        json_data = json.load(data)
        results = [x["data"] for x in json_data["data"]["children"]]

        if len(self.seen_submissions) == 0:  # Fetching for the first time.
            for result in results:
                self.seen_submissions.add(result["id"])
        else:
            temporary_queue = []
            for result in results:
                if result["id"] in self.seen_submissions:
                    break
                temporary_queue.append(result)
                self.seen_submissions.add(result["id"])
            self.submission_deque.extend(reversed(temporary_queue))

    @permissions(ADMIN)
    def queue_status(self, user, channel, parameters):
        self.bot.msg(channel, "Queue status: %d submissions in the queue, %d submissions seen." % (
        len(self.submission_deque), len(self.seen_submissions)))

    def deactivate(self):
        print "Deactivate called."
        self.timer.stop()
        del self.timer

