# Pup_up_on_Flask
#### Video Demo:  https://drive.google.com/file/d/1PhssEv2-yn4_TeC7qso7FSxHhJfkAGph/view
### App: http://rlhenshaw.pythonanywhere.com/
#### Description:
Tinder for adopting dogs; emphasizes location and photos; deployed with Flask on Python Anywhere

This project for CS50 was built with Flask, python, JavaScript, CSS, HTML is deployed on Python Anywhere at: http://rlhenshaw.pythonanywhere.com/
The dog and thought bubble were borrowed from open source and are credited in the CSS file "dog.css".
The idea of this web app (eventually should be a mobile app) is to get a quick fix on an adoptable dog, and potentially save the profile for later. Users can use the site without registering but must register if they want to save any dogs. 

This app uses the free PetFinder API for the database.

The CSS dog, only when on the dog profile screen, will make comments about the pups, personalized with the dog's name. He says 4-5 different phrases. I also implemented a "how many times this dog was saved" feature so people know which dog is popular. 

Database Design:
There are 3 tables, ones for just dogs, one for just users, and one for mapping the many to many relationship between dogs and users, so that each dog is only saved once in the database regardless of how many people flag it. Primary Keys are autoincremented integers, indexes were created for each common search.

User design:
Simple web-app user interface. The animated dog was fun to make work. The design is meant to be simple and intuitive. CSS/Bootstrap was used, as well as CSS characters borrowed from open source as referenced. 

app.py
This has routes and the main interactions with the database. Also as sessions implemented. 

helpers.py
This file is for interacting with the API and helper functions are here. As well as a function to auto-create a token, which expires every hour. 

Static Files:
I chose two CSS files to separate the dog and thought bubble from CSS that was fully mine. I felt it was easier to keep it organized this way.

Templates:
I chose to make a main layout function that did not have the dog, because I didn't want the dog on the database page. The template with the dog inherits from the main template, and then most others inherit directly from the dog. This is to eliminate repeated text.
