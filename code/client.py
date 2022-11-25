import os
import io
from PIL import Image
import socket
import threading
import json
import sys
import time
import subprocess as sp
import hashlib
from newencrypt import *
from grpencrypt import *
from os.path import exists


def signup():
	"""
	Sends signup request to the main_server which checks whether the signup credentials are valid and if yes creates the user in the server's database
	
	:rtype: bool
	"""
	global index
	global myConn
	global signUp
	global username
	signUp = True
	myConn = True
	
	if not file_reading:
		username = input("Enter new username: ")
		password = input("Enter new password: ")
	else:
		username = file_lines[index]
		print(username)
		password = file_lines[index+1]
		print(password)
		index+=2
		
	global clients
	myConn = True  ## check
	clients.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
	clients[0].connect((IP,PORT[0]))
	#SHA 
	password = hashlib.sha256(password.encode()).hexdigest()
	
	msg = {}
	msg['purpose'] = 'signup'
	msg['username'] = username
	msg['password'] = password
	y = json.dumps(msg)
	clients[0].send(f'{len(y):064b}{y}'.encode('utf-8'))
	
	msg_len = clients[0].recv(64).decode('utf-8')
	msg_len = '0b'+msg_len
	msg_len = int(msg_len, 2)
	msg = clients[0].recv(msg_len).decode('utf-8')
	x = json.loads(msg)
	if(x['purpose'] == 'authenticate'):
		if(x['correct'] == True):
			time.sleep(0.1)
			msg = {}
			msg['purpose'] = 'public_key_exchange'
			msg['key'] = generatekeys(username)
			msg['username'] = username
			msg = json.dumps(msg)
			clients[0].send(f'{len(msg):064b}{msg}'.encode('utf-8'))
			return True
		else:
			return False
	

def loGin():
	"""
	Sends login request to the main_server which authorizes the client based on the given username and password.
	
	:rtype: bool
	"""
	global index
	global login
	global myConn
	global clients
	login = True
	myConn = True
	global username
	
	if not file_reading:
		username = input("Enter new username: ")
		password = input("Enter new password: ")
	else:
		username = file_lines[index]
		password = file_lines[index+1]
		index+=2
		
	myConn = True  ## check
	clients.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
	clients[0].connect((IP, PORT[0]))
	
	#SHA 
	password = hashlib.sha256(password.encode()).hexdigest()
	
	msg = {}
	msg['purpose'] = 'login'
	msg['username'] = username
	msg['password'] = password
		
	y = json.dumps(msg)
	clients[0].send(f'{len(y):064b}{y}'.encode('utf-8'))
	
	msg_len = clients[0].recv(64).decode('utf-8')
	msg_len = '0b'+msg_len
	msg_len = int(msg_len, 2)
	msg = clients[0].recv(msg_len).decode('utf-8')
	x = json.loads(msg)
	if(x['purpose'] == 'authenticate'):
		if(x['correct'] == True):
			return True
		else:
			return False

	
	
def send_text(msg, client=0):
	"""
	Sends a message to the server. The message functionalities vary according to the request the client has made. It first asks the main_server to allot some server out of the many given servers.
	
	:param msg: the message to be processed and sent
	:type msg: dictionary
	:param client: the server to which the message is to be sent. If it is 0, then main_server is asked to return a server to which message is to be sent
	:type client: connection object
	"""
	global clients
	
	#msg = recv_id + msg
	if client==0:
		client = getServer()
	
	if(msg['purpose'] == 'send_text'):
		if msg['receiver'] in public_keys:
			msg['key'] = public_keys[msg['receiver']]
		else:
			d = {}
			d['purpose'] = 'getkey'
			d['username'] = msg['receiver']
			d['key'] = ''
			d['requester'] = username
			send_text(d)
			public_keys[msg['receiver']] = 'p'
			time.sleep(0.1)
			#a = rec_text()
			#public_keys[msg['receiver']] = a['key']						
			msg['key'] = public_keys[msg['receiver']]
			
		my_key = msg['key']
		d = {}
		d['purpose'] = msg['purpose']
		d['receiver'] = msg['receiver']
		d['sender'] = msg['sender']
		d['msg'] = msg['msg']
		d['time_sent'] = msg['time_sent']
		msg1 = encrypt(msg['msg'], my_key)
		d['msg'] = msg1
		y = json.dumps(d)
	else:
		y = json.dumps(msg)
	client.send(f'{len(y):064b}{y}'.encode('utf-8'))


def rec_text(server_number):
	"""
	Receives the message from the servers in string format and converts it into python dictionary.
	
	:param server_number: the server from which message is to be received
	:type server_number: int
	:return: message 
	:rtype: python dictionary
	"""
	global clients
	client = clients[server_number]
	msg_len = client.recv(64).decode('utf-8')
	#if(msg_len == ''):
	#	global myConn
	#	myConn = False
	#	return msg_dict
	msg_len = '0b'+msg_len
	msg_len = int(msg_len, 2)
	msg = client.recv(msg_len).decode('utf-8')
	x = json.loads(msg)
	if(x['purpose'] == 'send_text'):
		new_msg = decrypt(x['msg'], x['receiver'])
		x['msg'] = new_msg
	if(x['purpose'] == 'send_group_text_per'):
		new_msg = group_decrypt(x['msg'], x['group_name'])
	return x
	
	
def send_image(msg, client):
	"""
	Sends image to a different client through intermediate server
	
	:param msg: image name
	:type msg: str
	:param client: connection to the server through which image is to be sent
	:type client: connection object
	"""
	with open(msg, "rb") as file:
		image_data = file.read(image_size)

		while image_data:
			client.send(image_data)
			image_data = file.read(image_size)
		time.sleep(0.1)
		client.send(b"%IMAGE_COMPLETED%")


def rec_image(file_type, server_number):
	"""
	Receives and saves the image sent from a client through a server. It saves the image in the currect working directory.
	
	:param file_type: The file type of the image which helps in correctly saving the image
	:type file_type: str
	:param server_number: the number representing which server to listen to for receiving the image
	:type server_number: int
	"""
	file_stream = io.BytesIO()
	image_chunk = clients[server_number].recv(image_size)
	while image_chunk:
		file_stream.write(image_chunk)
		image_chunk = clients[server_number].recv(image_size)
		if image_chunk==b"%IMAGE_COMPLETED%":
			break			
	image = Image.open(file_stream)
	c = file_type.lower()
	image.save(f'download.{c}', format=f'{file_type}')


def create_group(groupname, username):
	"""
	Sends group creation request to the server.
	
	:param groupname: name of the group
	:type groupname: str
	:param username: the username of the client who is creating the group
	:type username: str
	"""
	d = {}
	d['purpose'] = 'group_creation'
	d['group_name'] = groupname
	d['creator'] = username
	send_text(d)
	
	
def add_member(groupname, member, username):
	"""
	Sends add member request to the server.
	
	:param groupname: name of the group in which a new member is to be added
	:type groupname: str
	:param member: username of the new member to be added
	:type member: str
	:param username: the client who is sending the command for adding member(the admin of the group)
	:type username: str
	"""
	d = {}
	d['purpose'] = 'add_member'
	d['group_name'] = groupname
	d['member'] = member
	d['adder'] = username
	d['public_key'] = public_key_getting(groupname)
	
	if member in public_keys:
		b_key = public_keys[member]
	else:
		f = {}
		f['purpose'] = 'getkey'
		f['username'] = member
		f['key'] = ''
		f['requester'] = username
		send_text(f)
		time.sleep(0.1)
		#a = rec_text()
		#public_keys[member] = a['key']						
		b_key = public_keys[member]
	
	#print(d)
	d['private_key'] = private_key_getting(groupname)
	d['msg'] = 'p'
	#print(d)
	send_text(d)
	
	
def delete_member(groupname, member, username):
	"""
	Sends request to the server to remove a client from a group.
	
	:param groupname: name of the group from which the member is to be removed
	:type groupname: str
	:param member: username of the member to be removed
	:type member: str
	:param username: the client who is sending the command for deleting the member(the admin of the group)
	:type username: str
	"""
	d = {}
	d['purpose'] = 'del_member'
	d['group_name'] = groupname
	d['member'] = member
	d['deleter'] = username
	send_text(d)
	
	
def leave_group(groupname, username):
	"""
	Sends request to the server for leaving a group. 
	
	:param groupname: the groupname of the group the client wants to leave
	:type groupname: str
	:param username: the username of the client who wants to leave the group
	:type username: str
	"""
	d = {}
	d['purpose'] = 'group_quitting'
	d['group_name'] = groupname
	d['leaver'] = username
	send_text(d)


def disconnect():
	"""
	Sends logout request to the servers.
	"""
	global myConn
	global clients
	myConn = False
	msg = {}
	msg['purpose'] = 'disconnection'
	msg = json.dumps(msg)
	for c in clients:
		c.send(f'{len(msg):064b}{msg}'.encode('utf-8'))
	

def send_group_text(groupname, msg, username):
	"""
	Sends a groupmessage to be broadcasted in the group
	
	:param groupname: name of the group in which message is to be broadcasted
	:type groupname: str
	:param msg: the message to be broadcasted
	:type msg: str
	:param username: the sender
	:type username: str
	"""
	d = {}
	d['purpose'] = 'send_group_text'
	d['group_name'] = groupname
	d['sender_id'] = username
	d['msg'] = group_encrypt(msg, groupname)
	send_text(d, getServer())


def send_group_image(msg, client):
	"""
	Sends a group image to be sent to each member of the group.
	
	:param msg: image name
	:type msg: str
	:param client: the server connection to which the message is to be sent
	:type client: connection object
	"""
	with open(msg, "rb") as file:
		image_data = file.read(2048)

		while image_data:
			client.send(image_data)
			image_data = file.read(2048)
		time.sleep(0.1)
		client.send(b"%IMAGE_COMPLETED%")


def save_group_keys(msg):
	"""
	Saves the group keys that are used for encryption of messages of the group
	
	:param msg: contains the required keys fo storing
	:type msg: python dictionary
	"""
	public_key_storing(msg['group_name'], msg['public_key'])
	private_key_storing(msg['group_name'], msg['private_key'])


def getServer(msg_type = 'text'):
	"""
	Requests a server from the main_server to which the client can send command to.
	
	:return: connection object to the server
	:rtype: connection object
	"""
	global clients
	mains = clients[0]
	alpha = {}
	alpha['purpose'] = 'get_me_a_server'
	alpha['msg_type'] = msg_type
	alpha = json.dumps(alpha)
	mains.send(f'{len(alpha):064b}{alpha}'.encode('utf-8'))
	
	msg_len = mains.recv(64).decode('utf-8')
	msg_len = '0b'+msg_len
	msg_len = int(msg_len, 2)
	msgs = mains.recv(msg_len).decode('utf-8')
	x = json.loads(msgs)
	return clients[x['server']]


def talk():
	"""
	The main loop function which makes our application a continuous one which can send messages and receive messages anytime
	"""
	
	def command():
		global index
		global file_lines
		global file_reading
		global myConn
		global username
		while True and myConn:
			try:
				if(file_reading):
					timesl = float(file_lines[index])
					time.sleep(timesl)
					index+=1
					cmd = file_lines[index]
					index += 1
				else:
					cmd = input()
				cmd = cmd.split(maxsplit=1)
				
				if(cmd[0].lower() == 'send'):
					x = cmd[1].split(maxsplit = 1)
					msg = {}
					msg['purpose'] = 'send_text'
					msg['receiver'] = x[0]
					msg['sender'] = username
					msg['msg'] = x[1]
					msg['time_sent'] = round(time.time()*1000)
					send_text(msg)
				
				elif(cmd[0].lower() == 'sendimage'):
					x = cmd[1].split(maxsplit = 1)
					msg = {}
					msg['purpose'] = 'send_image'
					msg['receiver'] = x[0]
					msg['sender'] = username
					msg['msg'] = x[1]
					if not exists(x[1]):
						print(f'{x[1]} doesn\'t exist ')
						continue
					else:
						y = sp.getoutput(f'file -b {x[1]}')
						y = y.split(maxsplit = 1)
						msg['type'] = y[0]
						c = getServer('image')
						send_text(msg, c)
						send_image(msg['msg'], c)
					
				elif(cmd[0].lower() == 'creategroup'):
					x = cmd[1].rstrip()
					genkeys(x)
					create_group(x, username)
					
				elif(cmd[0].lower() == 'addmember'):
					x = cmd[1].split(maxsplit = 1)
					add_member(x[0], x[1], username)
					
				elif(cmd[0].lower()=='delmember'):
					x = cmd[1].split(maxsplit = 1)
					delete_member(x[0], x[1], username)
					
				elif(cmd[0].lower()=='leavegroup'):
					leave_group(cmd[1], username)
				
				elif(cmd[0].lower()=='sendgroup'):
					x = cmd[1].split(maxsplit = 1)
					send_group_text(x[0], x[1], username)
				
				elif(cmd[0].lower()=='sendgroupimage'):
					x = cmd[1].split(maxsplit = 1)
					msg = {}
					msg['purpose'] = 'send_group_image'
					msg['group_name'] = x[0]
					msg['sender_id'] = username
					msg['msg'] = x[1]
					if not exists(x[1]):
						print(f'{x[1]} doesn\'t exist ')
						continue
					else:
						y = sp.getoutput(f'file -b {x[1]}')
						y = y.split(maxsplit = 1)
						msg['type'] = y[0]
						c = getServer('image')
						send_text(msg, c)
						send_group_image(msg['msg'], c)
				
				elif(cmd[0].lower()=='logout' or cmd[0].lower()=='exit'):
					disconnect()
					break
				else:
					pass
				
			except:
				pass
			
	
	def rec(server_number):
		global myConn
		while True and myConn:
			x = rec_text(server_number)
			if not myConn:
				break
			
			if(x['purpose'] == 'send_text'):
				x['time_received'] = round(time.time()*1000)
				
				if log_writing:
				
					with open('logs', 'a') as file:
						file.write(f'{x["sender"]} {x["receiver"]} {x["time_sent"]} {x["time_received"]}')
						file.write('\n')
				print(x['sender'], '->', x['msg'])	
			
			elif(x['purpose'] == 'send_image'):
				print(f'Received an Image from {x["sender"]}')
				rec_image(x['type'], server_number)
			
			elif(x['purpose'] == 'getkey'):
				public_keys[x['username']] = x['key']
				
			elif(x['purpose'] == 'send_group_text_per'):
				t = group_decrypt(x['msg'], x['group_name'])
				print(f"{x['group_name']}({x['sender_id']}) -> {t}")
				
			elif(x['purpose'] == 'add_member'):
				save_group_keys(x)
			
		if not myConn:
			clients[server_number].close()
	
	thread_rec = []	
	thread_send = threading.Thread(target = command, args = ())
	
	for i in range(number_servers-1):
		thread_rec.append(threading.Thread(target = rec, args = (i+1,)))
	
	
	thread_send.start()
	
	for i in range(number_servers-1):
		thread_rec[i].start()
	
	for i in range(number_servers-1):
		thread_rec[i].join()
	thread_send.join()



if __name__ == '__main__':
	
	
	IP = '127.0.0.1'
	conn = 0
	login = False
	signUp = False
	username = ''
	myConn = False
	PORT = []
	clients = []
	file_lines = []
	file_reading = False
	log_writing = False
	index = 0
	number_servers = 0

	number_servers = int(sys.argv[1])
	for i in range(number_servers):
		PORT.append(int(sys.argv[2+i]))

	file_reading = False
	file_name = 0
	flag = number_servers + 2
	
	try:
		f = sys.argv[flag]
		if f == '-f':
			file_reading = True
			file_name = sys.argv[flag+1]
			with open(file_name, 'r') as g:
				for i in g:
					file_lines.append(i.rstrip())
					
		if f == '-fl':
			file_reading = True
			file_name = sys.argv[flag+1]
			with open(file_name, 'r') as g:
				for i in g:
					file_lines.append(i.rstrip())
					
		if f == '-l':
			log_writing = True
	except:
		file_reading = False
	
	image_size = 64

	public_keys = {}

	
	print('-------------------------------------------------------------------------------')
	print('Welcome to FASTCHAT')
	print('Signup: signup')
	print('Login: login')
	print('Send text message: send <receiver> <message>')
	print('Send text message: sendgroup <receiver> <message>')
	print('Send image: sendimage <receiver> <image>')
	print('Send image: sendgroupimage <receiver> <image>')
	print('Log out: logout')
	print('Group Creation: creategroup <groupname>')
	print('Add members in the group: addmember <groupname> <member>')
	print('Delete members from the group: delmember <groupname> <member>')
	print('Leave group: leavegroup <groupname>')
	print('For exiting : exit')
	print('-------------------------------------------------------------------------------')
	print()


	while(not login and not signUp):
		if file_reading:
			cmd = file_lines[index]
			index += 1
		else:
			cmd = input()
		cmd = cmd.split(maxsplit=1)
		
		
		### login
		if(cmd[0].lower()=='login'):
			c = loGin()
			if c:
				for i in range(number_servers-1):
					clients.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
					clients[i+1].connect((IP,PORT[i+1]))
					msg = {}
					#msg['purpose'] = 'login'
					msg['username'] = username
					#msg['password'] = password
			
					y = json.dumps(msg)
					clients[i+1].send(f'{len(y):064b}{y}'.encode('utf-8'))
				client = getServer()
				
				msg = {}
				msg['purpose'] = 'message_ret'
				msg['username'] = username
				msg = json.dumps(msg)
				client.send(f'{len(msg):064b}{msg}'.encode('utf-8'))
				
				talk()
				print('Successful logout')
				login = False
				signUp = False
				clients = []
				if file_reading:
					time.sleep(float(file_lines[index]))
					index+=1
				continue
			else:
				print('Invalid login')
				break
		
		
		### signup
		elif(cmd[0].lower() == 'signup'):
			c = signup()
			if c:
				for i in range(number_servers-1):
					clients.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
					clients[i+1].connect((IP,PORT[i+1]))
					msg = {}
					#msg['purpose'] = 'login'
					msg['username'] = username
					#msg['password'] = password
			
					y = json.dumps(msg)
					clients[i+1].send(f'{len(y):064b}{y}'.encode('utf-8'))
					
				talk()
				print('Successful logout')
				login = False
				signUp = False
				clients = []
				if file_reading:
					time.sleep(float(file_lines[index]))
					index+=1
				continue
			else:
				print('Username already exists')
				break
		
		
		### exit 	
		elif(cmd[0].lower()=='exit'):
			exit()
			
		### pass
		else:
			print('Incorrect choice')

