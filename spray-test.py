import os
import subprocess
import time
import re
import sys
import traceback

#CHANGE BELOW
PY_PATH = "c:\\Python27\\python.exe"
TARGET_PATH = "C:\\Program Files (x86)\\Internet Explorer\\iexplore.exe"
TARGET_PROGRAM = "iexplore.exe"
DBG_PATH = "\"\"C:\\Program Files (x86)\\Windows Kits\\10\\Debuggers\\x86\\cdb.exe\""
#DBG_PATH = "windbgX"
poc_file = "http://127.0.0.1:8000//poc2.html"
MAGIC_BYTES = "25252424"
FREED_PTR_REG = "ebx"
SEARCH_SPACE = "1000" #how many bytes(in hex) to search from the start of FREED_PTR_REG

#CONFIG
DETACHED_PROCESS = 0x00000008
CREATE_SUSPENDED = 0x00000004
NUMBER_OF_TRIES = 20

def keep_trying():
	freed_ptr = 0
	fake_object = 0
	try :
		#start a webserver in the current directory (* this is for browser targets only)
		test = subprocess.Popen([PY_PATH, "-m" , "SimpleHTTPServer"],shell =False, stdin=None,stdout=None,stderr=None,close_fds=True,creationflags=DETACHED_PROCESS)
		#open target path with poc file 
		subprocess.Popen([TARGET_PATH, poc_file ], shell=False,stdin=None,stdout=None,stderr=None,close_fds=True,creationflags=DETACHED_PROCESS)

		#  subprocess pid doesnt work , gives u pid of the shell/cmd. 
		# no clean way to get pid of iexplore.exe :(  relying on tasklist command for now

		time.sleep(1)
		result = os.popen("tasklist /FI \"IMAGENAME eq %s\" /FI \"STATUS eq running\" /FO LIST"%(TARGET_PROGRAM)).read()
		result = result.split("\n")

		pid = [int(s) for s in (result[8]).split() if s.isdigit()]
		print "[*] Attaching to PID : %s"%pid[0]

		#attach to IE process, get freed pointer, search sprayed fake objects, log , detach , close
		os.popen("%s -p %s -c \" .childdbg 1 ;g; .logopen log_abc ; r;r %s;s -d %s L?%s %s; .logclose ; qq \" "%(DBG_PATH , pid[0], FREED_PTR_REG,FREED_PTR_REG,SEARCH_SPACE, MAGIC_BYTES ))
		#os.system("%s -p %s -c \" .childdbg 1 ;g; .logopen log_abc ; r;r %s;s -d %s L?%s %s; .logclose ; qq \" "%(DBG_PATH , pid[0], FREED_PTR_REG,FREED_PTR_REG,SEARCH_SPACE, MAGIC_BYTES ))
		#print "[*] Success"

		#parse log file for freed + fake objects
		f = open("log_abc","r")
		for each_line in f:
			x = re.search("^%s.*$"%(FREED_PTR_REG),each_line) #starts with FREED_PTR_REG, end with a newline
			if not (x== None) : 
				y = re.search("\ ", x.string) # doesnt contain any whitespace/ignore the register dump
				if y == None:
					freed_ptr = x.string.replace("%s="%FREED_PTR_REG, "")
					freed_ptr = int(freed_ptr,16)
					print "[*] Freed pointer value is %s"%(hex(freed_ptr))
					next_line = f.next() # next line
					if "Closing open log file" in next_line:
						print "[*] Couldnt find Fake Object within %s bytes"%(SEARCH_SPACE)
					else :
						next_line = next_line.split("  ")
						fake_object = int(next_line[0],16)
						print "[*] Fake object at %s"%(hex(fake_object))
						print "[*] Fake Object allocation is %d bytes away from freed ptr"%(fake_object - freed_ptr)
					break

	except:
	    print(traceback.format_exc())


	finally: 
		try:
			f.close()
		except:
			pass	

		#cleanup. Kill Target program and python shell
		os.popen("taskkill /IM %s /F"%(TARGET_PROGRAM))
		#os.system("taskkill /IM python.exe /F")

		return_vals = [freed_ptr,fake_object]
		return return_vals
perfect_hit = 0
hits = 0
miss = 0 
mean_variance = 0
for i in range(0,NUMBER_OF_TRIES):
	print "----- BEGIN #%d -----"%(i+1)
	vals = keep_trying()
	if vals[0] ==0:
		print "[*] Couldnt find the freed pointer?? This shouldnt happen. exiting!"
		continue
		#os.popen("taskkill /IM python.exe /F")
	else:
		if vals[1] ==0:
			miss  =  miss+ 1	
		else :
			if vals[1]-vals[0] ==0:
				perfect_hit = perfect_hit +1 # fake object spray succeded!!
				hits = hits +1
			hits = hits + 1
			mean_variance  = mean_variance + vals[1] - vals[0]
	print "----- END #%d -----\n"%(i+1)
print "\n[*] Perfect Hits = %d , Regular Hits = %d , Miss = %d "%(perfect_hit, hits, miss)
if (hits ==0):
	print "[*] In %d tries, there wasn't a single time the spray worked."%(NUMBER_OF_TRIES)
else:
	print "[*] In %d tries, the mean variance in the distance between the fake_object and freed_ptr was %d bytes"%(NUMBER_OF_TRIES, mean_variance/hits)

os.popen("taskkill /IM python.exe /F")
