import rsa
import base64

def genkeys(groupname):
	(pubKey, privKey) = rsa.newkeys(1024)
	with open(f'pubkey{groupname}.pem', 'wb') as f:
		f.write(pubKey.save_pkcs1('PEM'))
	with open(f'privkey{groupname}.pem', 'wb') as f:
		f.write(privKey.save_pkcs1('PEM'))
    
def public_key_getting(groupname):
	with open(f'pubkey{groupname}.pem','rb') as f:
		pubkeys = f.read()
	pubkeystring = base64.b64encode(pubkeys).decode()
	
	return pubkeystring # returns public key as a string to be stored by the group participant

def private_key_getting(groupname):
	with open(f'privkey{groupname}.pem','rb') as f:
		pubkeys = f.read()
	pubkeystring = base64.b64encode(pubkeys).decode()
	
	return pubkeystring 

def public_key_storing(groupname,publicstring):
	publicbytes = base64.b64decode(publicstring)
	pubkey =  rsa.PublicKey.load_pkcs1(publicbytes)
	with open(f'pubkey{groupname}.pem', 'wb') as f:
		f.write(pubkey.save_pkcs1('PEM'))
	
def private_key_storing(groupname,privatestring):
	privatebytes = base64.b64decode(privatestring)
	privkey =  rsa.PrivateKey.load_pkcs1(privatebytes)
	with open(f'privkey{groupname}.pem', 'wb') as f:
		f.write(privkey.save_pkcs1('PEM'))

def group_encrypt(msg,groupname): # takes msg to be encrypted as string type, key as string type from database
	with open(f'pubkey{groupname}.pem','rb') as f:
		grppubkey = rsa.PublicKey.load_pkcs1(f.read())
	encryptbyte = rsa.encrypt(msg.encode(),grppubkey)
	encryptstring = base64.b64encode(encryptbyte).decode()
	return encryptstring # returns encrypted msg in string type

def group_decrypt(encryptedmsg,groupname): # takes msg to be decrypted in string type
	with open(f'privkey{groupname}.pem','rb') as f:
		privKey = rsa.PrivateKey.load_pkcs1(f.read())
	encryptedbytes = base64.b64decode(encryptedmsg)
	return rsa.decrypt(encryptedbytes,privKey).decode() # returns decrypted msg in string type
