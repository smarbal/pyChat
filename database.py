import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import time 
cred = credentials.Certificate("service_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://poc-chatapp-default-rtdb.europe-west1.firebasedatabase.app/'
})

ref = db.reference("/")
users_ref = ref.child("users")
chats_ref = ref.child("chats")
messages_ref = ref.child("messages")

def new_user(name, firstname, pseudo, password) : 
    data = { pseudo : 
             {"name" : name, 
            "firstname" : firstname, 
            "password" : password, 
            "chats" : { "none" : "true"    #needed to make it easier for the creation of chats

                }
             }
            }
    users_ref.update(data)

def new_chat(sender, receiver) : 
    chat = { sender : "true", 
            receiver : "true"
    }
    new_chat_ref = chats_ref.push(chat)
    chat_id = new_chat_ref.key
    
    receiver_dic = {receiver: chat_id}
    sender_dic = { sender : chat_id} 
    users_ref.child(f'{sender}/chats').update(receiver_dic)
    users_ref.child(f'{receiver}/chats').update(sender_dic)
    return chat_id



def new_message(chat, sender, message) : 
    now = time.time()
    message = { 
        "sender" : sender, 
        "message": message, 
        "timestamp": now
      }
    messages_ref.child(chat).push(message)

def user_login(username, password) : 
    user = users_ref.child(username).get()
    try : 
        if user["password"] == password : 
            return True 
    except : 
        pass 
    return False

def chatExists(receiver, sender) : 
    user_chats = users_ref.child(f'{sender}/chats').get()
    return receiver in user_chats.keys() 


def getChatId(sender, receiver) : 
    chatId = users_ref.child(f'{sender}/chats/{receiver}').get()
    return chatId

def messageHistory(chat_id) :
    mess_chat_ref = messages_ref.child(f'{chat_id}')
    snapshot = mess_chat_ref.order_by_child('timestamp').limit_to_last(20).get() 
    return snapshot

#elem = messageHistory("-MmOhnrkn9utT4FchpZa")
#print(elem)
#print(elem["-MmOi8uZHefgpLi0LOO_"])