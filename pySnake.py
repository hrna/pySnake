import curses
import random
import traceback
from time import time

class SnakeGame():

    # TODO: Different kinds of foods with a different point value.
    # TODO: A big junk of food slows down the speed where smaller junks makes snake faster.
    # TODO: Timed junks of food, maybe even two junks at the same time.

    '''Input game area size as parameters, screen height comes first and then width
    3rd arg is for the speed. Lower the number, faster the snake is'''

    def __init__(self, screenHeigth, screenWidth, speed):
        
        # Taking in and setting some initial parameters
        self.screenHeigth = screenHeigth
        self.screenWidth = screenWidth
        self.speed = speed
        self.points = 0
        self.startTime = time()


    def endGame(self, message, debug = None):
        print(message)
        print(f"You survived {round(time()-self.startTime,2)} seconds")
        print(f"And scored {self.points} points.")
        
        if debug != None:
            print(debug)

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
        snake = [
            [y_position, x_position],
            [y_position, x_position - 1],
            [y_position, x_position - 2]
        ]

        # Creating the first food in the scene and paint it to canvas.
        food = [int(self.screenHeigth / 2), int(self.screenWidth / 2)]
        game.addch(int(food[0]), int(food[1]), "o")

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
            score.addstr(1, int(self.screenWidth/3), f"DEBUG: Pos: {snake[0]}, Speed: {self.speed}")
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
            if snake[0][0] in [0, self.screenHeigth-1] or snake[0][1] in [0, self.screenWidth-1]:
                curses.endwin()
                self.endGame("Snake hit the wall!", f"DEBUG: y: {snake[0][0]}, x: {snake[0][1]}")
                break
            elif snake[0] in snake[1:]:
                curses.endwin()
                self.endGame("Cannibalism is not good.", f"DEBUG: y: {snake[0][0]}, x: {snake[0][1]}")
                break

            # Add a block towards new direction
            # movement [Y,X]
            movement = [snake[0][0],snake[0][1]]

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
            snake.insert(0, movement)


            # -------------------------------------------------------------------
            # Check if food is consumed, if not pop the tail out.
            # IF consumed, create a new treat and let the snake grow
            if snake[0] == food:
                food = None

                while food is None:
                    newFood = [
                        int(random.randint(2,self.screenHeigth-2)),
                        int(random.randint(2,self.screenWidth-2))
                    ]

                    if newFood not in snake[0]:
                        food = newFood
                    else:
                        food = None
                game.addch(int(food[0]),int(food[1]), "o")

                # Get yourself a meal, add a point and lower the timout value for higher speed after every 5th food.
                self.points += 1
                if self.points % 5 == 0:
                    self.speed -= 1

                # Debugging (this method worked on windows but not on linux)
                #print(f"DEBUG: Food eaten ({self.points}) @ {snake[0]}, Time: {round(time()-self.startTime,2)}")

            else:
                # Getting rid of the tail bits
                tail = snake.pop()
                game.addch(int(tail[0]),int(tail[1]), " ")
            # -------------------------------------------------------------------


            # Bring the snake alive
            game.addch(int(snake[0][0]),int(snake[0][1]), curses.ACS_BULLET)

            # Debugging (this method worked on windows but not on linux)
            #print(f"DEBUG: Pos: {snake[0]}, Speed: {self.speed}, Time: {round(time()-self.startTime,2)}")

snake = SnakeGame(20,75,100)

try:
    curses.wrapper(snake.game)
except Exception as e:
    print(traceback.format_exc())
