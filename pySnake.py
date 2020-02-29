import curses
import random
import traceback
from time import time

class SnakeGame():
    '''Input game area size as parameters, screen height comes first and then width
    3rd arg is for the speed. Lower the number, faster the snake is'''

    def __init__(self, screenHeigth, screenWidth, speed):
        
        # Taking in and setting some initial parameters
        self.screenHeigth = screenHeigth
        self.screenWidth = screenWidth
        self.speed = speed
        self.points = 0
        self.startTime = time()
        self.snake = []


    def endGame(self, message, debug = None):
        print(message)
        print(f"You survived {round(time()-self.startTime,2)} seconds")
        print(f"And scored {self.points} points.")
        
        if debug != None:
            print(debug)

    def processFood(self):
        # Create a new treat for snake        
        food = None
        while food is None:
           
            newFood = [
                int(random.randint(2,self.screenHeigth-2)),
                int(random.randint(2,self.screenWidth-2))              
                ]

            if newFood not in self.snake[0]:
                food = newFood
            else:
                food = None
        return food

    def game(self, screen):

        # Initializing the screen and set cursor hidden.
        s = curses.initscr()
        s.clear()
        curses.curs_set(0)

        # Create a game main window with borders
        game = curses.newwin(self.screenHeigth, self.screenWidth, 0, 0)
        game.border()

        # Create a window for scores
        score = curses.newwin(4, self.screenWidth, self.screenHeigth, 0)
        score.border()

        #get screen max values for screen size checkup
        sh, sw = s.getmaxyx()
   
        # Activate keypad/arrow keys
        game.keypad(True)

        # Controlling the snake speed by setting the time out in ms
        # lower the time out -> faster the snake is
        # Updating the timeout value in the game main loop
        game.timeout(self.speed)

        # Setting starting coordinates for snake
        y_position = int(self.screenHeigth / 2)
        x_position = int(self.screenWidth / 4)

        # Creating a list holding the snake
        # Giving the snake 3 blocks, snake[0][0] will always be the snake head and the rest will come behind.
        self.snake = [
            [y_position, x_position],
            [y_position, x_position - 1],
            [y_position, x_position - 2]
        ]

        # Creating the first food in the scene and paint it to canvas.
        foodTypes = ["o", "O","@"]
        insertFood = foodTypes[0]
        food = [int(self.screenHeigth / 2), int(self.screenWidth / 2)]
        game.addch(int(food[0]), int(food[1]), insertFood)

        # Set the default starting direction
        key = curses.KEY_RIGHT

        while (True):

            # End game if the screen is smaller than the main game area (excluding scoreboard)
            if self.screenHeigth > sh or self.screenWidth > sw:
                curses.endwin()
                print("Terminal window must be at least as big as the main game area")
                print(f"minimum height: {self.screenHeigth}, width: {self.screenWidth}")
                break

            # Add some content to scoreboard
            score.addstr(1,1,f"Points: {self.points}")
            score.addstr(2,1,f"Next Food: {food}")

            # Debug information displayed at score window
            score.addstr(1, int(self.screenWidth/3), f"DEBUG: Pos: {self.snake[0]}, Speed: {self.speed}")
            score.addstr(2, int(self.screenWidth/3), f"DEBUG: Width: {self.screenWidth-1}, Time: {round(time()-self.startTime,2)}")
            scoreUpdate = score.refresh()

            # Updating the timeout value
            game.timeout(self.speed)

            # 258 down, 259 up, 260 left, 261 right, 10 enter
            allowedKeys = [258, 259, 260, 261]
            update = game.getch()

            if update in allowedKeys:
                key = update
            else:
                key = key
            
            # If snake is out of bounds in Y / X axis or snake is in itself, quit
            # snake[0][0] = Y, snake[0][1] = X
            if self.snake[0][0] in [0, self.screenHeigth-1] or self.snake[0][1] in [0, self.screenWidth-1]:
                curses.endwin()
                self.endGame("Snake hit the wall!", f"DEBUG: y: {self.snake[0][0]}, x: {self.snake[0][1]}, speed: {self.speed}")
                break
            elif self.snake[0] in self.snake[1:]:
                curses.endwin()
                self.endGame("Cannibalism is not good.", f"DEBUG: y: {self.snake[0][0]}, x: {self.snake[0][1]}, speed: {self.speed}")
                break

            # Add a block towards new direction
            # movement [Y,X]
            movement = [self.snake[0][0],self.snake[0][1]]

            # If moving up or down direction, we are manipulating Y axis.
            if key == curses.KEY_DOWN:
                movement[0] += 1
            if key == curses.KEY_UP:
                movement[0] -= 1

            # If moving left or right, we have to modify X axis.
            if key == curses.KEY_LEFT:
                movement[1] -= 1
            if key == curses.KEY_RIGHT:
                movement[1] += 1
            
            # Inserting a new block towards the direction of movement.
            self.snake.insert(0, movement)


            # Check if food is consumed, if not pop the tail out.
            # IF consumed, create a new treat and let the snake grow          
            if self.snake[0] == food: 

                # Get yourself a meal, add a point
                if insertFood == foodTypes[0]:
                    self.points += 1     

                # Bigger the meal is, slower the snake gets                 
                elif insertFood == foodTypes[1]:
                    self.points += 3
                    self.speed += 1

                elif insertFood == foodTypes[2]:
                    self.points += 5
                    self.speed += 2

                # Lower the timout value for higher speed after every food.
                self.speed -= 1

                insertFood = foodTypes[random.randint(0,len(foodTypes)-1)]
                food = self.processFood()
                game.addch(int(food[0]),int(food[1]),insertFood)
            else:
                # Getting rid of the tail bits
                tail = self.snake.pop()
                game.addch(int(tail[0]),int(tail[1]), " ")
               
            # Bring the snake alive
            game.addch(int(self.snake[0][0]),int(self.snake[0][1]), curses.ACS_BULLET)

            # Debugging (this method worked on windows but not on linux)
            #print(f"DEBUG: Pos: {snake[0]}, Speed: {self.speed}, Time: {round(time()-self.startTime,2)}")

snake = SnakeGame(20,75,100)

try:
    curses.wrapper(snake.game)
except Exception as e:
    print(traceback.format_exc())
