#!/usr/bin/env python2
"""
This application gets TV shows by connecting to transmission-rpc, determining
a list of appropriate media (by tracker and exclude dirs), downloading the 
files, and then moving them to a "done" directory.
"""

import config
import filelock
import transmissionrpc
import os
import re
import aamnotifs

def dl_and_move(torrent):
    file_list = []

    for x in torrent.files(): 
        file_list.append(t.files()[x]['name'])
    
    creds = config.rsync_creds

    for f in file_list:
        cmd = 'rsync -avpPr --password-file=$HOME/.config/mhazinsk/rsync-pass.txt rsync://{0}@{1}/{2}/"{3}" {4}'.format(creds['user'], creds['host'], creds['path'], f, config.local_dl_dir)
        status = os.system(cmd)
        
    if status == 0:
        t.move_data(config.done_dir)
        organize_shows(f)

    # TODO make a deferred for each thing in the file_list to move 

def organize_shows(filename):
    """
    Moves a locally-downloaded file to the correct directory.

    :params filename:       filename relative to config.local_dl_dir
    :type filename:         str or unicode
    """

    origpath = os.path.join(config.local_dl_dir, filename)

    for s in config.series:
        if filename.lower().startswith(s['prefix'].lower()):

            if not os.path.exists(s['dest']):
                os.makedirs(s['dest'])

            # Place it in the correct season folder
            if s['seasons']:
                pattern = re.compile(s['prefix'], re.IGNORECASE)
                epstr = pattern.sub("", filename).split('.')[1].lower()

                # Some sanity checking
                if len(epstr) == 6:
                    if (epstr[0] == 's') and (epstr[3] == 'e'):
                        try:
                            season = int(epstr[1:3])
                            seasondir = "Season {0}".format(season)

                            # now move origpath to dest/seasondir
                            newpath = os.path.join(s['dest'], seasondir)

                            if not os.path.exists(newpath):
                                os.makedirs(newpath)

                            print("moving {0} to {1}".format(origpath, newpath))
                            os.renames(origpath, os.path.join(newpath, filename))
                            notify_add(os.path.join(newpath, filename))
                            return

                        except ValueError:
                            pass

                # It didn't have an epstr after all! Move it anyways to the correct dir
                print("Warning: you selected seasons but this does not have an epstr!")
                os.renames(origpath, os.path.join(s['dest'], filename))
                notify_add(os.path.join(s['dest'], filename))

            else:
                os.renames(origpath, os.path.join(s['dest'], filename))
                notify_add(os.path.join(s['dest'], filename))



def notify_add(fpath):
    """
    Notifies a user via RabbitMQ about content that is available locally.

    This function is executed after each file is moved but only sends a 
    notification if aamnotifs_enable is set in the config.
    """

    if config.aamnotifs_enable:
        rmqc = config.rabbitmq_creds

        if rmqc['ssl']:
            n = aamnotifs.Notifs("amqps://{0}:{1}@{2}:{3}/%2F{4}".format(rmqc['user'], rmqc['pass'], rmqc['host'], rmqc['port'], rmqc['vhost']))

        else:
            n = aamnotifs.Notifs("amqp://{0}:{1}@{2}:{3}/%2F{4}".format(rmqc['user'], rmqc['pass'], rmqc['host'], rmqc['port'], rmqc['vhost']))

        print("notifying of: {0}".format(fpath))
        n.send(rmqc['queue'], fpath, "Downloaded {0}".format(fpath))

    

# Create mhazinsk config directory if it doesn't exist
configpath = os.path.expanduser("~/.config/mhazinsk")
if not os.path.exists(configpath):
    print("{0} not found, creating it.".format(configpath))
    os.makedirs(configpath)


lock = filelock.FileLock(config.lock_file)

try:
    with lock.acquire(timeout=10):
        # Connect
        tc = config.transmission_creds
        client = transmissionrpc.Client(tc['host'], port=tc['port'], user=tc['user'], password=tc['pass'])

        # Get a list of torrents
        torrents = client.get_torrents()

        # Filter to torrents in torrent_dir AND complete AND has one tracker in trackers
        dl_list = []

        for t in torrents:

            torrent_in_wl = True
            if t.status != "seeding":
                torrent_in_wl = False

            if t.downloadDir != config.torrent_dir:
                torrent_in_wl = False

            tracker_in_wl = False
            for tracker in t.trackers:
                if '/'.join(tracker['announce'].split('/')[0:3]) in config.trackers:
                    tracker_in_wl = True

            if tracker_in_wl == False:
                torrent_in_wl = False

            if torrent_in_wl:
               dl_list.append(t)


        # download locally and move to done_dir
        for t in dl_list:
            dl_and_move(t)


        # xbmc_clean or xbmc_update if needed

        if config.xbmc_update:
            print("Updating xbmc library not yet implemented.")
            # TODO

        if config.xbmc_clean:
            print("Cleaning xbmc library not yet implemented.")
            # TODO

        # TODO plex updating

except filelock.Timeout as err:
    print("Could not acquire the file lock. Is this program already running?")
    exit(1)

