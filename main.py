import os

#Added because of dll problems on Windows : https://github.com/kivy/kivy/issues/6335
os.environ["KIVY_NO_ARGS"] = "1"
os.environ['KIVY_IMAGE'] = "pil,sdl2"
os.environ['PATH'] += ';' + os.path.expandvars('%AppData%\\Python\\share\\glew\\bin')
os.environ['PATH'] += ';' + os.path.expandvars('%AppData%\\Python\\share\\sdl2\\bin')


import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
# to use buttons:
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
import database as db
from functools import partial

kivy.require("1.10.1")


class ConnectPage(GridLayout):
    # runs on initialization
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2  # used for our grid

        self.add_widget(Label(text='Username:'))  # widget #1, top left
        self.username = TextInput(text = "", multiline=False)  # defining self.username...
        self.add_widget(self.username) # widget #2, top right

        self.add_widget(Label(text='Password :'))
        self.password = TextInput(text="", multiline=False)
        self.add_widget(self.password)

        # add our button.
        self.join = Button(text="Connect")
        self.join.bind(on_press=self.join_button)
        self.add_widget(Label())  # just take up the spot.
        self.add_widget(self.join)

        self.register = Button(text="Register")
        self.register.bind(on_press=self.register_button)
        self.add_widget(Label())  # just take up the spot.
        self.add_widget(self.register)

    def join_button(self, instance):
        password = self.password.text
        username = self.username.text
        #print(f"Joining {username}:{password} as {username}")
        # Create info string, update InfoPage with a message and show it
        info = f"Joining as {username}"
        chat_app.info_page.update_info(info)
        chat_app.screen_manager.current = 'Info'
        if db.user_login(username, password) :
            chat_app.connected_user = username
            chat_app.create_homepage()
            chat_app.screen_manager.current = 'Home'
        else : 
            print("Failed to connect. Bad username/password combination")
            chat_app.screen_manager.current = 'Connect'
            
    def register_button(self, instance) : 
            chat_app.screen_manager.current = 'Register'
        

class RegisterPage(GridLayout) : 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2  # used for our grid

        self.add_widget(Label(text='Username :'))  # widget #1, top left
        self.username = TextInput(text = "", multiline=False)  # defining self.username...
        self.add_widget(self.username) # widget #2, top right

        self.add_widget(Label(text='Firstname :'))  # widget #1, top left
        self.firstname = TextInput(text = "", multiline=False)  # defining self.username...
        self.add_widget(self.firstname) # widget #2, top right

        self.add_widget(Label(text='Lastname :'))  # widget #1, top left
        self.lastname = TextInput(text = "", multiline=False)  # defining self.username...
        self.add_widget(self.lastname) # widget #2, top right

        self.add_widget(Label(text='Password :'))
        self.password = TextInput(text="", multiline=False)
        self.add_widget(self.password)

        self.join = Button(text="Register")
        self.join.bind(on_press= self.register_button)
        self.add_widget(Label())  # just take up the spot.
        self.add_widget(self.join)

    def register_button(self, instance) : 
        db.new_user(self.lastname.text, self.firstname.text, self.username.text, self.password.text)
        chat_app.screen_manager.current = 'Connect'



# This class is an improved version of Label
# Kivy does not provide scrollable label, so we need to create one
class ScrollableLabel(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ScrollView does not allow us to add more than one widget, so we need to trick it
        # by creating a layout and placing two widgets inside it
        # Layout is going to have one collumn and and size_hint_y set to None,
        # so height wo't default to any size (we are going to set it on our own)
        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.add_widget(self.layout)

        # Now we need two wodgets - Label for chat history and 'artificial' widget below
        # so we can scroll to it every new message and keep new messages visible
        # We want to enable markup, so we can set colors for example
        self.chat_history = Label(size_hint_y=None, markup=True)
        self.scroll_to_point = Label()

        # We add them to our layout
        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)

    def update_chat_history_layout(self, _=None):
        # Set layout height to whatever height of chat history text is + 15 pixels
        # (adds a bit of space at the bottom)
        # Set chat history label to whatever height of chat history text is
        # Set width of chat history text to 98 of the label width (adds small margins)
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)

    # Methos called externally to add new message to the chat history
    def update_chat_history(self, message):

        # First add new line and message itself
        self.chat_history.text += '\n' + message

        # Set layout height to whatever height of chat history text is + 15 pixels
        # (adds a bit of space at teh bottom)
        # Set chat history label to whatever height of chat history text is
        # Set width of chat history text to 98 of the label width (adds small margins)
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)

        # As we are updating above, text height, so also label and layout height are going to be bigger
        # than the area we have for this widget. ScrollView is going to add a scroll, but won't
        # scroll to the botton, nor there is a method that can do that.
        # That's why we want additional, empty wodget below whole text - just to be able to scroll to it,
        # so scroll to the bottom of the layout
        self.scroll_to(self.scroll_to_point)



class HomePage(BoxLayout) : 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation='vertical'
        self.box1 = BoxLayout(size_hint = (1 , .2))
        self.box2 = BoxLayout()
        self.contacts_grid = GridLayout(cols=3)
        l = Label(text='Your contacts list : ', size_hint = (1 , .2))
        self.add_widget(l)
        self.add_widget(self.box2)
        self.add_widget(self.box1)
        self.box2.add_widget(self.contacts_grid)

        self.search = TextInput( multiline=False)
        self.send = Button(text="Start chat with user :", size_hint=(.3, 1))

        self.box1.add_widget(self.send)
        self.box1.add_widget(self.search) # widget #2, top right

        chat_app.contact = self.search.text
        self.send.bind(on_press=self.start_chat)
        all_contacts = db.getContacts(chat_app.connected_user)
        for elem in all_contacts : 
            self.button = Button(text=f"{elem}", size_hint= (.8, .8))
            self.contacts_grid.add_widget(self.button)
            self.button.bind(on_press= partial(self.start_chat_with, f'{elem}'))

    def start_chat_with(self, contact, instance) :
        chat_app.contact = contact
        print(contact)
        if not db.chatExists(chat_app.contact, chat_app.connected_user) :
            db.new_chat(chat_app.connected_user, chat_app.contact)
        chat_app.create_chat_page()
        chat_app.screen_manager.current = 'Chat'

    def start_chat(self, instance) :   #Merge with function before didn't work 
        chat_app.contact = self.search.text
        if not db.chatExists(chat_app.contact, chat_app.connected_user) :
            db.new_chat(chat_app.connected_user, chat_app.contact)
        chat_app.create_chat_page()
        chat_app.screen_manager.current = 'Chat'

class ChatPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # We are going to use 1 column and 2 rows
        self.cols = 1
        self.rows = 3
        self.bind(size=self.adjust_fields)

        self.back = Button(text="Back")
        self.back.bind(on_press=self.back_button)
        self.add_widget(self.back)  # just take up the spot.
        # First row is going to be occupied by our scrollable label
        # We want it be take 90% of app height
        self.history = ScrollableLabel(height=Window.size[1]*0.9, size_hint_y=None)
        self.add_widget(self.history)

        # In the second row, we want to have input fields and Send button
        # Input field should take 80% of window width
        # We also want to bind button click to send_message method
        self.new_message = TextInput(width=Window.size[0]*0.8, size_hint_x=None, multiline=False)
        self.send = Button(text="Send")
        self.send.bind(on_press=self.send_message)

        # To be able to add 2 widgets into a layout with just one collumn, we use additional layout,
        # add widgets there, then add this layout to main layout as second row
        bottom_line = GridLayout(cols=2)
        bottom_line.add_widget(self.new_message)
        bottom_line.add_widget(self.send)
        self.add_widget(bottom_line)
        
        
        Window.bind(on_key_down=self.on_key_down)
        Clock.schedule_once(self.focus_text_input, 1)
        #socket_client.start_listening(self.incoming_message, show_error)
        
        chat_app.chat = db.getChatId(chat_app.connected_user, chat_app.contact)[1:]
        self.calls = 0

        message_list = db.messageHistory(chat_app.chat)
        if message_list : 
            for message in message_list: 
                if message_list[message]["sender"] == chat_app.connected_user : 
                    self.history.update_chat_history(f'[color=dd2020]{chat_app.connected_user}[/color] > {message_list[message]["message"]}')
                else : 
                    self.history.update_chat_history(f'[color=20dd20]{chat_app.contact}[/color] > {message_list[message]["message"]}')


        db.messages_ref.listen(self.listener)
    # Gets called when either Send button or Enter key is being pressed
    # (kivy passes button object here as well, but we don;t care about it)

    def listener(self, event):
        self.calls += 1
        if self.calls > 1 :  
            #print(event.event_type)  # can be 'put' or 'patch'
            #print(event.path)  # relative to the reference, it seems
            #print(event.data)  # new data at /reference/event.path. None if deleted
            if event.data["sender"] == chat_app.contact :   #add ?[f'-{chat_app.chat}']
                self.incoming_message(event.data["sender"], event.data["message"])

    def send_message(self, _):
        #print("send a message!!!")
        self.history.update_chat_history(f'[color=dd2020]{chat_app.connected_user}[/color] > {self.new_message.text}')
        db.new_message(chat_app.chat, chat_app.connected_user, self.new_message.text)
        self.new_message.text = ''
        Clock.schedule_once(self.focus_text_input, 0.1)

        
    def adjust_fields(self, *_):
    
        # Chat history height - 90%, but at least 50px for bottom new message/send button part
        if Window.size[1] * 0.1 < 50:
            new_height = Window.size[1] - 50
        else:
            new_height = Window.size[1] * 0.9
        self.history.height = new_height

        # New message input width - 80%, but at least 160px for send button
        if Window.size[0] * 0.2 < 160:
            new_width = Window.size[0] - 160
        else:
            new_width = Window.size[0] * 0.8
        self.new_message.width = new_width

        # Update chat history layout
        #self.history.update_chat_history_layout()
        Clock.schedule_once(self.history.update_chat_history_layout, 0.01)

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        # But we want to take an action only when Enter key is being pressed, and send a message
        if keycode == 40:
            self.send_message(None)
    
    def focus_text_input(self, _):
        self.new_message.focus = True

    def incoming_message(self, username, message):
        # Update chat history with username and message, green color for username
        self.history.update_chat_history(f'[color=20dd20]{username}[/color] > {message}')

    def back_button(self, instance) :
        chat_app.screen_manager.current = 'Home'
        chat_app.screen_manager.remove_widget(chat_app.screen_chat)





# Simple information/error page
class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Just one column
        self.cols = 1

        # And one label with bigger font and centered text
        self.message = Label(halign="center", valign="middle", font_size=30)

        # By default every widget returns it's side as [100, 100], it gets finally resized,
        # but we have to listen for size change to get a new one
        # more: https://github.com/kivy/kivy/issues/1044
        self.message.bind(width=self.update_text_width)

        # Add text widget to the layout
        self.add_widget(self.message)

    # Called with a message, to update message text in widget
    def update_info(self, message):
        self.message.text = message

    # Called on label width update, so we can set text width properly - to 90% of label width
    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)


class EpicApp(App):
    connected_user = ''
    chat = ''
    contact = ''
    def build(self):

        # We are going to use screen manager, so we can add multusernamele screens
        # and switch between them
        self.screen_manager = ScreenManager()

        # Initial, connection screen (we use passed in name to activate screen)
        # First create a page, then a new screen, add page to screen and screen to screen manager
        self.connect_page = ConnectPage()
        screen = Screen(name='Connect')
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        # Info page
        self.info_page = InfoPage()
        screen = Screen(name='Info')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        self.register_page = RegisterPage()
        screen = Screen(name='Register')
        screen.add_widget(self.register_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    # We cannot create chat screen with other screens, as it;s init method will start listening
    # for incoming connections, but at this stage connection is not being made yet, so we
    # call this method later
    def create_chat_page(self):
        self.chat_page = ChatPage()
        self.screen_chat = Screen(name='Chat')
        self.screen_chat.add_widget(self.chat_page)
        self.screen_manager.add_widget(self.screen_chat)
    def create_homepage(self):
        self.home_page = HomePage()
        screen = Screen(name='Home')
        screen.add_widget(self.home_page)
        self.screen_manager.add_widget(screen)


# Error callback function, used by sockets client
# Updates info page with an error message, shows message and schedules exit in 10 seconds
# time.sleep() won't work here - will block Kivy and page with error message won't show up
def show_error(message):
    chat_app.info_page.update_info(message)
    chat_app.screen_manager.current = 'Info'
    Clock.schedule_once(sys.exit, 10)

if __name__ == "__main__":
    chat_app = EpicApp()
    chat_app.run()