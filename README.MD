# What is TimedModlists
This a set of python scripts to enabled timed blocks/mutes by adding to modlists that are cleaned out.

# Setup
1. In Bluesky, go to Settings --> Moderation --> Moderation lists --? + New and create a new modlist for each time interval. If you want both mute and blocklists on the same interval, create them separately. Subscribe to your own lists.
2. Log into Bluesky, go to settings, then App Passwords. Generate an app password, copy it, bluesky will not show it to you again.
3. Download (clone) this whole repository onto your computer.
4. Create a new file called .env in the same directory as you downloaded the scripts. It needs two lines:
> BLUESKY_HANDLE=noat.your.handle
> BLUESKY_PASSWORD=whateveryourapppasswordis
5. Run buildconfigfile.py. A file called config.txt will be created with all your modlists.
6. Edit config.txt by removing any modlists you don't want to clear. Also change the frequency using a a number and a single letter code for time unit. **Y**ears **M**onths **D**ays **H**ours or **S**econds.

# Use
1. Add people to your modlists through the bluesky interface.
2. Run TimedModlists.py and keep the process alive. (You can also deploy this whole thing via a service like Heroku. If you do that, you can remove the .env if you set the environmental variables with the service.)

# Important notes
The script is currently fragile and will fail if any of your configuration is done wrong. It has no sense of the calendar, just "now" and "seconds from now" which is determined when the script is run. If the process running the script restarts the counter will reset at that point.

# Features to come
- Error handling
- Restart handling and absolute time references
- Duplication prevention