import tkinter 
import pygame, os
import sys

window_width = 500
window_height = 500

window = pygame.display.set_mode((window_width,window_height))
os.environ['SDL_VIDEO_CENTERED'] = '1'


columns = 25
rows = 25

box_width = window_width // columns
box_height = window_height // rows

grid = []  # Will store every box object
queue = []  # Stores every box that we need to visit
path = []

class Box:
    def __init__(self, i, j):  # i and j will tell us the position of the box
        self.x = i
        self.y = j

        # flags
        self.start = False  # Set to true if box is the starting box
        self.wall = False  # Set to true if box is a wall
        self.target = False  # Set to true if the box is our target
        self.queued = False
        self.visited = False

        self.neighbours = []
        self.prior = None

    def draw(self, win, color):
        pygame.draw.rect(win, color, (self.x*box_width, self.y*box_height, box_width - 2, box_height - 2))  # Subtracting two pixels
    
    def set_neighbours(self):
        # Appending the boxes horizontally adjacent to the current box to the neighbours array
        if self.x > 0:
            self.neighbours.append(grid[self.x - 1][self.y])
        if self.x < columns - 1:
            self.neighbours.append(grid[self.x + 1][self.y])

        # Appending the boxes vertically adjacent 
        if self.y > 0:
            self.neighbours.append(grid[self.x][self.y - 1])
        if self.y < rows - 1:
            self.neighbours.append(grid[self.x][self.y + 1])

for i in range(columns):
    arr = []
    for j in range(rows):
        arr.append(Box(i, j))
    grid.append(arr)

for i in range(columns):
    for j in range(rows):
        grid[i][j].set_neighbours()

def restart():
    path.clear()
    queue.clear()

    for i in range(columns):
        for j in range(rows):
            box = grid[i][j]
            box.start = False
            box.target = False
            box.wall = False
            box.queued = False
            box.visited = False
            box = None

    main(columns,rows)

# prompts user to either quit or restart the program after search algorithm finishes 
def restart_dialog():
    root = tkinter.Tk()
    root.withdraw()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    dialog_width = 250
    dialog_height = 100
    x = (screen_width - dialog_width) // 2 # center line of the screen

    dialog = tkinter.Toplevel(root)
    dialog.title("Restart")
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{0}")

    label = tkinter.Label(dialog, text="Would you like to restart?")
    label.pack(pady=10)

    def on_ok():
        dialog.destroy()  # Close the dialog
        restart()  # Restart the program

    def on_cancel():
        dialog.destroy()
        pygame.quit()
        sys.exit()

    ok_button = tkinter.Button(dialog, text="Restart", command=on_ok)
    ok_button.pack(side=tkinter.LEFT, padx=10)

    cancel_button = tkinter.Button(dialog, text="Quit", command=on_cancel)
    cancel_button.pack(side=tkinter.RIGHT, padx=10)

    root.mainloop()

def main(columns, rows):
    begin_search = False
    target_box_set = False
    searching = True
    target_box = None
    start_box = Box  
    start_box.start = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:  # Capturing the mouse position to create walls
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]
                if event.buttons[0]:  # Whenever the left mouse button is pressed
                    i = x // box_width
                    j = y // box_height
                    grid[i][j].wall = True
                if event.buttons[2] and not target_box_set:  # If the right mouse button is pressed
                    i = x // box_width
                    j = y // box_height
                    target_box = grid[i][j]
                    target_box.target = True
                    target_box_set = True
                if pygame.key.get_pressed()[pygame.K_s]:
                    if not start_box.start:  # Make sure that the user cannot draw more than one starting box
                        i = x // box_width
                        j = y // box_height
                        start_box = grid[i][j]
                        start_box.start = True
                        start_box.visited = True
                        queue.append(start_box)

            # Start algorithm
            if pygame.key.get_pressed()[pygame.K_SPACE] and target_box_set: # make sure that we are pressing space and the target_box is set before we begin searching
                begin_search = True

        if begin_search:
            if len(queue) > 0 and searching:  # Ensure queue is greater than zero
                current_box = queue.pop(0)
                current_box.visited = True
                if current_box == target_box: 
                    searching = False
                    while current_box.prior != start_box:
                        path.append(current_box.prior)
                        current_box = current_box.prior
                    
                    path.reverse()

                    # Visualize the path
                    for box in path:
                        box.draw(window, (0, 0, 200))
                        pygame.display.flip()  # Update display
                        pygame.time.delay(70) # delay draw method by 70 ms. Better than using time.sleep, as it blocks the main thread     
                    searching = False    
                    begin_search = False

                    restart_dialog()
                else:
                    for neighbour in current_box.neighbours:  # If neighbour box is not a wall and not already queued
                        if not neighbour.queued and not neighbour.wall:
                            neighbour.queued = True
                            neighbour.prior = current_box
                            queue.append(neighbour)
            else:  # If queue is zero, no solution
                if searching and (start_box.start):                    
                    searching = False
                    restart_dialog()
                    

        window.fill((0, 0, 0))  # Fill before drawing our boxes

        for i in range(columns):  # Draw every box
            for j in range(rows):
                box = grid[i][j]
                box.draw(window, (50, 50, 50))

                if box.queued:
                    box.draw(window, (200, 0, 0))
                if box.visited:
                    box.draw(window, (0, 200, 0))  

                if box.start:
                    box.draw(window, (0, 200, 200))
                if box.wall:
                    box.draw(window, (90, 90, 90))
                if box.target:
                    box.draw(window, (200, 200, 0))
        if searching:
            pygame.display.flip()  # Display flip method. Updates the display if searching is true

main(columns, rows)