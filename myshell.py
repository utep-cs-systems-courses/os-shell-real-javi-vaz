#! /usr/bin/env python3

import os,sys,re

while 1:
    os.write(1,"$".encode())
    rawString = os.read(0,1024).decode().strip()
    usrInput = rawString.split()
    #Built In Commands
    if usrInput[0] == "exit":
        sys.exit(0)
    elif usrInput[0] == "cd":
        os.write(1,(os.getcwd()+"\n").encode())
        try:
            os.chdir(usrInput[1])
            os.write(1,(os.getcwd()+"\n").encode())
        except FileNotFoundError:
            os.write(2,"Invalid Path, please try again.\n".encode())
    #Runs a program 
    else:
        rc = os.fork()

        if rc < 0:
            os.write(2,("Fork failed when initializing command, Code %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0: #child
            args = usrInput
            if ">" in usrInput:
                index = usrInput.index(">")
                if (index + 1) >= len(usrInput):
                    os.write(2,"Invalid command\n".encode())
                    sys.exit(1)
                os.close(1)
                os.open(usrInput[index+1],os.O_CREAT | os.O_WRONLY)
                os.set_inheritable(1,True)
                args = usrInput[:index]
                
            elif "<" in usrInput:
                index = usrInput.index("<")
                if (index + 1) >= len(usrInput):
                    os.write(2,"Invalid command\n".encode())
                    sys.exit(1)
                os.close(0)
                
                try:
                    os.open(usrInput[index+1], os.O_RDONLY)
                except:
                    os.write(2,"Invalid command\n".encode())
                    
                os.set_inheritable(0,True)
                args = usrInput[:index]

            if usrInput[0][0] == "." or usrInput[0][0] == "/":
                try:
                    os.execve(usrInput[0],args,os.environ)
                except FileNotFoundError:
                    os.write(2,(usrInput[0]+": Command not found").encode())
                    sys.exit(1)
            else:
                for dir in re.split(":",os.environ['PATH']):
                    program = dir + "/" + usrInput[0]
                    try:
                        os.execve(program,args,os.environ)
                    except FileNotFoundError:
                        pass
                    os.write(2,(usrInput[0]+": Command not found\n").encode())
                    sys.exit(1)
        else: #Parent
            childPidCode = os.wait()
            #os.write(1,("Parent: Child %d terminated with exit code %d\n" % childPidCode).encode())
    
