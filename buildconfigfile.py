from atproto import Client, client_utils, models
import os

from dotenv import load_dotenv
#Load environmental variables at runtime.
load_dotenv()

MY_HANDLE=os.environ.get("BLUESKY_HANDLE")
MY_PW=os.environ.get("BLUESKY_PASSWORD")
def buildconfig():
  client = Client()
  # By default, it uses the server of bsky.app. To change this behavior, pass the base api URL to constructor
  # Client('https://example.com')
  #
  # Login
  profile = client.login(MY_HANDLE,MY_PW)
  print("Logging in as", client.me.did)
  #iterate through user's own lists and extract modlists
  allmylists=my_lists(client)
  configtext="# Instructions: remove a line entirely if you don't want to schedule clearing. Otherwise change the FREQ to a number of Years, Months, Weeks, Days, Hours, xor Seconds .\nFREQ\tNEXT\tNAME\tURI"
  for sublist in allmylists:
    if sublist.purpose=="app.bsky.graph.defs#modlist":
      configtext = configtext + "\n"+"2Y\t\t"+sublist.name+"\t"+sublist.uri
  print("writing config file as:\r"+configtext)
  with open("config.txt", "w") as text_file:
    text_file.write(configtext)


def my_lists(client):
  cursor=None
  listoflists=[]
  while True:
    params = models.AppBskyGraphGetLists.Params(actor=client.me.did, cursor=cursor, limit=30)
    fetchedlists = client.app.bsky.graph.get_lists(params)   
    listoflists.extend(fetchedlists.lists)
    #if cursor returns empty, stop building list.
    if not fetchedlists.cursor:
      break
    #otherwise, update cursor and loop back
    print(fetchedlists.cursor)
    cursor=fetchedlists.cursor
  return listoflists

    
if __name__ == "__main__":
  buildconfig()
