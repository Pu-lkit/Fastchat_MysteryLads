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
from random import random




def createServer():
	"""
	Creates a socket object and a database connection for the load balancing server. 
	"""
	global server 
	global db
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	db = Database()
	db.make_users_table()
	db.make_groups_table()
	
	
def bindSocket():
	"""
	Binds the socket object of the load balancing server to the required IP address and PORT number
	"""
	try:
		global server
		server.bind((IP,PORT))
		
		server.listen()
	
	except:
		print("Server binding unsuccessful. Retrying ...")
		bindSocket()


def return_a_server(msg_type, conn):
	"""
	Contains algorithms based on which a server is sent to the requesting client
	
	:param msg_type: what is the message type that needs to be sent
	:type msg_type: str
	:param conn: connection object from the load balancing server to the client
	:type conn: connection object
	:param algo: represents which algorithm is to be used for server selection
	:type algo: int
	"""
	global algorithm
	global round_robbin
	algo = algorithm
	x = {}
	x['purpose'] = 'take_server'
	if algo == 1:
		x['server'] = int(random()*float(number_servers))+1
	elif(algo == 2):
		x['server'] = (round_robbin+1)%number_servers + 1
		round_robbin += 1
	elif(algo==3):	
		x['server'] = 1
	elif(algo==4):
		if number_servers > 1:
			if msg_type == 'image':
				x['server'] = 1
			else:
				x['server'] = 2
			
	x = json.dumps(x)
	conn.send(f'{len(x):064b}{x}'.encode('utf-8'))

	
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
	msg = json.loads(msg)
	return msg

	
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
	#conn.send(f'{len(msg):064b}{msg}'.encode('utf-8'))
	clients = {x: clients[x] for x in clients if x != username}

	
def store_key(msg):
	"""
	Stores public key of a client in the database.
	
	:param msg: contains key
	:type msg: pytohn dictionary
	"""
	global db
	db.update_key(msg['username'], msg['key']) #correct


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
		if(message_log['purpose'] == 'disconnection'):
			disconnect(username, conn)
			break
		
		elif(message_log['purpose'] == 'get_me_a_server'):
			return_a_server(message_log['msg_type'], conn)
		
		elif(message_log['purpose'] == 'public_key_exchange'):
			store_key(message_log)
			
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
		## username validation/ signup etc place
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
			
			thread_client.start()
		
		else:
			d = {}
			d['purpose'] = 'authenticate'
			d['correct'] = False
			
			d = json.dumps(d)
			conn.send(f'{len(d):064b}{d}'.encode('utf-8'))
	

if __name__ == '__main__':
	IP = '127.0.0.1'
	PORT = int(sys.argv[1])
	number_of_clients = 0
	#key = 1000
	clients = {}
	db = 0
	round_robbin = 1
	number_servers = int(sys.argv[2])
	algorithm = int(sys.argv[3])
	#image_size = 64
	createServer()
	bindSocket()
	acceptClient()
	server.close()

