$(function(){

  // Game objects setup
  var gameloop;
  var running;
  var user = {
    'speed':50,
    'xpos': 0,
    'ypos': 0
  };
  var bot = {
    'xpos': 300,
    'ypos': 300
  };
  var explosions = [];

  // Key event listeners
  var keys = {};
  document.addEventListener("keydown",function(e){
    if (e.keyCode != 32){
      keys[e.keyCode] = true;
    }
    else {
      if (running) {
        pauseGame();
      }
      else {
        resumeGame();
      }
    }
  }, false);
  document.addEventListener("keyup",function(e){
    delete keys[e.keyCode];
  }, false);

  // Render data setup
  var previousRend;
  var canvasVisor = document.getElementById('mapcanvas');
  var canvasCtx = canvasVisor.getContext('2d');

  // Each render of the canvas
  var renderCanvas = function(){
    canvasCtx.clearRect(0,0, canvasVisor.width, canvasVisor.height);
    // render user
    canvasCtx.fillStyle = "#FFFFFF";
    canvasCtx.fillRect(user.xpos, user.ypos, 30, 30);
    // render bot
    if (bot!={}) {
      canvasCtx.fillStyle = "#AACC88";
      canvasCtx.fillRect(bot.xpos, bot.ypos, 30, 30);
    }
    // render the explosions
    var now = Date.now();
    for(exp in explosions){
      canvasCtx.fillStyle = "#5500AA";
      canvasCtx.fillRect(exp.xpos + 15, exp.ypos + 15, 10, 10);
      if(now - exp.time > 5000){
        explosions.pop(exp);
      };
    };
  };

  // update the movement made by the user in the last deltaTime
  var updUserPos = function(deltaTime){
    if(38 in keys){ // up arrow
      user.ypos -= user.speed * deltaTime;
    };
    if(40 in keys){ // down arrow
      user.ypos += user.speed * deltaTime;
    };
    if(37 in keys){ // left arrow
      user.xpos -= user.speed * deltaTime;
    };
    if(39 in keys){ // right arrow
      user.xpos += user.speed * deltaTime;
    };
    socket.emit('move',user);  // sends the user new position to server
  };

  // each frame, this function is called to update the state of the game
  var updateCycle = function(){
    var now = Date.now();
    var delta = now - previousRend; // the time since last update
    updUserPos(delta / 1000); // updates the user position
    renderCanvas(); // reflect changes in the canvas
    previousRend = now;
  };

  var socket;


  var disconnected = function(){
    window.clearInterval(gameloop);
    canvasCtx.clearRect(0,0, canvasVisor.width, canvasVisor.height);
  };

  var pauseGame = function(){
    window.clearInterval(gameloop);
    socket.emit('pause');
  }

  var resumeGame = function(){
    previousRend = Date.now();
    socket.emit('resume');
    gameloop = window.setInterval(updateCycle,200);
  };

  var setupGame = function(data){
    user.xpos = data.coordx;
    user.ypos = data.coordy;
  };

  var botmoved = function(data){
    bot.xpos = data.coordx;
    bot.ypos = data.coordy;
    console.log(bot);
  };

  var collision = function(data){
    var col = {};
    col.time = Date.now();
    col.xpos = data.coordx;
    col.ypos = data.coordy;
    explosions.push(col);  // add in the list of explosions the coordinades and the generation time
    console.log("collided");
    bot = {};
  };

  var start = function(){
    socket = io.connect('/game');
    socket.on("connect",resumeGame);
    socket.on("init",setupGame);
    socket.on("botmove",botmoved);
    socket.on("collision",collision);
    // socket.on("message",messaged);
    socket.on("disconnect",disconnected);
    // pass method updateCycle as callback of the requestAnimationFrame function so, each frame, updateCycle will be evaluated
  };

  start();

});
