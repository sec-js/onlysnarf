import json
import time
import os
import threading
from datetime import datetime, timedelta
from re import sub
from decimal import Decimal
import PyInquirer
##
from ..util.colorize import colorize
from ..lib.driver import Driver
from ..util.settings import Settings

class User:

    def __init__(self, data):

        data = json.loads(json.dumps(data))
        self.name               =   data.get('name')                            or None
        self.username           =   str(data.get('username')).replace("@","")   or None
        self.id                 =   data.get('id')                              or None
        self.messages_parsed    =   data.get('messages_parsed')                 or []
        self.messages_sent      =   data.get('messages_sent')                   or []
        self.messages_received  =   data.get('messages_received')               or []
        self.messages           =   data.get('messages')                        or []
        self.preferences        =   data.get('preferences')                     or []
        self.last_messaged_on   =   data.get('last_messaged_on')                or None
        self.sent_files         =   data.get('sent_files')                      or []
        self.subscribed_on      =   data.get('subscribed_on')                   or None
        self.isFavorite         =   data.get('isFavorite')                      or False
        self.lists              =   data.get('lists')                           or []
        self.statement_history  =   data.get('statement_history')               or []
        self.started            =   data.get('started')                         or None
        ###### fucking json #####
        self.messages_sent      =   ",".join(self.messages_sent).split(",")     or []
        self.messages_received  =   ",".join(self.messages_sent).split(",")     or []
        self.messages           =   ",".join(self.messages_sent).split(",")     or []
        self.messages_parsed    =   ",".join(self.messages_parsed).split(",")   or []
        self.preferences        =   ",".join(self.messages_sent).split(",")     or []
        self.sent_files         =   ",".join(self.messages_sent).split(",")     or []
        self.statement_history  =   ",".join(self.messages_sent).split(",")     or []
        #########################
        self.discount           =   None
        self.promotion          =   None
        #########################

        # try:
            # Settings.dev_print("user: {} - {} - {}".format(self.name, self.username, self.id))
        # except Exception as e:
            # Settings.dev_print(e)
            # Settings.dev_print("user: {}".format(self.id))

        # BUG: fix empty array
        if self.sent_files[0] == "":
            self.sent_files = []


    def get_id(self):

        """
        Get the provided ID of the User.

        """

        if self.id: return self.id
        id_ = Driver.get_driver().user_get_id(self.get_username())
        self.id = id_
        return self.id

    def get_username(self):

        """
        Get the @username of the User.

        """

        if self.username: return self.username
        username = Driver.get_driver().user_get_username(self.get_id())
        self.username = username
        return self.username

    def message(self, message):

        """
        Message the user by their available username or id with the provided message.

        Parameters
        ----------
        message : Object
            The message to send as a serialized Message object from get_message.

        """

        if not self.get_username() and not self.get_id(): return Settings.error("Missing user identifiers")
        Settings.print("messaging user (id): {} ({}) <-- {}".format(self.username, self.id, message["text"]))
        successful = Driver.get_driver().message(self.username, user_id=self.id)
        if not successful: return False
        successful = self.enter_message(message)
        if not successful: return False
        Settings.print("messaged: user (id): {} ({})".format(self.username, self.id))
        return True

    @staticmethod
    def message_user(message, username, user_id=None):

        """
        Message the user by their available username or id with the provided message data.

        Parameters
        ----------
        message : Object
            The message to send as a serialized Message object from get_message.
        """

        user = User({"username":username,"id":user_id})
        return user.message(message)    

    def enter_message(self, message):

        """
        Complete the various components of sending a message to a user.
        
        Parameters
        ----------
        message : Object
            The message to send as a serialized Message object from get_message.

        """

        Settings.print("entering message: {} - ${}".format(message["text"], message["price"] or 0))
        try:
            # enter the text of the message
            def enter_text(text):
                return Driver.get_driver().message_text(text)
            # enter the price to send the message to the user
            def enter_price(price):
                if not price: return True
                if price != None and Decimal(sub(r'[^\d.]', '', str(price))) < Decimal(Settings.get_price_minimum()):
                    Settings.warn_print("price too low; {} < {}".format(price, Settings.get_price_minimum()))
                    return False
                return Driver.get_driver().message_price(price)
            # enter files by filepath while checking for already sent files
            def enter_files(files):
                # if isinstance(files, str) and str(files) == "unset": return True
                for file in files:
                    file_name = file.get_title()
                    if str(file_name) in self.sent_files:
                        Settings.err_print("file already sent to user: {} <-- {}".format(self.username, file_name))
                        # return False
                        continue
                    self.sent_files.append(file_name)
                return Driver.get_driver().upload_files(files)
            def confirm_message():
                return Driver.get_driver().message_confirm()
            successful = []
            successful.append(enter_text(message["text"]))
            successful.append(enter_price(message["price"]))
            successful.append(enter_files(message["files"]))
            if all(successful): return confirm_message()
        except Exception as e:
            Settings.err_print("message failed!")
            Settings.dev_print(e)
        return False

    def equals(self, user):
        """
        Equals comparison checks usernames and ids.

        Parameters
        ----------
        user : classes.User
            The classes.User to compare this classes.User object against.
        """

        # Settings.print(str(user.username)+" == "+str(self.username))
        if str(user.username) == str(self.username) or str(user.id) == str(self.id):
            return True
        return False

    def toJSON(self):
        """
        Dumps relevant user data to JSON.
        """

        return json.dumps({
            "name":str(self.name),
            "username":str(self.username),
            "id":str(self.id),
            "messages_parsed":str(self.messages_parsed),
            "messages_sent":str(self.messages_sent),
            "messages_received":str(self.messages_received),
            "messages":str(self.messages),
            "preferences":str(self.preferences),
            "last_messaged_on":str(self.last_messaged_on),
            "sent_files":str(self.sent_files),
            "subscribed_on":str(self.subscribed_on),
            "isFavorite":str(self.isFavorite)
        })

    def read_messages(self):
        """
        Read the chat of the user.
        """

        Settings.print("reading user chat: {} - {}".format(self.username, self.id))
        messages, messages_received, messages_sent = Driver.get_driver().read_user_messages(self.username, user_id=self.id)
        self.messages = messages
        self.messages_received = messages_received
        self.messages_sent = messages_sent
        # self.messages_and_timestamps = messages[1]
        Settings.maybe_print("chat read: {} - {}".format(self.username, self.id))

    def update(self, user):
        # print("classes.User: THIS NEEDS TO BE FIXED")
        # return # todo fix this
        for key, value in json.loads(user.toJSON()).items():
            # Settings.print("updating: {} = {}".format(key, value))
            setattr(self, str(key), value)

    @staticmethod
    def read_users_messages(users=[]):
        """
        Read all the users messages.

        Parameters
        ----------
        users : classes.User
            A list of users to read the messages of.

        """

        if len(users) == 0:
            users = User.get_all_users()
        Settings.print("updating chat logs: {}".format(len(users)))
        for user in users:
            user.read_messages()
        User.write_users_local(users=users)
        return users

    @staticmethod
    def get_all_users():
        return User.get_active_users()

    # gets users from local or refreshes from onlyfans.com
    @staticmethod
    def get_active_users():
        if Settings.is_prefer_local():
            users = User.read_users_local()
            if len(users) > 0: return users
        active_users = []
        users = Driver.get_driver().users_get()
        for user in users:
            try:
                user = User(user)
                user = User.skipUserCheck(user)
                if user is None: continue
                active_users.append(user)
            except Exception as e:
                Settings.dev_print(e)
        Settings.maybe_print("pruning memberlist")
        Settings.maybe_print("users: {}".format(len(active_users)))
        User.write_users_local(users=active_users)
        Settings.set_prefer_local(True)
        return active_users

    @staticmethod
    # return following Users
    def get_following():
        if Settings.is_prefer_local():
            users = User.read_following_local()
            if len(users) > 0: return users
        active_users = []
        users = Driver.get_driver().following_get()
        for user in users:
            try:
                user = User(user)
                user = User.skipUserCheck(user)
                if user is None: continue
                active_users.append(user)
            except Exception as e:
                Settings.dev_print(e)
        Settings.maybe_print("following: {}".format(len(active_users)))
        User.write_following_local(users=active_users)
        Settings.set_prefer_local(True)
        return active_users

    @staticmethod
    def get_random_user():
        import random
        return random.choice(User.get_all_users())














    def get_unparsed_messages(self):
        unparsed_messages = [m for m in self.messages if m not in self.messages_parsed]  
        Settings.dev_print("unparsed messages: {}\n{}".format(len(unparsed_messages),"\n".join(unparsed_messages)))
        return unparsed_messages














    @staticmethod
    def get_user_by_username(username):
        if not username or username == None:
            Settings.err_print("missing username")
            return None

        if str(username) == "all":
            return User.get_all_users()
        elif str(username) == "recent":
            return User.get_recent_users()
        elif str(username) == "favorite":
            return User.get_favorite_users()
        elif str(username) == "random":
            return User.get_random_user()
        

        users = User.read_users_local()
        for user in users:
            if str(user.username) == "@u"+str(username) or str(user.username) == "@"+str(username) or str(user.username) == str(username):
                Settings.maybe_print("found user: local")
                return user
        users = User.get_all_users()
        for user in users:
            if str(user.username) == "@u"+str(username) or str(user.username) == "@"+str(username) or str(user.username) == str(username):
                Settings.maybe_print("found user: members")
                return user
        Settings.err_print("missing user by username - {}".format(username))
        return None

    @staticmethod
    def get_user_by_id(userid):
        if not userid or userid == None:
            Settings.err_print("missing user id")
            return None

        users = User.read_users_local()
        for user in users:
            if str(user.id) == "@u"+str(userid) or str(user.id) == "@"+str(userid) or str(user.id) == str(userid):
                Settings.maybe_print("found user: local")
                return user
        users = User.get_all_users()
        for user in users:
            if str(user.id) == "@u"+str(userid) or str(user.id) == "@"+str(userid) or str(user.id) == str(userid):
                Settings.maybe_print("found user: members")
                return user
        Settings.err_print("missing user by user id - {}".format(userid))
        return None

    ## TODO
    # make this actually do something
    @staticmethod
    def get_favorite_users():
        Settings.maybe_print("getting favorite users")
        users = User.get_all_users()
        favUsers = []
        # favorites = ",".join(str(Settings.get_users_favorite()))
        for user in users:
            if user.isFavorite:
                Settings.maybe_print("fav user: {}".format(user.username))
                user = User.skipUserCheck(user)
                if user is None: continue
                favUsers.append(user)
        return favUsers

    @staticmethod
    def get_users_by_list(number=None, name=None, ):
        Settings.maybe_print("getting users by list: {} - {}".format(number, name))
        users = Driver.get_driver().get_list(number=number, name=name)
        listUsers = []
        for user in users:
            Settings.maybe_print("user: {}".format(user.username))
            user = User.skipUserCheck(user)
            if user is None: continue
            listUsers.append(user)
        return listUsers

    # returns users that have no messages sent to them
    @staticmethod
    def get_new_users():
        Settings.maybe_print("getting new users")
        users = User.get_all_users()
        newUsers = []
        date_ = datetime.today() - timedelta(days=10)
        for user in users:
            if not user.started: continue
            started = datetime.strptime(str(user.started),"%b %d, %Y")
            # Settings.maybe_print("date: "+str(date_)+" - "+str(started))
            if started < date_: continue
            Settings.maybe_print("new user: {}".format(user.username))
            user = User.skipUserCheck(user)
            if user is None: continue
            newUsers.append(user)
        return newUsers






    # probably not necessary
    def parse_message(self, message=None):
        self.messages.remove(str(message))
        self.messages_parsed.append(str(message))














    @staticmethod
    def get_recent_users():
        Settings.maybe_print("getting recent users")
        users = User.get_all_users()
        i = 0
        users_ = []
        for user in users:
            Settings.maybe_print("recent user: {}".format(user.username))
            user = User.skipUserCheck(user)
            if user is None: continue
            users_.append(user)
            i += 1
            if i == int(Settings.get_recent_user_count()):
                return users_
        return users_


    @staticmethod
    def get_never_messaged_users():
        Settings.maybe_print("getting new users")
        users = User.get_all_users()
        newUsers = []
        for user in users:
            if len(user.messages_received) == 0:
                Settings.maybe_print("never messaged user: {}".format(user.username))
                user = User.skipUserCheck(user)
                if user is None: continue
                newUsers.append(user)
        return newUsers

    @staticmethod
    def get_recent_messagers():
    # def get_recent_messagers(notusers=[], ):
        Settings.maybe_print("getting recent users from messages")
        users = []
        try:
            users_ = Driver.get_driver().messages_scan()
            # users_ = Driver.get_driver().messages_scan(num=notusers)
            for user in users_:
                users.append(User({"id":user}))
        except Exception as e:
            Settings.dev_print(e)
        return users











    @staticmethod
    def list_menu():
        question = {
            'type': 'list',
            'name': 'answer',
            'message': 'User:',
            'choices': ["Back", "Enter", "Select"]
        }
        answer = PyInquirer.prompt(question)["answer"]
        if str(answer) == "Back":
            Settings.print(0)
            return User.select_user()
        elif str(answer) == "Enter":
            question = {
                'type': 'input',
                'message': 'Enter List (name or #):',
                'name': 'list'
            }
            list_ = PyInquirer.prompt(question)["list"]
            theList = None
            try:
                theList = int(list_)
                users = User.get_users_by_list(number=theList)
            except Exception as e:
                try:
                    theList = str(list_)
                    return User.get_users_by_list(name=theList)
                except Exception as e:
                    Settings.err_print("unable to find list number")
        elif str(answer) == "Select":
            lists_ = Driver.get_driver().get_lists()
            lists__ = [{"name":"Back", "value":"back"}]
            for list___ in lists_:
                lists__.append({
                    "name":list___[1],
                    "value":list___[0],
                })
            question = {
                'type': 'list',
                'name': 'answer',
                'message': 'Lists:',
                'choices': lists_
            }
            answer = PyInquirer.prompt(question)["answer"]
            if str(answer) == "back":
                return User.select_user()
            else:
                return Driver.get_driver().get_list_members(answer)
        return []


















    @staticmethod
    def select_user():
        user = Settings.get_user() or None
        if user: return user
        # if user: return User.get_user_by_username(user.username)
        # if not Settings.prompt("user"): return User.get_random_user()
        choices = Settings.get_message_choices()
        choices.append("enter username")
        choices.append("select username")
        choices = [str(choice).title() for choice in choices]
        question = {
            'type': 'list',
            'name': 'user',
            'message': 'User:',
            'choices': choices,
            'filter': lambda val: str(val).lower()
        }
        answers = PyInquirer.prompt(question)
        user = answers["user"]
        if str(user) == "enter username":
            username = input("Username: ")
            return User.get_user_by_username(username)
        elif str(user) == "select username":
            return User.select_username()
        elif str(user) == "favorites":
            return User.get_favorite_users()
        elif str(user) == "list":
            return User.list_menu()
        elif str(user) == "all":
            return User.get_all_users()
        if not Settings.confirm(user): return User.select_user()
        return user

    @staticmethod
    def select_users():
        # if not Settings.prompt("users"): return []
        users = []
        while True:
            user = User.select_user()
            if not user: break
            if str(user).lower() == "all" or str(user).lower() == "recent": return [user]
            users.append(user)
            if not Settings.prompt("another user"): break
        if not Settings.confirm([user.username for user in users]): return User.select_users()
        return users

    @staticmethod
    def select_username():
        # returns the list of usernames to select
        # if not Settings.prompt("select username"): return None
        users = User.get_all_users()
        users_ = []
        for user in users:
            user_ = {
                "name":user.username.replace("@",""),
                "value":user,
                "short":user.id
            }
            users_.append(user_)
        question = {
            'type': 'list',
            'name': 'user',
            'message': 'Username:',
            'choices': users_
        }
        user = PyInquirer.prompt(question)['user']
        if not Settings.confirm(user.username): return User.select_username()
        return user















    def send_dick_pics(self, num):
        Settings.print("sending dick pics: {}".format(num))
        # pass
        # downloads a dick pic from configured source and sends to user

        # search source for dick pics
        # send dick pics
        # Settings.get_drive_keyword()
        Settings.set_bycategory("dick")
        message = Message()
        setattr(message, "text", "8=======D~~") # todo: randomize this
        self.message(message=message)







    @staticmethod
    def skipUserCheck(user):
        if str(user.id).lower() in Settings.get_skipped_users() or str(user.username).lower() in Settings.get_skipped_users():
            Settings.maybe_print("skipping: {}".format(user.username))
            return None
        return user





































    # gets a list of all subscribed user_ids from local txt
    @staticmethod
    def read_users_local():
        Settings.maybe_print("getting local users")
        users = []
        users_ = []
        try:
            with open(str(Settings.get_users_path())) as json_file:  
                users = json.load(json_file)['users']
            Settings.maybe_print("loaded local users")
            for user in users:
                try:
                    users_.append(User(json.loads(user)))
                except Exception as e:
                    Settings.dev_print(e)
            return users_
        except Exception as e:
            Settings.dev_print(e)
        return users_

    # writes user list to local txt
    @staticmethod
    def write_users_local(users=None):
        if users is None:
            users = User.get_all_users()
        if len(users) == 0:
            Settings.maybe_print("skipping: local users save - no users")
            return
        Settings.print("Saving Users Locally")
        Settings.maybe_print("local users path: "+str(Settings.get_users_path()))
        ##
        # update from existing
        existingUsers = User.read_users_local()
        for user in users:
            for user_ in existingUsers:
                if user.equals(user_):
                    user.update(user_)
        ##
        data = {}
        data['users'] = []
        for user in users:
            data['users'].append(user.toJSON())
        try:
            with open(str(Settings.get_users_path()), 'w') as outfile:  
                json.dump(data, outfile, indent=4, sort_keys=True)
        except FileNotFoundError:
            Settings.err_print("missing local users")
        except OSError:
            Settings.err_print("missing local path")

    @staticmethod
    def read_following_local():
        Settings.maybe_print("getting local following")
        users = []
        users_ = []
        try:
            with open(str(Settings.get_users_path().replace("users.json", "following.json"))) as json_file:  
                users = json.load(json_file)['users']
            Settings.maybe_print("loaded local following")
            for user in users:
                try:
                    users_.append(User(json.loads(user)))
                except Exception as e:
                    Settings.dev_print(e)
            return users_
        except Exception as e:
            Settings.dev_print(e)
        return users_

    @staticmethod
    def write_following_local(users=None):
        if users is None:
            users = User.get_following()
        if len(users) == 0:
            Settings.maybe_print("skipping: local following save - no following")
            return
        Settings.print("Saving Following Users Locally")
        Settings.maybe_print("local users path: "+str(Settings.get_users_path().replace("users.json", "following.json")))
        data = {}
        data['users'] = []
        for user in users:
            data['users'].append(user.toJSON())
        try:
            with open(str(Settings.get_users_path().replace("users.json", "following.json")), 'w') as outfile:  
                json.dump(data, outfile, indent=4, sort_keys=True)
        except FileNotFoundError:
            Settings.err_print("missing local following")
        except OSError:
            Settings.err_print("missing local path")



