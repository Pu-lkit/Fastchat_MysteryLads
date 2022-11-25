import psycopg2
import hashlib
import time
from psycopg2 import Error


# IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII

class Database:

    def __init__(self):

        
        self.connection = psycopg2.connect(user="postgres",
                                      password="1234",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="postgres")

        self.cursor = self.connection.cursor()
        self.connection.commit()
     
        
                            
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def make_users_table(self):
        """
        It creates the table Users in the database if it wasn't there. If it was already present, it drops that and creates a new Users table in the database.
        """
        # CREATING Users TABLE''''''''''''''''''''''
        self.cursor.execute("DROP TABLE IF EXISTS Users;")
        
        create_table_query = """ CREATE TABLE Users(
                                username TEXT,
                                password TEXT,
                                isOnline INT,
                                publicKey TEXT,
                                PRIMARY KEY (username)
                                ) """
    
                                
        self.cursor.execute(create_table_query)
        self.connection.commit()
        return 1
        
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        
    def make_groups_table(self):
        """
        It creates the table Groups in the database if it wasn't there. If it was already present, it drops that and creates a new Groups table in the database.
        """
        # CREATING Groups TABLE''''''''''''''''''''
        self.cursor.execute("DROP TABLE IF EXISTS  Groups;")
        self.cursor.execute(""" CREATE TABLE Groups(
                            groupname TEXT PRIMARY KEY,
                            publicKey TEXT
                            )""")
        self.connection.commit()
        return 1
        
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def create_user(self, username, password, publicKey=''):
        """
        Checks whether the given username is present in the Users table or not. If it is not present then it adds that user to the database, otherwise it doesn;t update the database.
        
        :param username: Username of the client to be added
        :type username: str
        :param password: encrypted for of the password of the user
        :type password: str
        :param publicKey: publicKey of the user for E2E encryption
        :type publicKey: str
        """
        
        if not self.check_username(username):
        
            # ADDING TO Users
            add_user_query = f"INSERT INTO Users VALUES ('{username}', '{password}', 1, '{publicKey}')"
            self.cursor.execute(add_user_query)
            
            print("User Successfully created")
            
            # CREATING table<username>'''''''''''''''''''''
            self.cursor.execute(f"DROP TABLE  IF EXISTS table{username};")
            create_user_table_query = f"""CREATE TABLE table{username}(
                                            otherusername TEXT,
                                            message TEXT
                                            )"""
            self.cursor.execute(create_user_table_query)
            self.connection.commit()
            return 0
        else :
            print("Username already exists, please change")
            return 1
        
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''     
    
    def check_username(self, username):
        """
        Checks whether the username given exists in the database or not.
        
        :param username: username whose existence in the databse is to be checked
        :type username: str
        :return: bool object representing whether it exists or not
        :rtype: bool
        """
        self.cursor.execute(f"""SELECT * from Users WHERE username = '{username}'""")
        if len(self.cursor.fetchall()) == 0:
            # Other User does not exist
            print("User does not exist")
            self.connection.commit()
            return False
        else:
            return True
        
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' 
    
    def check_groupname(self, groupname):
        """
        Checks whether the there exists a group with its name given exists in the databse or not.
        
        :param groupname: groupname whose existence in the databse is to be checked
        :type groupname: str
        :return: bool object representing whether it exists or not
        :rtype: bool
        """
        self.cursor.execute(f"""SELECT * from Groups WHERE groupname = '{groupname}'""")
        if len(self.cursor.fetchall()) == 0:
            # Other User does not exist
            print("Group does not exist")
            self.connection.commit()
            return False
        else:
            return True
            
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' 
    
    def check_user_in_group(self, username, groupname):
        """
        Check whether a user with name given as username is present in the group whose name is groupname.
        
        :param username: username whose existence in the group database is to be checked
        :type username: str
        :param groupname: groupname of the group in which existence is to be checked
        :type groupname: str
        :return: bool object representing whether it exists or not
        :rtype: bool
        """
        
        self.cursor.execute(f"""SELECT (username) FROM groupusers{groupname} WHERE username = '{username}'""")
        if len(self.cursor.fetchall()) == 0:
            print("User not present in the group")
            self.connection.commit()
            return False;
        else :
            return True;
    
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' 
    
    def authenticate(self, username, password):
        """
        Authenticates the user with name given as username and password given as password. Used in login purposes.
        
        :param username: username of the user whose authentication is to be done
        :type username: str
        :param password: password given by the user
        :type password: str
        :return: 1 on incorrect credentials and 2 on successful authentication
        :rtype: int
        """
        
        self.cursor.execute(f"""SELECT * FROM Users WHERE username = '{username}' AND password = '{password}';""")
        if len(self.cursor.fetchall()) == 0:
            print("Incorrect Username or Password")
            return 1
        else:
        
            # UPDATE ONLINE STATUS OF <currentuser>''''''''''''''''''''
            self.cursor.execute(f"""UPDATE Users
                               SET isOnline = 1
                               WHERE username = '{username}' 
                               AND password = '{password}';
                               """)
            print("Successfully Authenticated")
            self.connection.commit()
            return 2
            
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            
    def change_status(self, username, isOnline):
        """
        Updates the isOnline value of a user in the database which tells whether a user is Online or Offline
        
        :param username: username of the user
        :type username: str
        :param isOnline: 1 if online and 0 if offline
        :type isOnline: int
        """
        if self.check_username(username):
            # UPDATE ONLINE STATUS OF currentuser'''''''''''
            self.cursor.execute(f"""UPDATE Users
                               SET isOnline = {isOnline}
                               WHERE username = '{username}'
                               """)
                               
            print("Successfully Status Changed")
            self.connection.commit()
            return 1
        else :
            return 0
            
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def get_status(self, username):
        """
        Returns the curent status of the user stating whether the user is online or offline
        
        :param username: username of the user
        :type username: str
        :return: isOnline (1 if online and 0 if offline)
        :rtype: int
        """
        if not self.check_username(username):
            return -1
        
        self.cursor.execute(f"""SELECT (isOnline) FROM Users WHERE username = '{username}'""")
        isOnline = self.cursor.fetchall()[0][0];
        self.connection.commit()
        return isOnline
            
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def message_sent_to_user(self, username2, message):
        """
        Saves the message of the sent by a client to user with username as username2 and hence helps in message retrieval when the user switches back to online from offline
        
        :param username2: username of the user
        :type username2: str
        :param message: message to be stored
        :type message: str
        """
        if not self.check_username(username2):
            return 0
       
        if self.get_status(username2) == 0:
            self.cursor.execute(f"""INSERT INTO table{username2}
                            VALUES ('', '{message}')""")
                            
        
        self.connection.commit()
        return 1
   
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        
    def message_ret(self, username):
        """
        Gives a list of messages stored in a user's database for transmission of messages by the server to clients who missed these messages and switched back to online from offline
        
        :param username: username of the user
        :type username: str
        :returns: list of messages
        :rtype: list
        """
        
        if not self.check_username(username): 
            return 0
            
        
        self.cursor.execute(f"SELECT (message) FROM table{username}") 
        ll = self.cursor.fetchall()
        self.cursor.execute(f"DELETE FROM table{username}")            
        print("Messages successfully retrieved")
        self.connection.commit()
        return ll
        
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        
    def create_group_database(self, groupname, adminuser, publickey=''):
        """
        Updates the database and adds a new table for the group with name as groupname.
        Also adds the adminuser to the group's table and adds the publicKey of the group
        
        :param groupname: groupname of the group
        :type groupname: str 
        :param adminuser: username of the admin
        :type adminuser: str
        :param publickey: publickey of the group
        :type publickey: str
        """
    
        if self.check_groupname(groupname):
            print("Use another group name, this name already used")
            return 0
    
        # ADDING <groupname> TO Groups TABLE
        self.cursor.execute(f"INSERT INTO Groups VALUES ('{groupname}', '{publickey}')")
        
        # CREATING groupusers<groupname> TABLE
        self.cursor.execute(f"DROP TABLE  IF EXISTS groupusers{groupname}")
        self.cursor.execute(f""" CREATE TABLE groupusers{groupname} (
                            username TEXT,
                            isAdmin INT,
                            PRIMARY KEY (username)
                            )""")
             
        # ADDING <currentuser> TO THE groupusers<groupname> TABLE
        self.cursor.execute(f"""INSERT INTO groupusers{groupname} VALUES ('{adminuser}', 1)""")
        self.connection.commit()
        
        print("Group successfully created")
        
        return 2;
                            
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def get_all_users(self, groupname):
        """
        Returns a list of users in the group with name as groupname.
        
        :param groupname: name of the group
        :type groupname: str
        :return: list of usernames present in the group
        :rtype: list
        """
        if not self.check_groupname(groupname):
            return 0
            
        self.cursor.execute(f"""SELECT (username) FROM groupusers{groupname}""")
        print("Users list retrieved")
        self.connection.commit()
        return self.cursor.fetchall()
        
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def message_sent_to_group(self, username, groupname, message):
        """
        Stores the messages sent to the group.
        
        :param username: username of the user
        :type username: str
        :param groupname: name of the group
        :type groupname: str
        :param message: message to be stored
        :type message: str
        """
        
        if not self.check_username(username) or not self.check_groupname(groupname) or not self.check_user_in_group(username, groupname):
            return 0;
        
        group_users_list = self.get_all_users(groupname)
        for t in group_users_list:
            print("Hey t[0] is ", t[0])
            if username != t[0] and not self.get_status(t[0]):
                print("t[0] is ", t[0])
                self.cursor.execute(f"""INSERT INTO table{t[0]} VALUES ('{groupname}:{t[0]}', '{message}')""")
                
        self.connection.commit()
                                
        return 3;
       
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def isAdmin(self, username, groupname):
        """
        Checks whether the user with name as username is the admin of the group with name as groupname.
        
        :param username: username of the user
        :type username: str
        :param groupname: name of the group
        :type groupname: str
        :return: 0 if it is not an Admin else 1
        :rtype: int
        """
    
        if not self.check_username(username) or not self.check_groupname(groupname) or not self.check_user_in_group(username, groupname):
            return 0;
       
        self.cursor.execute(f"""SELECT (isAdmin) FROM groupusers{groupname} WHERE username = '{username}'""")
        self.connection.commit()
        return self.cursor.fetchall()[0][0]
            
        
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''       
    
    def add_user_to_group(self, username, groupname, isAdmin=0):
        """
        Adds the user with name as username to the group whose name is groupname.
        
        :param username: username of the user
        :type username: str
        :param groupname: groupname of the user
        :type groupname: str
        """
        
        if not self.check_username(username) or not self.check_groupname(groupname):
            return 0;
        
        # ADDING <username> TO groupusers<groupname>
        self.cursor.execute(f"""INSERT INTO groupusers{groupname} VALUES ('{username}', {isAdmin})""")
        self.connection.commit()
        print("Successfully added to group")
        return 6;
        
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''  
      
    def delete_user_in_group(self, username, groupname):
        """
        Removes the user with name as username from the group whose name is groupname.
        
        :param username: username of the user
        :type username: str
        :param groupname: groupname of the user
        :type groupname: str
        """
    
        if not self.check_username(username) or not self.check_groupname(groupname) or not self.check_user_in_group(username, groupname):
            return 0;
            
        # REMOVING <username> FROM grouptable<groupname>
        self.cursor.execute(f"""DELETE FROM groupusers{groupname} WHERE username = '{username}'""")
        self.connection.commit()
        print("Successfully Deleted from group")
        return 4
        
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''      
    
    def get_key(self, username):
        """
        Returns publicKey of the user with name as username.
        
        :param username: username of the user
        :type username: str
        :return: publicKey of the user
        :rtype: str
        """
    
        if not self.check_username(username):
            return 0
            
        self.cursor.execute(f"""SELECT (publicKey) FROM Users WHERE username = '{username}'""")
        print("Key retrieved")
        self.connection.commit()
        return self.cursor.fetchall()[0][0]
    
    
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''    
        
    def update_key(self, username, key):
        """
        Adds publicKey of the user with name as username.
        :param username: username of the user
        :type username: str
        """
    
        if not self.check_username(username):
            return 0
        
        self.cursor.execute(f"""UPDATE Users
                                SET publicKey = '{key}'
                                WHERE username = '{username}'""")
                                
        print("Key updated successfully")   
        self.connection.commit()
        return 2
    
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''    
    
    def close_connection(self):
        """ 
        Closes the connection with the database
        """
        if self.connection:
            self.cursor.close()
            self.connection.close()
            # print("PostgreSQL connection is closed")

    
# IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
                                

    
            
if __name__ == "__main__":
    db = Database()
    db.make_users_table()
    db.make_groups_table()
    time.sleep(5.0)
    db.create_user('Henry', '123')
    db.update_key('Henry', 'ABC')
    """
    db.check_username('Tim')
    db.create_group_database('hash', 'Tim')
    db.create_user('Jack', '123', 'B')
    db.add_user_to_group('Jack', 'hash')
    db.check_user_in_group('Jack', 'hash')
    db.authenticate('Jack', '123')
    db.change_status('Jack', 0)
    print(db.get_status('Tim'))
    db.message_sent_to_user('Jack', 'ho')
    db.change_status('Jack', 1) # login
    print(db.message_ret('Jack'))
    db.change_status('Jack', 0) # logout
    db.message_sent_to_user('Jack', 'hey')
    #db.message_sent_to_group('Tim', 'hash', 'jump')
    print(db.get_all_users('hash'))
    db.change_status('Jack', 1) # login
    print(db.message_ret('Jack'))
    db.delete_user_in_group('Jack', 'hash')
    print(db.get_key('Tim'))
    db.update_key('Tim', 'C')
    """
    
    
    
    
    
    
    
    
    
