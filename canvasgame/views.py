from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from socketio.namespace import BaseNamespace
from socketio.sdjango import namespace
from socketio import socketio_manage
import random
import gevent
from gevent.event import Event
import logging
logging.basicConfig()

# Create your views here.

def CanvasGame(request):
    context = {}
    template = loader.get_template('canvasgame/app.html')

    return HttpResponse(template.render(context,request))

def socketio_service(request):
    socketio_manage(request.environ, {'/game': GameNamespace}, request)
    return 'out'

@namespace('/game')
class GameNamespace(BaseNamespace):

    def initialize(self):
        self.botalive = Event()
        self.running = Event()
        self.user = {'xpos':0,'ypos':0}
        self.bot = {'xpos':100,'ypos':100}
        self.bounds = {'xsup':400, 'ysup':300 }
        self.dest = {'xpos':0,'ypos':0}
        self.lastmove = {'x': 0, 'y': 0}
        self.paused = True
        self.maxDist = 70
        # the size of the player and bot is 10x10, so there're virtually
        # 40 horizontal slots per 30 vertical slots to be into

    # when the user sets the pause state
    def on_pause(self):
        if self.paused:
            self.paused = False
            self.running.set()
            self.emit('resume')
        else:
            self.paused = True
            self.running.clear()
            self.emit('pause')
        return True

    # when the client activates an event to move the user
    def on_move(self,mov):
        self.lastmove = {'x': mov.get('x', 0), 'y': mov.get('y', 0)}
        return True

    # cheks if a collition between the user and the bot has happened. If it is the case, destroys and resets the bot
    def detectCollision(self):
        if abs( self.user.get('xpos') - self.bot.get('xpos') ) < 10 and abs( self.user.get('ypos') - self.bot.get('ypos') ) < 10:
            self.emit('collision',{ 'coordx':self.bot.get('xpos'), 'coordy':self.bot.get('ypos') })
            self.botalive.clear()
            self.botreset()

    # if bot is destroyed, resets the bot in a new position after 2 seconds and resumes the game loop
    def botreset(self):
        self.bot['xpos'] = random.randint(0,self.bounds.get('xsup'))
        self.bot['ypos'] = random.randint(0,self.bounds.get('ysup'))
        self.newdest()
        gevent.sleep(2)
        self.emit('botmove',{ 'coordx':self.bot.get('xpos'), 'coordy':self.bot.get('ypos') })
        self.botalive.set()

    # obtains a new destination for the bot, after it reaches the previous one
    def newdest(self):
        xpos = self.bot.get('xpos', 0)
        ypos = self.bot.get('ypos', 0)
        self.dest['xpos'] = random.randint(max(0, xpos - self.maxDist), min(self.bounds.get('xsup'), xpos + self.maxDist))
        self.dest['ypos'] = random.randint(max(0, ypos - self.maxDist), min(self.bounds.get('ysup'), ypos + self.maxDist))

    # returs true if the current position of the bot is next to the current destination
    def arrivesdest(self):
        if abs( self.bot.get('xpos') - self.dest.get('xpos') ) < 10 and abs( self.bot.get('ypos') - self.dest.get('ypos') ) < 10:
            return True
        return False

    # when the server receives a socket connection request
    def recv_connect(self):
        def startGame():
            self.bot['xpos'] = random.randint(0,self.bounds.get('xsup'))
            self.bot['ypos'] = random.randint(0,self.bounds.get('ysup'))
            self.newdest()
            self.emit('init', { 'coordx':self.user.get('xpos'), 'coordy':self.user.get('ypos') })
            self.botalive.set()
            self.running.set()
            while True: # the game loop
                self.botmove()
                self.usermove()
                self.detectCollision()
                if self.arrivesdest():
                    self.newdest()
                gevent.sleep(0.01)
                self.botalive.wait()
                self.running.wait()
        self.spawn(startGame)
        return True

    def recv_disconnect(self):
        self.disconnect(silent=True)
        return True

    # moves the bot to a position toward the current destination
    def botmove(self):
        willMovX = bool(random.getrandbits(1))
        willMovY = bool(random.getrandbits(1))

        difX = self.dest.get('xpos') - self.bot.get('xpos')
        speedX = 0
        if difX < 0:
            speedX = min((difX / self.maxDist) * 5, -2) * willMovX
        if difX > 0:
            speedX = max((difX / self.maxDist) * 5, 2) * willMovX

        difY = self.dest.get('ypos') - self.bot.get('ypos')
        speedY = 0
        if difY < 0:
            speedY = min((difY / self.maxDist) * 5, -2) * willMovY
        if difY > 0:
            speedY = max((difY / self.maxDist) * 5, 2) * willMovY

        self.bot['xpos'] = self.bot['xpos'] + speedX
        self.bot['ypos'] = self.bot['ypos'] + speedY
        self.emit('botmove',{ 'coordx':self.bot.get('xpos'), 'coordy':self.bot.get('ypos') })


    def usermove(self):
        userx = self.user.get('xpos') + self.lastmove.get('x')
        usery = self.user.get('ypos') + self.lastmove.get('y')
        self.user = { 'xpos': userx, 'ypos': usery}
        self.emit('usermove', { 'coordx': userx, 'coordy': usery })
