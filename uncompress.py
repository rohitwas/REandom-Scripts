import subprocess
import os

FNULL = open(os.devnull, 'w')
filename= raw_input("name of the file\n")

while (1):

	command = "file " + str(filename)
	file_ret =  subprocess.call(command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

	if not(file_ret == 0) :

  		print ("Failed to run file command. Invalid filename?")
  		exit();

	output = subprocess.check_output(command,shell=True)

	beg= output.find(filename+": ") + len(filename)+2
	end = (output[beg:]).find(" ")
	filetype = output[beg:beg+end]
	filetype = filetype.lower()
	print filetype

	if filetype == "gzip" :
		new_filename = filename +"."+"gz"
		command = filetype + " -d " + new_filename
		rename_command = "mv " + filename + " " + filename+"."+"gz"

	elif filetype == "lzma" :
		new_filename = filename +"."+"lzma"
		command = filetype + " -d " + new_filename
		rename_command = "mv " + filename + " " + filename+"."+"lzma"

	elif filetype == "bzip2" :
		new_filename = filename +"."+"bz2"
		command = filetype + " -d " + new_filename
		rename_command = "mv " + filename + " " + filename+"."+"bz2"

	elif filetype == "zip" :
		new_filename = filename +"."+"zip" 
		command = "un"+filetype+" -p " +new_filename +" > " + "test ; mv test "+filename
		rename_command = "mv " + filename + " " + filename+"."+"zip"

	elif filetype == "xz" :
		new_filename = filename +"."+"xz"
        	command = filetype+" -d " +new_filename
        	rename_command = "mv " + filename + " " + filename+"."+"xz"


	else :
		print "Unknown filetype?" 
		exit()
	print command
	print rename_command


	file_ret =  subprocess.call(rename_command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

	if file_ret == 0:
        	print "[*] Renamed %s archive"%(filetype)
	else :
        	print "Failed to rename %s archve ! Exiting..."%(filetype)


	file_ret =  subprocess.call(command, shell=True, stdout=FNULL, 	stderr=subprocess.STDOUT)

	if file_ret == 0:
		print "[*] Uncompressed a %s archive"%(filetype)
	else :
		rename_command = "mv " + new_filename + " " + filename
		file_ret =  subprocess.call(rename_command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
		if file_ret ==0:
			print "Failed to uncompress %s archve ! Renaming to orig filename and Exiting..."%(filetype)
		else:
			print "Failed to uncompress %s archive and Rename! please rename manually.."%(filetype)
