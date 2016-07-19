# Catch the dot Mini-game

This is a mini-game made for learning purposes.
Here, I've tried gevent-socketio technologies for full-duplex server - client communication.
Also, I've tried the html5 canvas and played with the animation loop to redraw it according to the changes in game.

The game consists of a display in which there are two points, the bot (in green) and the player (in white).
Once made the connection, server constantly sends to client the position of the bot, and such a movement is reflected in the canvas.
Also, player can move his "character" with keyboard arrows (up, down, left, right). Player movements are sent to the server, which updates his own player representation and checks for possible "collisions". When server detects a collision, sends an event to client (so it stops drawing it). After 3 seconds restarts the bot in a new random position and resumes the bot movement loop.

By now, the only goal is to catch the bot (i.e., generate collisions).
In the current state of the game, there is no collisions counter, nor any other element to spice the game.
Although it was just for learning purposes, maybe I work a little bit more on it later.
