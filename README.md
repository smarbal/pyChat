# pyChat
Proof of Concept that demonstrates the use of a Firebase Realtime database in a chat application.   
database.py contains the functions to connect and communicate with the Firebase database. 
main.py contains the functions to launch the program, show the interface and chat. 

## Installation 
First you need to install the Firebase Python SDK :  
```pip install firebase-admin```    
Then you have to install Kivy, we **recommend** doing that in a **virtual environnement** : 
```
python -m pip install --upgrade pip wheel setuptools    
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew  
python -m pip install kivy.deps.gstreamer  
python -m pip install kivy.deps.angle  
python -m pip install kivy   
 ```
You also need a file named service-key.json which you can export from your Firebase Realtime database.

## Features 
At the initial menu, you can either connect with an existing username or register a new user.   

Once you're connected, you'll see buttons of users you have already communicated with (you can click on them to open the chat). To communicate with a new user, type their username in the search bar and click on the button on the left to start a new chat with them.   

Chatting happens in real time and when you open the chatting page, it loads the 20 last messages that have been exchanged. The 20 limit can easily be changed in the database.py file. 
