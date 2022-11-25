import os
import io
from PIL import Image
import socket
import threading
import json
import sys
import time
from sql import *
import base64




def createServer():
	"""
	Creates a socket object and a database connection for the server. 
	"""
	global server 
	global db
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	db = Database()
	
	
def bindSocket():
	"""
	Binds the socket object of the server to the required IP address and PORT number
	"""
	global PORT
	try:
		global server
		server.bind((IP,PORT))
		
		server.listen()
	
	except:
		print("Server binding unsuccessful. Retrying ...")
		bindSocket()
	
	
def rec_query(conn):
	"""
	Listens for each client whatever message they have sent
	
	:param conn: connection from the server to the client
	:type conn: connection object
	:return: message received
	:rtype: python dictionary
	"""
	msg_len = conn.recv(64).decode('utf-8')
	#if(msg_len == ''):
	#	return create_dictionary(0,0,1,0,0,0,0,'DISCONNECT','', '0000', 0, 0)
	msg_len = '0b'+msg_len
	msg_len = int(msg_len, 2)
	msg = conn.recv(msg_len).decode('utf-8')
	#print(msg)
	msg = json.loads(msg)
	#print(msg)
	return msg
	
	
def send_text(rec, msg, my_conn = 0):
	"""
	Sends message to the client
	
	:param rec: username of the client to which message is to be sent
	:type rec: str
	:param msg: message
	:param msg: python dictionary
	"""
	#print(rec, msg)
	conn = 0
	global clients
	global db
	for key in clients:
		if key == rec:
			conn = clients[key][0]
			break
	
	try:
		if(msg['msg'] == '' or msg['msg']=='\n'):
			return
	except:
		pass
		
	if(conn==0):
		ans = db.check_username(rec)
		if not ans:
			return
		else:
			msg = json.dumps(msg)
			db.message_sent_to_user(rec, msg)
			return
	
	msg = json.dumps(msg)
	conn.send(f'{len(msg):064b}{msg}'.encode('utf-8'))
	
	
def send_image(rec, msg, conn_send):
	"""
	Receives and sends image from sender client to receiver client
	
	:param rec: username of the receiver client
	:type rec: str
	:param msg: the initial message to be sent before image is sent
	:type msg: str
	:param conn_send: connection object from the sender client to the server
	:type conn_send: connection object
	"""
	conn = 0
	global clients
	for key in clients:
		if key == rec:
			conn = clients[key][0]
			break
	
	if(conn==0):
		while True:
			image_chunk = conn_send.recv(image_size)
			if image_chunk == b"%IMAGE_COMPLETED%":
				break
		return
	
	send_text(rec, msg)
	
	while True:
		image_chunk = conn_send.recv(image_size)
		if image_chunk == b"%IMAGE_COMPLETED%":
			break
		conn.send(image_chunk)
			
	time.sleep(0.1)
	conn.send(b"%IMAGE_COMPLETED%")
		

def create_group(msg):
	"""
	Updates database when a new group is created
	
	:param msg: the message containing groupname, admin
	:type msg: python dictionary
	"""
	global db
	#correct
	db.create_group_database(msg['group_name'], msg['creator'])
	
	
def add_member(msg):
	"""
	Updates the database when a new user is added in a group
	
	:param msg: contains groupname, username of the added member
	:type msg: python dictionary
	"""
	global db
	isAd = db.isAdmin(msg['adder'], msg['group_name'])#correct
	if isAd==1:
		db.add_user_to_group(msg['member'], msg['group_name'])#correct
		send_text(msg['member'], msg)
	
	
def delete_member(msg):
	"""
	Updates the database when a member is deleted from the group
	
	:param msg:  contains groupname, username of the deleted member
	:type msg: python dictionary
	"""
	global db
	isAd = db.isAdmin(msg['deleter'], msg['group_name'])#correct	
	if isAd==1:
		db.delete_user_in_group(msg['member'], msg['group_name']) # correct
	
	
def leave_group(msg):
	"""
	Updates the database when a member leaves a group
	
	:param msg:  contains groupname, username of the member left
	:type msg: python dictionary
	"""
	global db
	db.delete_user_in_group(msg['leaver'], msg['group_name'])#correct


def disconnect(username, conn):
	"""
	Removes the connection of a client on his request for disconnection.
	
	:param username: username of the client who is disconnecting
	:param conn: connection object from the client to the server
	"""
	global number_of_clients
	global clients
	global db
	db.change_status(username, 0)
	number_of_clients -= 1
	msg = {}
	msg['purpose'] = 'disconnection'
	msg = json.dumps(msg)
	conn.send(f'{len(msg):064b}{msg}'.encode('utf-8'))
	clients = {x: clients[x] for x in clients if x != username}
	
	
def loginpage(msg):
	"""
	Authenticates a user on his login into the application
	
	:param msg: contains username and password of the client that he has entered
	:type msg: python dictionary
	:return: a bool object depending on whether the login is correct or not
	:rtype: bool
	"""
	global db
	x = db.authenticate(msg['username'], msg['password'])#correct
	
	if(x==1):
		return False# wrong
	elif(x==2):
		db.change_status(msg['username'], 1)
		return True # true
	

def signuppage(msg):
	"""
	Updates the database when a new user signsup in the application
	
	:param msg: contains the username and password of the new client
	:type msg: python dictionary
	:return: bool object depending on whether the username was unique or not
	:rtype: bool
	"""
	global db
	x = db.create_user(msg['username'], msg['password'])
	if(x==0):
		return True # sahi
	elif(x == 1):
		return False # wrong


def send_group_text(msg):
	"""
	Sends a broadcasting group message to all the members of a group except the user who sent that message
	
	:param msg: the message sent by the user
	:type msg: python dictionary
	"""
	#getstatus use
	global db
	
	if not db.check_groupname(msg['group_name']):
		q = {}
		q['purpose'] = 'invalid_user'
		send_text(msg['sender_id'], q)
		return
		
	if not db.check_user_in_group(msg['sender_id'], msg['group_name']):
		q = {}
		q['purpose'] = 'invalid_user'
		send_text(msg['sender_id'], q)
		return
	
	x = db.get_all_users(msg['group_name'])
	if x:
		for s in x:
			if(s[0] == msg['sender_id']):
				continue
			elif not db.get_status(s[0]):
				d = {}
				d['purpose'] = 'send_group_text_per'
				d['receiver'] = s[0]
				d['sender_id'] = msg['sender_id']
				d['group_name'] = msg['group_name']
				d['msg'] = msg['msg']
				send_text(s[0], d)
			else:	
				d = {}
				d['purpose'] = 'send_group_text_per'
				d['receiver'] = s[0]
				d['sender_id'] = msg['sender_id']
				d['group_name'] = msg['group_name']
				d['msg'] = msg['msg']
				send_text(s[0], d)
		#db.message_sent_to_group(msg['sender_id'], msg['group_name'], msg['msg'])


def send_key(msg, conn):
	"""
	Sends the public key of a client to another client who wants it for communication
	
	:param msg: the message sent by the client who wants the key
	:type msg: python dictionary
	:param conn: connection object from the requesting client to the server
	:type conn: connection object
	"""
	global db
	msg['key'] = 'x'
	#msgs = json.dumps(msg)
	#conn.send(f'{len(msgs):064b}{msgs}'.encode('utf-8'))
	#time.sleep(0.1)
	msg['key'] = db.get_key(msg['username'])
	msg = json.dumps(msg)
	conn.send(f'{len(msg):064b}{msg}'.encode('utf-8'))
	
	
def store_key(msg):
	"""
	Stores public key of a client in the database.
	
	:param msg: contains key
	:type msg: pytohn dictionary
	"""
	global db
	db.update_key(msg['username'], msg['key']) #correct


def send_group_image(msg, conn_send):
	"""
	Sends image to all the members of the group except the one who has sent it
	
	:param msg: contains information about the groupname, sender, image type etc
	:type msg: python dictionary
	:param conn_send: connection object from the sender client to the server
	:type conn_send: connection object
	"""
	conns =[]
	global db
	global clients
	
	if not db.check_groupname(msg['group_name']):
		while True:
			image_chunk = conn_send.recv(image_size)
			if image_chunk == b"%IMAGE_COMPLETED%":
				break
		q = {}
		q['purpose'] = 'invalid_user'
		send_text(msg['sender_id'], q)
		return
		
		
	if not db.check_user_in_group(msg['sender_id'], msg['group_name']):
		while True:
			image_chunk = conn_send.recv(image_size)
			if image_chunk == b"%IMAGE_COMPLETED%":
				break
		q = {}
		q['purpose'] = 'invalid_user'
		send_text(msg['sender_id'], q)
		return
		
	
	x = db.get_all_users(msg['group_name'])
	if x:
		for s in x:
			if(s[0] == msg['sender_id']):
				continue
			else:
				d = {}
				d['purpose'] = 'send_image'
				d['receiver'] = s[0]
				d['sender'] = f"{msg['sender_id']}({msg['group_name']})" 
				d['type'] = msg['type']
				
				conn = 0
				
				for key in clients:
					if key == s[0]:
						conn = clients[key][0]
						break
				
				if(conn==0):
					continue
					
				d = json.dumps(d)
				conn.send(f'{len(d):064b}{d}'.encode('utf-8'))
				
				conns.append(conn)
			
	while True:
		image_chunk = conn_send.recv(image_size)
		if image_chunk == b"%IMAGE_COMPLETED%":
			break
		else:
			for conn in conns:
				conn.send(image_chunk)
			
	time.sleep(0.1)
	for conn in conns:
		conn.send(b"%IMAGE_COMPLETED%")
				

def message_retrieval(msg, conn):
	"""
	Retrieves the messages that were sent to a client when he was offline and sends them on his login.
	
	:param msg: contains username of the client
	:type msg: python dictionary
	:param conn: connection object from the client to the server
	:type conn: connection object
	"""
	time.sleep(0.1)
	l = db.message_ret(msg['username'])
	for i in l:
		d = i[0]
		conn.send(f'{len(d):064b}{d}'.encode('utf-8'))
		time.sleep(0.1)
		

def talk(username, conn):
	"""
	The continuous loop that enables the server to listen from a client and take action accordingly.
	
	:param username: username of the client
	:type username: str
	:param conn: connection object from the client to the server
	:type conn: connection object
	"""
	global number_of_clients
	global clients
	while(True):
		message_log = rec_query(conn)
		if(message_log['purpose'] == 'send_group_text'):
			send_group_text(message_log)

		elif(message_log['purpose'] == 'disconnection'):
			disconnect(username, conn)
			break
			
		elif(message_log['purpose'] == 'send_text'):
			send_text(message_log['receiver'], message_log, conn)
			
		elif(message_log['purpose'] == 'send_image'):
			send_image(message_log['receiver'], message_log, conn)
			
		elif(message_log['purpose'] == 'group_creation'):
			create_group(message_log)
			
		elif(message_log['purpose'] == 'group_quitting'):
			leave_group(message_log)
			
		elif(message_log['purpose'] == 'add_member'):
			add_member(message_log)
			
		elif(message_log['purpose'] == 'del_member'):
			delete_member(message_log)
		elif(message_log['purpose'] == 'getkey'):
			send_key(message_log, conn)
		elif(message_log['purpose'] == 'public_key_exchange'):
			store_key(message_log)
		elif(message_log['purpose'] == 'send_group_image'):
			send_group_image(message_log, conn)
			time.sleep(0.1)
		elif(message_log['purpose'] == 'message_ret'):
			message_retrieval(message_log, conn)
			
		else:
			pass
	

def acceptClient():
	"""
	Accepts connection from the client
	"""
	global db
	global number_of_clients
	global key
	global clients
	while True:
		conn, addr = server.accept()
		msg = rec_query(conn)
		clients[msg['username']] = (conn,addr)
		number_of_clients += 1
		thread_client = threading.Thread(target = talk, args = (msg['username'],conn))
		thread_client.start()
		## username validation/ signup etc place
		'''
		success1 = 0
		success2 = 0
		if(msg['purpose'].lower() == 'login'):
			username = msg['username']
			success1 = loginpage(msg)
		elif(msg['purpose'].lower() == 'signup'):
			username = msg['username']
			success2 = signuppage(msg)
		
		if(success2):
			clients[username] = (conn,addr)
			number_of_clients += 1
			thread_client = threading.Thread(target = talk, args = (username,conn))
			d = {}
			d['purpose'] = 'authenticate'
			d['correct'] = True
			
			d = json.dumps(d)
			conn.send(f'{len(d):064b}{d}'.encode('utf-8'))
			
			thread_client.start()
		
		elif(success1):
			clients[username] = (conn,addr)
			number_of_clients += 1
			thread_client = threading.Thread(target = talk, args = (username,conn))
			d = {}
			d['purpose'] = 'authenticate'
			d['correct'] = True
			
			d = json.dumps(d)
			conn.send(f'{len(d):064b}{d}'.encode('utf-8'))
			time.sleep(0.1)
			
			l = db.message_ret(username)
			for i in l:
				d = i[0]
				conn.send(f'{len(d):064b}{d}'.encode('utf-8'))
				time.sleep(0.1)
				
			thread_client.start()
		
		else:
			d = {}
			d['purpose'] = 'authenticate'
			d['correct'] = False
			
			d = json.dumps(d)
			conn.send(f'{len(d):064b}{d}'.encode('utf-8'))
		'''

if __name__ == '__main__':

	IP = '127.0.0.1'
	number_of_clients = 0
	#key = 1000
	clients = {}
	db = 0
	image_size = 64
	PORT = int(sys.argv[1])
	createServer()
	bindSocket()
	acceptClient()
	server.close()

