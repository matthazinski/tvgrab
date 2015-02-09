#!/usr/bin/env python2

################################################################################
# Derived from aamnotifs example file
# Simple example for receiving notifications.
################################################################################
import aamnotifs
import config
import os

def print_all_notifications(title, message):
    print "Notification received: {0}: {1}".format(title, message)

def notify_send(title, message):
    os.system("notify-send \"{0}\" \"{1}\"".format(title, message))


def print_mail_and_irc_notifications(title, message):
    print "Mail and IRC notifications received: {0}: {1}".format(title, message)

try:
    rmqc = config.rabbitmq_creds

    if rmqc['ssl']:
        n = aamnotifs.Notifs("amqps://{0}:{1}@{2}:{3}/%2F{4}".format(rmqc['user'], rmqc['pass'], rmqc['host'], rmqc['port'], rmqc['vhost']))

    else:
        n = aamnotifs.Notifs("amqp://{0}:{1}@{2}:{3}/%2F{4}".format(rmqc['user'], rmqc['pass'], rmqc['host'], rmqc['port'], rmqc['vhost']))


    # The routing_name is the name of the "channel" you want to use
    # it can be "mail", "chat", etc.
    # This will make it easy to choose which channels your clients
    # will receive. Can be a list too, for listening on multiple streams.
    n.receive("#", notify_send)  # "#" matches all channels


except KeyboardInterrupt:
    exit(1)
