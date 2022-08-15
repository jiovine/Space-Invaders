"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in
the Alien Invaders game.  Instances of Wave represent a single wave. Whenever 
you move to a new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on 
screen. These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or 
models.py. Whether a helper method belongs in this module or models.py is 
often a complicated issue.  If you do not know, ask on Piazza and we will 
answer.

# YOUR NAME(S) AND NETID(S) HERE
# DATE COMPLETED HERE
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not 
# permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.
    
    This subcontroller has a reference to the ship, aliens, and any laser bolts 
    on screen. It animates the laser bolts, removing any aliens as necessary. 
    It also marches the aliens back and forth across the screen until they are 
    all destroyed or they reach the defense line (at which point the player 
    loses). When the wave is complete, you  should create a NEW instance of 
    Wave (in Invaders) if you want to make a new wave of aliens.
    
    If you want to pause the game, tell this controller to draw, but do not 
    update.  See subcontrollers.py from Lecture 24 for an example.  This 
    class will be similar to than one in how it interacts with the main class 
    Invaders.
    
    All of the attributes of this class ar to be hidden. You may find that 
    you want to access an attribute in class Invaders. It is okay if you do, 
    but you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter 
    and/or setter for any attribute that you need to access in Invaders.  
    Only add the getters and setters that you need for Invaders. You can keep 
    everything else hidden.
    
    """
    # HIDDEN ATTRIBUTES:
    # Attribute _ship: the player ship to control 
    # Invariant: _ship is a Ship object or None
    #
    # Attribute _aliens: the 2d list of aliens in the wave 
    # Invariant: _aliens is a rectangular 2d list containing Alien objects or None 
    #
    # Attribute _bolts: the laser bolts currently on screen 
    # Invariant: _bolts is a list of Bolt objects, possibly empty
    #
    # Attribute _dline: the defensive line being protected 
    # Invariant : _dline is a GPath object
    #
    # Attribute _lives: the number of lives left
    # Invariant: _lives is an int >= 0
    #
    # Attribute _time: the amount of time since the last Alien "step" 
    # Invariant: _time is a float >= 0s
    #
    # You may change any attribute above, as long as you update the invariant
    # You may also add any new attributes as long as you document them.
    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY

    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getPause(self):
        return self._pause
    
    def setPause(self, value):
        self._pause = value

    def getLives(self):
        return self._lives

    def setLives(self):
        self._lives = SHIP_LIVES

    def getVictory(self):
        return self._victory

    def setVictory(self):
        self._victory = True

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        self._aliens = self.createAliens()
        self._ship = Ship()
        self._dline = GPath(points=[0, DEFENSE_LINE, GAME_WIDTH, DEFENSE_LINE], linewidth=2, linecolor='black')
        self._time=0
        self._direction = 0
        self._bolts=[]
        self._aliensteps = 0
        self._alienboltrate = random.randint(1, BOLT_RATE)
        self._pause = 0
        self._lives = SHIP_LIVES
        self._victory = False
        

    def createAliens(self):
        self._aliens =[]
        left = (ALIEN_H_SEP+(0.5*ALIEN_WIDTH))
        top = GAME_HEIGHT-ALIEN_CEILING
        aliens_height=((ALIEN_ROWS-1)*ALIEN_V_SEP)+(ALIEN_ROWS+ALIEN_HEIGHT)
        bottom=(top-aliens_height)+(0.5*ALIEN_HEIGHT)
        for col in range(ALIENS_IN_ROW):
            subset = []
            for row in range(ALIEN_ROWS):
                rem=row%6
                if rem <= 1:
                    source= ALIEN_IMAGES[0]
                elif rem <= 3:
                    source = ALIEN_IMAGES[1]
                else:
                    source = ALIEN_IMAGES[2]
                subset.append(Alien(left+(ALIEN_WIDTH+ALIEN_H_SEP)*col,bottom+(ALIEN_HEIGHT+ALIEN_V_SEP)*row,source)) 
            self._aliens.append(subset)
        return self._aliens

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self, input, dt):
        if self._ship:
            self._updateShip(input)
        self._moveAliens(dt)
        self._time+=dt
        if (input.is_key_down('spacebar') or input.is_key_down('up')) and self._playerBoltCount():
            self._bolts.append(Bolt(self._ship.x, SHIP_BOTTOM+SHIP_HEIGHT+BOLT_HEIGHT//2, 1, 'black'))
        self._alienBolts()
        self._moveBolts()
        self._alienCollision()
        self._shipCollision()
        if self._aliensDefeated():
            self._victory = True


    
    def _updateShip(self, input):
        if input.is_key_down('left') and self._ship.x > SHIP_WIDTH//2:
            self._ship.x-=SHIP_MOVEMENT
        if input.is_key_down('right') and self._ship.x < GAME_WIDTH-(SHIP_WIDTH//2):
            self._ship.x+=SHIP_MOVEMENT
        
    def _moveAliens(self, dt):
        if self._time > ALIEN_SPEED:

            future_pos = 0
            if self._direction == 0:
                for row in self._aliens:
                    for alien in row:
                        if alien:
                            future_pos = alien.x+ALIEN_H_WALK
                            if future_pos < GAME_WIDTH-(ALIEN_WIDTH//2+ALIEN_H_SEP):
                                alien.x+=ALIEN_H_WALK
                            else:
                                for row in self._aliens:
                                    for alien in row:
                                        if alien:
                                            alien.y-=ALIEN_V_WALK
                                self._direction = 1

            if self._direction == 1:
                for row in self._aliens:
                    for alien in row:
                        if alien:
                            if alien.x > (ALIEN_WIDTH//2+ALIEN_H_SEP):
                                alien.x-=ALIEN_H_WALK
                            else:
                                for row in self._aliens:
                                    for alien in row:
                                        if alien:
                                            alien.y-=ALIEN_V_WALK
                                self._direction = 0
            self._time = 0
            self._aliensteps+=1
    
    def _alienBolts(self):
        if self._aliensteps > self._alienboltrate:
            rand_col = random.randint(0, len(self._aliens)-1)
            if self._aliens[rand_col].count(None) != len(self._aliens[rand_col]):
                for n in range(len(self._aliens[rand_col])):
                    alien = self._aliens[rand_col][n]
                    if alien:
                        last_alien = alien
                        break
                self._bolts.append(Bolt(last_alien.x, last_alien.y-ALIEN_HEIGHT//2-BOLT_HEIGHT//2, -1, 'red'))
            self._aliensteps = 0
            self._alienboltrate = random.randint(1, BOLT_RATE)

        
    def _moveBolts(self):
        for bolt in self._bolts:
            if bolt.isPlayerBolt():
                bolt.y+=BOLT_SPEED
                if bolt.y-(BOLT_HEIGHT//2) > GAME_HEIGHT:
                    self._bolts.remove(bolt)
            else:
                bolt.y-=BOLT_SPEED

    def _playerBoltCount(self):
        for bolt in self._bolts:
            if bolt.isPlayerBolt():
                return False
        return True

    def _alienCollision(self):
        for row in range(len(self._aliens)):
            for col in range(len(self._aliens[row])):
                alien = self._aliens[row][col]
                for bolt in self._bolts:
                    if alien and alien.collides(bolt):
                        self._aliens[row][col] = None
                        self._bolts.remove(bolt)

    def _shipCollision(self):
        for bolt in self._bolts:
            if not bolt.isPlayerBolt() and self._ship.collides(bolt):
                self._ship = Ship()
                self._bolts.clear()
                self._lives-=1
                self._pause = 1

    def _aliensDefeated(self):
        for row in self._aliens:
            for alien in row:
                if alien:
                    return False
        return True



    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        self._drawAliens(view)
        if self._ship:
            self._ship.draw(view)
        self._dline.draw(view)
        self._drawBolts(view)

    def _drawAliens(self, view):
        """ Draws aliens """
        for col in range(len(self._aliens[0])):
            for row in range(len(self._aliens)):
                alien = self._aliens[row][col]
                if alien:
                    alien.draw(view)
    
    def _drawBolts(self, view):
        for bolt in self._bolts:
            if bolt:
                bolt.draw(view)

    # HELPER METHODS FOR COLLISION DETECTION