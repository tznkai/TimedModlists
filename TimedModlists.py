from dotenv import load_dotenv
from atproto import AtUri, Client, client_utils, models
import os
import time
import sched

#Load environmental variables at runtime.
load_dotenv()
MY_HANDLE=os.environ.get("BLUESKY_HANDLE")
MY_PW=os.environ.get("BLUESKY_PASSWORD")


class DeleteTask:
  def __init__(self, frequency:str,  date:str, name:str, uri:str):
    seconds:float
    if frequency.endswith("Y"):
      seconds=365*24*60*60
    elif frequency.endswith("M"):
      seconds=30*24*60*60
    elif frequency.endswith("W"):
      seconds=7*24*60*60
    elif frequency.endswith("D"):
      seconds=24*60*60
    elif frequency.endswith("H"):
      seconds=60*60
    elif frequency.endswith("S"):
      seconds=1
    else:
      raise ValueError("unexpected value, check your config.txt file")
    if frequency[0:-1].isnumeric():
      self.seconds = float(frequency[0:-1])*seconds
    else:
      raise ValueError("unexpected value, check your config.txt file")
    self.uri=uri.strip()
    self.frequency=frequency
    self.name=name

def delete_list(scheduler:sched.scheduler, task:DeleteTask):
  uri=task.uri
  client = Client()
  # By default, it uses the server of bsky.app. To change this behavior, pass the base api URL to constructor
  # Client('https://example.com')
  #
  # Login
  client.login(MY_HANDLE,MY_PW)
  print("logged in as: ", client.me.handle)
  cursor=None
  members=[]
  target_URIs=[]
  #get list and paginate
  while True:
    print("Fetching",task.name)
    params = models.AppBskyGraphGetList.Params(list=uri,cursor=cursor,limit=30)
    fetchedlist = client.app.bsky.graph.get_list(params)
    members.extend(fetchedlist.items)
    print("finding users to remove from the list:")
    for submember in members:
      print(submember.subject.handle) 
      target_URIs.append(submember.uri)
    #if cursor returns empty, stop building list.
    if not fetchedlist.cursor:
      break
    #otherwise, update cursor and loop back
    print("fetching more")
    cursor=fetchedlist.cursor
  #put uris into AtURI
  targets=[AtUri.from_str(uris) for uris in target_URIs]
  #iterate through targets and delate
  print("deleting....")
  obj:AtUri
  for obj in targets:
    print(obj.rkey)
    data = models.ComAtprotoRepoDeleteRecord.Data(collection=obj.collection, rkey=obj.rkey, repo=client.me.did)
    client.com.atproto.repo.delete_record(data)
  print("Done. Rescheduling task")
  schedule_tasks(scheduler,[task])
  return True

def schedule_tasks(scheduler, tasklist):
  task:DeleteTask
  for task in tasklist:
    scheduler.enter(delay=task.seconds,priority=0,action=delete_list, kwargs={"scheduler":scheduler, "task":task})
    print("scheduled "+task.name)
  print("it is now: "+str(time.time), "The queue is now")
  print(scheduler.queue)
  
  

def main():
  readmode=False
  tasklist=[]
  #iterate through config file until task block is found
  print("Reading Config file")
  with open("config.txt", "rt") as text_file:
    for line in text_file:
      
      if readmode:
        splitlist = line.split("\t")
        print("found task:", splitlist)
        tasklist.append( DeleteTask(*splitlist))
      if "FREQ\tNEXT\tNAME\tURI\n" == line:
        readmode=True
    print("starting scheduler")
    s = sched.scheduler(time.monotonic, time.sleep)
    schedule_tasks(s, tasklist)
    s.run()
  


if __name__ == "__main__":
  main()
