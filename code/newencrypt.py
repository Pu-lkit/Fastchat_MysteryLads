import rsa
import base64

def generatekeys(username):
	(publicKey, privateKey) = rsa.newkeys(1024)
	with open('publickey.pem', 'wb') as f:
		f.write(publicKey.save_pkcs1('PEM'))
	with open(f'privatekey{username}.pem', 'wb') as f:
		f.write(privateKey.save_pkcs1('PEM'))
	with open('publickey.pem','rb') as f:
		publickeys = f.read()
	publickeystring = base64.b64encode(publickeys).decode()
	return publickeystring	# returns publickey as string to the database
    

def encrypt(msg,otherUserPublicKey): # takes msg to be encrypted as string type, key as string type from database
	keybytes = base64.b64decode(otherUserPublicKey)
	publickey =  rsa.PublicKey.load_pkcs1(keybytes)
	encryptbyte = rsa.encrypt(msg.encode(),publickey)
	encryptstring = base64.b64encode(encryptbyte).decode()
	return encryptstring # returns encrypted msg in string type

def decrypt(encryptedtext, username): # takes msg to be decrypted in string type
	with open(f'privatekey{username}.pem','rb') as f:
		privateKey = rsa.PrivateKey.load_pkcs1(f.read())
	encryptedbytes = base64.b64decode(encryptedtext)
	return rsa.decrypt(encryptedbytes,privateKey).decode() # returns decrypted msg in string type


#testing part
if __name__ == "__main__":
    publickey = generatekeys()
    msg = input("Type: ")
    encryptstring = encrypt(msg,publickey)
    decryptedstring = decrypt(encryptstring)
    print(decryptedstring)
