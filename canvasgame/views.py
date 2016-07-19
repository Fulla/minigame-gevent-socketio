from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from socketio.namespace import BaseNamespace
from socketio.sdjango import namespace
from socketio import socketio_manage
import random
import gevent
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

    user = {'xpos':0,'ypos':0}
    bot = {'xpos':300,'ypos':300}

    def on_move(self,usr):
        self.user = { 'xpos':usr.get('xpos'), 'ypos':usr.get('ypos') }
        self.detectCollision()

    def detectCollision(self):
        if abs( self.user.get('xpos') - self.bot.get('ypos') ) < 30 and abs( self.user.get('ypos') - self.bot.get('ypos') ) < 30:
            self.emit('collision',{ 'coordx':self.bot.get('xpos'), 'coordy':self.bot.get('ypos') })
            return true

    def recv_connect(self):
        def startGame():
            print "conecta"
            xsup = 994;
            ysup = 738;
            self.bot['xpos'] = random.randint(0,xsup)
            self.bot['ypos'] = random.randint(0,ysup)
            self.emit('init', { 'coordx':self.user.get('xpos'), 'coordy':self.user.get('ypos') })
            while True:
                self.botmove()
                self.emit('botmove',{ 'coordx':self.bot.get('xpos'), 'coordy':self.bot.get('ypos') })
                col = self.detectCollision()
                if col:
                    gevent.sleep(3)
                    self.bot['xpos'] = random.randint(0,xsup)
                    self.bot['ypos'] = random.randint(0,ysup)
                    self.emit('botmove',{ 'coordx':self.bot.get('xpos'), 'coordy':self.bot.get('ypos') })
                else if self.arrivesdest():
                    self.newdest()
                gevent.sleep(0.1)

        self.spawn(startGame)

    def botmove(self):
        self.user['xpos'] = random.randint(0,xsup)
        self.user['ypos'] = random.randint(0,ysup)

    # def on_connection(request,socket,context):
    #     # xsup = request.data.xsup
    #     # ysup = request.data.ysup
