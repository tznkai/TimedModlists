from dotenv import load_dotenv
from atproto import AtUri, Client, client_utils, models
import os
import time
import sched
import fileinput

#Load environmental variables at runtime.
load_dotenv()
MY_HANDLE=os.environ.get("BLUESKY_HANDLE")
MY_PW=os.environ.get("BLUESKY_PASSWORD")
fmt="%m-%d-%y %H:%M:%S"

class DeleteTask:
  def __init__(self, frequency:str,  due:str, name:str, uri:str):
    #determine frequency of task in seconds
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
    if due=="":
      self.due:float = None
    else:
      self.due:float = time.mktime(time.strptime(due,fmt))
  def duestamp(self):
      if self.due is None:
        return ""
      else:
        return time.strftime(fmt, time.localtime(self.due))
        

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
  update_config(schedule_tasks(scheduler,[task]))
  return True

def schedule_tasks(scheduler, tasklist):
  task:DeleteTask
  for idx, task in enumerate(tasklist):
    e:sched.Event = scheduler.enter(delay=task.seconds,priority=1,action=delete_list, kwargs={"scheduler":scheduler, "task":task})
    print("scheduled", task.name, "for", str(e.time), "local time: "+time.strftime("%m-%d-%y %H:%M:%S",time.localtime(e.time)))
    task.due = e.time 
    tasklist[idx]=task
  print("Epochtime is "+str(time.time()), "local time is", time.strftime("%m-%d-%y %H:%M:%S"), "the queue is now")
  print(scheduler.queue)
  return tasklist

def abs_schedule_task(scheduler:sched.scheduler, task:DeleteTask):
  e:sched.Event = scheduler.enterabs(time=task.due,priority=2,action=delete_list,kwargs={"scheduler":scheduler, "task":task})
  print("scheduled", task.name, "for", str(e.time), "local time: "+time.strftime("%m-%d-%y %H:%M:%S",time.localtime(e.time)))
  task.due = e.time
  print("Epochtime is "+str(time.time()), "local time is", time.strftime("%m-%d-%y %H:%M:%S"), "the queue is now")
  print(scheduler.queue)
  return task

def read_config():
  taskmode=False
  tasklist=[]
  #iterate through config file until task block is found
  print("Reading Config file")
  with open("config.txt", "rt") as text_file:
    for line in text_file:
      if line.strip()=="":
        pass
      elif taskmode:
        splitlist = line.split("\t")
        print("found task:", splitlist) 
        tasklist.append( DeleteTask(*splitlist))
      elif "FREQ\tNEXT\tNAME\tURI\n" == line:
        taskmode=True
  return tasklist

def eval_config(scheduler:sched.scheduler, tasklist:list):
  #if there are due time stamps, send to abs_schedule_task to schedule at due. Otherwise, schedule based on frequency
  task:DeleteTask
  scheduled_tasks=[]
  print("Finding already configured lists")
  modified_tasklist =[]
  for task in tasklist:
    print(task.name, str(task.due))
    if task.due:
      scheduled_tasks.append(abs_schedule_task(scheduler,task))
    else:
      modified_tasklist.append(task)
  #update config file with already scheduled tasks
  update_config(scheduled_tasks)
  #send remainder of non due tasks back for initial scheduling
  return modified_tasklist

def update_config(tasklist:list):
  task:DeleteTask
  print("updating config file")
  for task in tasklist:
    print("now working on",task.name,task.duestamp())
    with fileinput.input("config.txt", inplace=True) as f:
      for line in f:
        if task.uri in line:
          splitline = line.split("\t")
          splitline[1] = task.duestamp()
          modified_line= "\t".join(splitline)
          print(modified_line,end="")
        else:
          print(line,end="")
  print("config.txt is updated")
  return(tasklist)

def main():
    #some sort of check needed for restart condition - or build into advanced?   
    tasklist=read_config()
    print("starting scheduler")
    s = sched.scheduler(time.time, time.sleep)    
    tasklist=eval_config(s, tasklist)
    print("scheduling fresh lists")
    tasklist=update_config(schedule_tasks(s, tasklist))
    #schedule_tasks(s, tasklist)
    print("running queue. Leave this process open")
    s.run()
  


if __name__ == "__main__":
  main()
