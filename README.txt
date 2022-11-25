

## HOW TO RUN THE CODE '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


>> Run 
	$ python3 main_server.py 5050 2 1

>> Run two servers
	$ python3 server.py 5051
	$ python3 server.py 5052
	
>> Run clients on different terminals
	$ python3 client.py 3 5050 5051 5052
	
	
>> Follow the instructions displayed on the screen for sending messages, creating groups, etc.

*** the idea behind the commands behind running the servers is as follows

>> python3 main_server.py <PORT_MAIN_SERVER> <Number of additional servers> <algo flag which can be 1, 2, 3, 4>

>> python3 server.py <PORT_INDIVIDUAL_SERVER>
>>> python3 client.py <TOTAL_NUMBER_OF_SERVERS> <PORT_OF_MAIN_SERVER> <PORTS_OF_INDIVIDUAL_SERVERS>

	
>> Follow the instructions displayed on the screen for sending messages, creating groups, etc.

		'Welcome to Whatsapp2.0'
		'Signup: signup <username> <password>'
		'Login: login <username> <password>'
		'Send text message: send <receiver> <message>'
		'Send text message: sendgroup <receiver> <message>'
		'Send image: sendimage <receiver> <image>'
		'Send image: sendgroupimage <receiver> <image>'
		'Log out: logout'
		'Group Creation: creategroup <groupname>'
		'Add members in the group: addmember <groupname> <member>'
		'Delete members from the group: delmember <groupname> <member>'
		'Leave group: leavegroup <groupname>'
		'For exiting : exit'




## PACKAGES USED '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

>> hashlib (python library)
	This library is used for encrypting passwords one way
	
>> rsa (python library)
	Used for end to end encryption, generating public and private keys
	

>> psycopg2 (python library)
	Used for connecting with PostgreSQL database and running SQL commands


>> threading module from python

>> socket module from python

>> And some standard packages like io, os, etc





## WHAT WE HAVE IMPLEMENTED SO FAR ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

>> Single Server Multiple Clients functional program

>> Authentication of users using encrypted passwords (using hashlib.sha256)

>> End-to-End Encryption for transfer of text messages between users using 
rsa library in python

>> Transfer of images between users

>> End-to-End encryption of the images

>> User can recieve unrecieved messages when he was offline

>> Implemented groups with single admin and implemented some features such as
adding and removing users to groups, etc.

>> Multiple servers program with different load balancing strategies

>> Performance Analysis using bash and python script, and made a PDF showing all the results
	


## TEAM MEMBER'S CONTRIBUTION ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

>> Pulkit Goyal, 210050126: 
	Designed and Implemented the server and client side code for exchanging text and images,
	wrote systematic code for sending various types of messages, implemented multiple servers and load balancing strategy,
	Sphinx documentation
	
>> Nikhil Nandigama, 210050105:
	Researched and implemented the program for End-to-end encryption using rsa library and password 
	encryption using hashlib library, Perforamnce Analysis and Presentations
	
>> Priyanshu Yadav, 210050125:
	Implemented the database using PostgreSQL for storing relevant information and helped integrate it
	with server program, Performance Analysis and Readme file.
	
## PERFORMANCE ANALYSIS ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

--How we generated data

	1 >>>> First, run the three servers (2 + 1) using run_servers.py in a new terminal with required 
	files like client.py, server.py, main_server.py, newencrypt.py, groupencrypt.py, etc.
			$ python3 run_servers.py 1
	The command line argument is to signify the Load Balancing Strategy,
		RANDOM : 1
		ROUND ROBIN : 2
		also, SINGLE SERVER : 3
	
	 2 >> In a new terminal, run the client
		$ python3 client.py 3 5000 5001 5002 -l
	
	Then signup with a new user called u1 and password 0, 
		signup
		u1
		0
	3 >> In third terminal, run another client
		$ python3 client.py 3 5000 5001 5002 -l
	This time,
		signup
		u2
		0
		
	4 >> In fourth terminal, run the following command,
		python3 msgpat.py 3 5 0.0 exp ; python3 client.py 3 5050 5060 5070 -fl zz.txt ; python3 lt.py tsr.txt 3 5 0.0 exp
		
	This adds an entry in file called data.txt, also when running (4) for the first time, make sure to change the 
	line 70 of msgpat.py to --- f.write("signup\n") -----, after that one can run the command (4), without making any
	change to other terminals.
	

******************   All the inferences and observations from the data generated are shown in performance.pdf ***************** 
	

	















