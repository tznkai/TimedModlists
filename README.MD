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
7. If you want to set a modlist to expire for a certain date and time and then recur from there, run TimedModlists.py once to get the format, then break the proccess. Modify the dates (MM-DD-YY) and hours (HH:MM:SS) in config.txt using your local time. If you only want to clear it once set the reoccurance for 99Y or something.

# Use
1. Add people to your modlists through the bluesky interface.
2. Run TimedModlists.py and keep the process alive, such as through Systemd on linux systems. You can also deploy this whole thing via a service like Heroku. If you do that, you can remove the .env if you set the environmental variables with the service.
3. You need to restart the service if you change your config.txt Anything that was scheduled to clear in the past will clear and reschedule on start up.

# Important notes
The script is currently fragile and will fail if any of your configuration is done wrong.
**Y**ears and **M**onths are not actual calendar increments, but 365 days and 30 days respectively, with no adjustment for leap years.
On restart, no adjustments are made for DST and stored times are only accurate to the second.

# Features to come
- Error handling
- Duplication detection
- More elegant single use configuration
- localized time formats, DST handling, other improved date/time handling