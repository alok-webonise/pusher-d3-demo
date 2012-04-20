import json
import os
import sys
import signal
import time
from pprint import pprint
import threading

import tweepy
import tweepy_helpers

import pusher

count = 0
config = ""

class Sender(threading.Thread):
    def __init__(self, seconds):
        threading.Thread.__init__(self)
        print "Preparing to send data"
        self.kill_received = False 
        self.seconds = seconds
        self.p = pusher.Pusher()
        
    def run(self):
        while not self.kill_received:
            self.task()
    
    def task(self):
        global count
        try:
            print "Sending: " + str(count)
            self.p['my-channel'].trigger('my-event', {'count': count})
        except Exception,e:
            print e

        count = 0
        time.sleep(self.seconds)


def handle_data(data):
    global count
    count = count + 1

def main(args):
    global config
    try:
        config_path = os.path.dirname(sys.argv[0]) + "/config.json"
        print "Getting config from %s" % config_path
        config = json.loads(open(config_path, 'r').read())
        
        # prepare Pusher object
        pusher.app_id = config['pusher']['app_id'].encode('ascii')
        pusher.key = config['pusher']['key'].encode('ascii')
        pusher.secret = config['pusher']['secret'].encode('ascii')
        
        print "Firing up threads"
        threads = []
        s = Sender(1.0)
        threads.append(s)
        s.start()
        
        print "Recording filter %s..." % config['search_terms']
        tweepy_helpers.stream('filter', config, handle_data)
        while True: time.sleep(1)
        
    except (KeyboardInterrupt, SystemExit):
        print "Ctrl-c received! Sending kill to threads..."
        for t in threads:
            t.kill_received = True

if __name__ == '__main__':
  main(sys.argv)