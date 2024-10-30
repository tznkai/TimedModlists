def main():
  readmode=False
  tasklist=[]
  #iterate through config file until task block is found
  with open("config.txt", "rt") as text_file:
    for line in text_file:
      
      if readmode:
        splitlist = line.split("\t")
        print(splitlist)
        uri=splitlist[len(splitlist)-1]
        print(uri[len(uri)-1])
#        print(splitlist[0],splitlist[len(splitlist)-1])
 #       tasklist.append( DeleteTask(frequency=splitlist[0],uri=splitlist[len(splitlist)-1]) )
      if "FREQ\tNEXT\tNAME\tURI\n" == line:
        readmode=True
  

if __name__ == "__main__":
  main()

