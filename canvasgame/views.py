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
        self.bot = {'xpos':300,'ypos':300}
        self.bounds = {'xsup':994, 'ysup':738 }
        self.dest = {'xpos':0,'ypos':0}

    # when the user sets the pause state
    def on_pause(self):
        self.running.clear()
        return True

    # when the user quits the pause state
    def on_resume(self):
        self.running.set()
        return True

    # when the client activates an event to move the user
    def on_move(self,usr):
        self.user = { 'xpos':usr.get('xpos'), 'ypos':usr.get('ypos') }
        self.detectCollision()
        return True

    # cheks if a collition between the user and the bot has happened. If it is the case, destroys and resets the bot
    def detectCollision(self):
        if abs( self.user.get('xpos') - self.bot.get('xpos') ) < 30 and abs( self.user.get('ypos') - self.bot.get('ypos') ) < 30:
            self.emit('collision',{ 'coordx':self.bot.get('xpos'), 'coordy':self.bot.get('ypos') })
            self.botalive.clear()
            self.botreset()

    # if bot is destroyed, resets the bot in a new position after 3 seconds and resumes the game loop
    def botreset(self):
        self.bot['xpos'] = random.randint(0,self.bounds.get('xsup'))
        self.bot['ypos'] = random.randint(0,self.bounds.get('ysup'))
        self.newdest()
        gevent.sleep(3)
        self.emit('botmove',{ 'coordx':self.bot.get('xpos'), 'coordy':self.bot.get('ypos') })
        self.botalive.set()

    # obtains a new destination for the bot, after it reaches the previous one
    def newdest(self):
        self.dest['xpos'] = random.randint(0,self.bounds.get('xsup'))
        self.dest['ypos'] = random.randint(0,self.bounds.get('ysup'))

    # returs tru if the current position of the bot is next to the current destination
    def arrivesdest(self):
        if abs( self.bot.get('xpos') - self.dest.get('xpos') ) < 30 and abs( self.bot.get('ypos') - self.dest.get('ypos') ) < 30:
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
                self.detectCollision()
                if self.arrivesdest():
                    self.newdest()
                gevent.sleep(0.1)
                self.botalive.wait()
                self.running.wait()
        self.spawn(startGame)
        return True

    def recv_disconnect(self):
        self.disconnect(silent=True)
        return True

    # moves the bot to a position toward the current destination
    def botmove(self):
        direction = bool(random.getrandbits(1))
        if direction:
            if self.bot.get('xpos') < self.dest.get('xpos'):
                self.bot['xpos'] = self.bot.get('xpos') + 5
            else:
                self.bot['xpos'] = self.bot.get('xpos') - 5
        else:
            if self.bot.get('ypos') < self.dest.get('ypos'):
                self.bot['ypos'] = self.bot.get('ypos') + 5
            else:
                self.bot['ypos'] = self.bot.get('ypos') - 5
        # self.bot['xpos'] = max(min(self.bot.get('xpos') + random.randint(-5,5), self.bounds.get('xsup')), 0)
        # self.bot['ypos'] = max(min(self.bot.get('ypos') + random.randint(-5,5), self.bounds.get('ysup')), 0)
        self.emit('botmove',{ 'coordx':self.bot.get('xpos'), 'coordy':self.bot.get('ypos') })
