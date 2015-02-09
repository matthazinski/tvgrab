## Description
This is a script to connect to Transmission via the RPC API and do the 
following:
- Filter torrents based on tracker and directory
- Rsync files to a local machine
- Sort files (locally) to the correct directory
- Move torrent data files (remotely) to a "done" directory
- Notify on completion via aamnotifs
- (planned) update XBMC and Plex libraries


## Usage
It is assumed that the user has several servers. Many of these services can be 
run on the same machine.
- A seedbox running transmission and the rsync daemon
- A storage server running tvgrab
- A RabbitMQ exchange (optional)
- A workstation to receive notifications (optional)
- XBMC and/or Plex clients (optional)

Installation of most of these components is left as an exercise for the reader.

On the machine running this script, do "pip install -r requirements.txt".
Copy config.py.example to config.py, modify it with your credentials and then
run tvgrab,py as a cronjob.

On your workstation, install dunst and then run aamnotifd.py in the background.
Eventually this will be properly daemonized.
