import pygame
from math import ceil, floor, sin, pi

# Initialises simulation by calculating values and setting defaults
def initialise(dim, cellSize):
    dimMachine = dim                                # Simulation window dimensions
    centreMachine = (dim[0]//2, 4*dim[1]//5)        # Calculate center of the machine

    display = pygame.display.set_mode(dim)          # Initialise display
    clock = pygame.time.Clock()                     # Initialise clock

    ITcentre = (4*dim[0]//5, dim[1]//3)             # Calculate instruction table center
    ITwidth = dim[0]//3                             # Calculate instruction table center
    ITheight = dim[1]//2                            # Calculate instruction table height

    ITrowHeight = ITwidth/8                         # Calculate instruction table row height

    tapeFonts = generateTapeFonts(cellSize)         # Generate tape fonts
    tableFonts = generateTableFonts(ITrowHeight)    # Generate instruction table fonts
    fonts = {                                       # Compile fonts dictionary
    'detail':tapeFonts['detail'],
    'cell':tapeFonts['cell'],
    'table1':tableFonts['table1'],
    'table2':tableFonts['table2'],
    }

    palette = {'bg':(240, 240, 240), 'main':(0, 0, 0), 'error':(255, 0, 0),     # Colour palette
    'accept':(0, 255, 0), 'state':(255, 255, 255), 'secondary':(200, 200, 200)}

    # Output dictionary
    sim = {
    'display':display,
    'clock':clock,
    'fonts':fonts,
    'palette':palette,
    'dimMachine':dimMachine,
    'centreMachine':centreMachine,
    'ITcentre':ITcentre,
    'ITwidth':ITwidth,
    'ITheight':ITheight,
    'ITrowHeight':ITrowHeight
    }

    return sim

# Generates the tape fonts based on the size of the tape's cells
def generateTapeFonts(cellSize):
    return {
    'detail':pygame.font.SysFont('consolas', 20*cellSize//80, True),
    'cell':pygame.font.SysFont('consolas', 40*cellSize//70, True)
    }

# Generates the instruction table fonts based on the height of the instruction table's rows
def generateTableFonts(rowHeight):
    rowHeight = round(rowHeight)
    return {
    'table1':pygame.font.SysFont('consolas', 4*rowHeight//5, True),
    'table2':pygame.font.SysFont('consolas', rowHeight//2, True)
    }

# Instructions class - acts as a lookup table for machine instructions
class Instructions:
    def __init__(self, instructions):
        # Initialise instruction dictionary
        self.instructions = {}

        # Add an entry for each instruction in the given list of instructions
        for n, i in enumerate(instructions):
            self.setInstruction(i[0], i[1], i[2], i[3], i[4], n)

    # Adds an entry for the given instruction
    def setInstruction(self, state, read, written, direction, next, index):
        stateSet = self.instructions.get(state)             # Try to get the inner dictionary that represents the given current state
        if stateSet is None:                                # If dictionary does not yet exist:
            stateSet = {}                                   # Create the dictionary
            self.instructions[state] = stateSet             # Create new entry in outer dictionary for the new dictionary

        stateSet[read] = (written, direction, next, index)  # Create a new entry in the inner dictionary for the given read character

    # Lookup function - returns the write character, move direction and next
    # state for the given current state and read character
    def getInstruction(self, state, read):
        stateSet = self.instructions.get(state)     # Try to get the inner dictionary for the current state
        if stateSet is None:                        # If the inner dictionary does not exist:
            return None

        return stateSet.get(read)                   # Return the instruction information (returns none if there is no defined
                                                    # instruction for the given current state and read character)

# Tape class - handles reading from and writing to the tape
class Tape:
    def __init__(self, blank, definition={}):
        self.blank = blank              # Set blank character
        self.definition = definition    # Set the dictionary that stores the values of (non-blank) cells

    # Gets the value of the cell at the given position (returns NoneType if cell is blank)
    def get(self, pos):
        char = self.definition.get(str(pos))

        return char

    # Sets the value of the cell at the given position to the given value
    def set(self, pos, char):
        self.definition[str(pos)] = char

    # Returns the string that represents a blank cell
    def getBlank(self):
        return self.blank

# Machine class - Handles animation, execution and Turing Machine logic
class Machine:
    def __init__(self, instructions, tape, startState, acceptStates, startPos, palette, instructionTable, speed=1):
        # Initialise internal attributes
        self.instructions = instructions            # Instructions object
        self.tape = tape                            # Tape object
        self.state = startState
        self.acceptStates = acceptStates            # List of accept states
        self.pos = startPos
        self.instructionTable = instructionTable    # Instruction table object

        self.direction = None                       # The direction that the head is going to move
        self.written = None                         # The string that the head is going to write
        self.next = None                            # The next state that the machine is going to enter
        self.instructionIndex = None                # The index of the instruction currently being executed
        self.running = True                         # False once the machine enters an accept state (or crashes)

        self.speed = speed                          # Speed of animation
        self.phase = 0                              # The current phase of animation
        self.animating = None                       # Stores a code for which animation is currently ongoing
                                                    # w: writing, m: moving, hd: head down, hu: head up, i: changing instruction

        self.colour = palette['main']               # Set head colour to default colour
        self.phaseCtr = 0                           # Stores how many more parts of a step the machine has to execute (-1 if runnung continuously)

        self.anim = {                               # Animation parameters - keeps track of how things should look at any given time
        'tapeOffset': 0,
        'headOffset': 0,
        'headDown': False,
        'charOffset': 0,
        'instructionTableOffset': 0
        }

    # Nudge the tape to continue execution
    def nudge(self, mode):
        if mode == 'one':                       # Just do one part of a step
            self.phaseCtr += 1
        elif mode == 'full':                    # Do one full step (or finish current step)
            self.phaseCtr += 5 - self.phase
        elif mode == 'go':                      # Run continuously
            self.phaseCtr = -1

    # Machine ready for next operation?
    def isStandby(self):
        return self.phaseCtr == 0 and self.running and not self.animating

    # Actually writes value to tape
    def writeAct(self):
        self.tape.set(self.pos, self.written)

    # Calculate animation parameters for the next frame of write animation
    def writeAnim(self, char):
        charOffset = self.anim['charOffset']                                # Get character offset parameter
        charOffset += (0.005 + 0.05 * sin(charOffset*pi)) * self.speed      # Increment parameter

        if charOffset >= 1:                         # If animation has finished:
            self.animating = None                   # Update flag
            self.anim['charOffset'] = 0             # Initialise parameter
            self.writeAct()                         # Actually update the tape
        else:
            self.anim['charOffset'] = charOffset    # Set parameter

    # Called each tick that the machine is writing to the tape
    def write(self, char, animate=True):
        if animate:                                 # If we are animating the write action:
            if self.animating is None:              # If we are not already animating:
                if char is None:                    # If the given character is the blank character:
                    char = self.tape.getBlank()     # Get the blank character
                self.animating = 'w' + char         # Set animating code
        else:                                       # Otherwise, skip straight to actually updating the tape
            self.writeAct()

    # Actually moves the head across the tape
    def moveHeadAct(self, direction):
        self.pos += {'l':-1, 'r':1}[direction]  # Increment or decrement head position

    # Calculate animation parameters for the next frame of move head animation
    def moveHeadAnim(self, direction):
        tapeOffset = self.anim['tapeOffset']                                                                    # Get tape offset parameter
        tapeOffset += ({'l':1, 'r':-1}[direction]) * (0.005 + 0.05 * sin(abs(tapeOffset)*pi)) * self.speed      # Increment parameter

        if abs(tapeOffset) >= 1:                    # If animation has finished:
            self.animating = None                   # Update flag
            self.anim['tapeOffset'] = 0             # Initialise parameter
            self.moveHeadAct(direction)             # Actually move the head
        else:
            self.anim['tapeOffset'] = tapeOffset    # Set parameter

    # Called each tick that the machine is moving the head across the tape
    def moveHead(self, direction, animate=True):
        if animate:                                 # If we are animating the move head action:
            if self.animating is None:              # If we are not already animating:
                self.animating = 'm' + direction    # Set animating code
        else:                                       # Otherwise, skip straight to actually moving the head
            self.moveHeadAct(direction)

    # Calculate animation parameters for the next frame of head down animation
    def headDownAnim(self):
        headOffset = self.anim['headOffset']                            # Get head offset parameter
        headOffset += (0.005 + 0.05 * sin(headOffset*pi)) * self.speed  # Increment parameter

        if headOffset >= 1:                         # If animation has finished:
            self.animating = None                   # Update flag
            self.anim['headOffset'] = 1             # Force parameter to clean value
            self.anim['headDown'] = True            # Update head down parameter
        else:
            self.anim['headOffset'] = headOffset    # Set parameter

    # Called each tick that the head is moving down
    def headDown(self):
        if self.animating is None and not self.anim['headDown']:    # If not already animating and the head is up:
            self.animating = 'hd'                                   # Set the animating code

    # Calculate animation parameters for the next frame of head up animation
    def headUpAnim(self):
        headOffset = self.anim['headOffset']                                    # Get head offset parameter
        headOffset -= (0.005 + 0.05 * sin(abs(headOffset)*pi)) * self.speed     # Increment parameter

        if headOffset <= 0:                         # If animation has finished:
            self.animating = None                   # Update flag
            self.anim['headOffset'] = 0             # Force parameter to clean value
            self.anim['headDown'] = False           # Update head down parameter
        else:
            self.anim['headOffset'] = headOffset    # Set parameter

    # Called each tick that the head is moving up
    def headUp(self):
        if self.animating is None and self.anim['headDown']:    # If not already animating and the head is up:
            self.animating = 'hu'                               # Set the animating code

    # Actually updates the instruction table's current index
    def moveInstructionTableAct(self, instructionIndex):
        self.instructionTable.currentIndex = instructionIndex

    # Calculate animation parameters for the next frame of move instruction table pointer animation
    def moveInstructionTableAnim(self, instructionIndex):
        instructionTableOffset = self.anim['instructionTableOffset']                                    # Get instruction table offset parameter
        instructionTableOffset += (0.005 + 0.05 * sin(abs(instructionTableOffset)*pi)) * self.speed     # Increment parameter

        if instructionTableOffset >= 1:                                     # If animation has finished:
            self.animating = None                                           # Update flag
            self.anim['instructionTableOffset'] = 0                         # Force parameter to clean value
            self.moveInstructionTableAct(instructionIndex)                  # Actually update the instruction table
        else:
            self.anim['instructionTableOffset'] = instructionTableOffset    # Set parameter

    # Called each tick that the instruction table pointer is moving
    def moveInstructionTable(self, instructionIndex, animate=True):
        if animate:                                             # If we are animating the move instruction table pointer action:
            if self.animating is None:                          # If we are not already animating:
                self.animating = 'i' + str(instructionIndex)    # Set animating code
        else:                                                   # Otherwise, skip straight to actually updating the instruction table
            self.moveInstructionTableAct(instructionIndex)

    # Draws the machine, tape and instruction table onto the display
    def draw(self, display, fonts, palette, dim, centre, cellSize, drawDetail=False):
        # = Instruction Table =
        self.instructionTable.draw(display, fonts, palette, self.instructionIndex, self.anim['instructionTableOffset'])

        midX = centre[0]
        midY = centre[1]

        # = Tape =
        offset = self.anim['tapeOffset']                    # Get tape offset parameter
        pOffset = offset * cellSize                         # Calculate the actual offset in pixels
        truePos = self.pos - offset                         # Calculate the true positin of the read/write head for this frame of animation
        sideCells = ceil((dim[0]/cellSize - 1) / 2) + 1     # Calculate the number of cells either side of the central one that must be drawn

        # For each cell that must be drawn:
        for c in range(-sideCells, sideCells+1):
            x = midX + c*cellSize   # Calculate the x coordinate of the center of the current cell
            # Cell border
            pygame.draw.rect(display, palette['main'], (x-cellSize//2 + pOffset, midY-cellSize//2, cellSize, cellSize), 1)

            p = c + self.pos                    # Get the tape position of the current cell
            char = self.tape.get(p)             # Get the character at this cell
            if char is None:                    # If the blank character:
                char = self.tape.getBlank()     # Get the blank character

            # If in the middle of the write animation the current cell is the middle one:
            if c == 0 and not self.animating is None and self.animating[0] == 'w':
                written = self.animating[1:]            # Get value currently being written
                charOffset = self.anim['charOffset']    # Get character offset parameter
                pCharOffset = charOffset * cellSize     # Calculate the actual offset in pixels

                # Draw the character that is being overwritten
                drawCentredText(display, char, fonts['cell'], palette['main'], (x + pOffset, midY + pCharOffset))
                # Draw the new character
                drawCentredText(display, written, fonts['cell'], palette['main'], (x + pOffset, midY - cellSize + pCharOffset))

                # Masks to hide characters as they fall off of and on to tape
                pygame.draw.rect(display, palette['bg'], (x-cellSize//2 + pOffset, floor(midY-3*cellSize/2), cellSize, cellSize))
                pygame.draw.rect(display, palette['bg'], (x-cellSize//2 + pOffset, ceil(midY+cellSize/2), cellSize, cellSize))

            else:
                # Draw the character at the cell
                drawCentredText(display, char, fonts['cell'], palette['main'], (x + pOffset, midY))

            # If drawing extra detail:
            if drawDetail:
                # Draw the cell position label
                drawCentredText(display, str(p), fonts['detail'], palette['main'], (x + pOffset, midY+ 2*cellSize//3))

        # = Read/Write Head =
        offset = self.anim['headOffset']                # Get head offset parameter
        pOffset = offset * cellSize//4                  # Calculate the actual offset in pixels
        arrowTop = midY - 5*cellSize//4 + pOffset       # Calculate the y coordinate of the top of the arrow
        arrowBottom = midY - 3*cellSize//4 + pOffset    # Calculate the y coordinate of the bottom of the arrow
        arrowMiddle = (2*arrowTop+arrowBottom)//3       # Calculate the y coordinate of the middle of the arrow

        # Draw the arrow
        pygame.draw.polygon(display, self.colour, ((midX, arrowBottom), (midX-cellSize//2, arrowTop), (midX+cellSize//2, arrowTop)))
        # If drawing extra detail:
        if drawDetail:
            # Draw the current state label
            drawCentredText(display, str(self.state), fonts['detail'], palette['state'], (midX, arrowMiddle))

    # Called when the machine is in the middle of an animation
    # Handles which animation should be processed
    def animate(self):
        # = Moving head across =
        if self.animating[0] == 'm':
            direction = self.animating[1]           # Read direction of motion
            self.moveHeadAnim(direction)            # Do next frame of animation

        # = Moving head up/down =
        elif self.animating[0] == 'h':
            direction = self.animating[1]           # Read direction of motion
            # Down
            if direction == 'd':
                self.headDownAnim()                 # Do next frame of animation
            # Up
            elif direction == 'u':
                self.headUpAnim()                   # Do next frame of animation

        # = Writing =
        elif self.animating[0] == 'w':
            char = self.animating[1:]               # Read character being written
            self.writeAnim(char)                    # Do next frame of animation

        # = Changing instruction =
        elif self.animating[0] == 'i':
            index = int(self.animating[1:])         # Read index of new instruction
            self.moveInstructionTableAnim(index)    # Do next frame of animation

    # Updates the simulation
    def update(self, palette):
        # If animating:
        if not self.animating is None:
            self.animate()

        # If (not animating and running) and (phase counter indicates that the tape must perform an operation):
        elif self.running and self.phaseCtr != 0:
            # = Head Down =
            if self.phase == 0:
                self.headDown()

            # = Read =
            elif self.phase == 1:
                cell = self.tape.get(self.pos)                                      # Read the current cell's value
                instruction = self.instructions.getInstruction(self.state, cell)    # Get the instruction

                # If transition not defined:
                if instruction is None:
                    self.colour = palette['error']  # Change head's colour
                    self.running = False            # Stop running
                    return

                written, direction, next, index = instruction   # Parse instruction

                # Update internal attributes
                self.next = next
                self.direction = direction
                self.written = written
                self.instructionIndex = index

                self.moveInstructionTable(index)

            # = Write =
            elif self.phase == 2:
                self.instructionIndex = None    # Reset instruction index attribute

                self.write(self.written)

            # = Change State & Head Up =
            elif self.phase == 3:
                self.written = None         # Reset string currently being written attribute
                self.state = self.next      # Update internal state

                #If reached an accept state:
                if self.state in self.acceptStates:
                    self.colour = palette['accept']     # Change head's colour
                    self.running = False                # Stop running

                self.next = None            # Reset next state attribute
                self.headUp()

            # = Move Tape =
            elif self.phase == 4:
                self.moveHead(self.direction)
                self.direction = None                   # Reset direction attribure

                if self.state in self.acceptStates:     # If reached an accept state:
                    self.running = False                # Stop running

            self.phase = (self.phase+1) % 5             # Increment phase

            # Decrement phase counter (if possible)
            if self.phaseCtr > 0:
                self.phaseCtr -= 1

        # Automatically progress from phase 0 to phase 1 as reading the head is actually just a two-part animation
        elif self.running and self.phase == 1:
            self.phaseCtr += 1

    # Gets the current status of the machine
    def getStatus(self):
        if not self.running:
            return 'stopped'

        # If the machine is in the middle of an animation
        # Or the machine is partway through a step which it must complete
        # Or the machine is halfway through the reading animation:
        if self.animating or self.phaseCtr != 0 or self.phase == 1:
            return 'playing'

        return 'standby'    # Machine is waiting for a nudge

# Instruction Table class - handles the graphics and animation of the instruction table
class InstructionTable:
    def __init__(self, instructions, blankChar, centre, width, height, rowHeight):
        self.instructions = instructions            # List of instructions
        self.numInstructions = len(instructions)    # Number of instructions
        self.blankChar = blankChar                  # Blank cell string
        self.centre = centre                        # Centre coordinate of instruction table
        self.width = width                          # Width of the table
        self.height = height                        # Height of the table
        self.rowHeight = rowHeight                  # Height of each row

        self.currentIndex = -1                      # Current instruction index (-1 means at the resting position)

    # Get the
    def getDrawOffsets(self, index):
        height = self.height                            # Table height
        rowHeight = self.rowHeight                      # Table row height
        top = self.centre[1] - height//2                # Top of table y coordinate
        bottom = self.centre[1] + height//2             # Bottom of table y coordinate
        fullHeight = rowHeight * self.numInstructions   # Height that table would be if it was all visible at once (excluding the header row)
        viewHeight = height-rowHeight                   # Height of the viewing region of the table (excluding the header row)

        topScroll = top + height/2 - (index*rowHeight)  # Calculate y coordinate of where the top of the entire table would be if current index was central
        bottomScroll = topScroll + fullHeight           # Calculate y coordinate of where the bottom of the entire table would be if current index was central

        # Adjust table and pointer y coordinates
        if topScroll > top + rowHeight or fullHeight <= viewHeight:
            arrowOffset = - (topScroll - (top + rowHeight))
            topScroll = top + rowHeight

        elif bottomScroll < bottom:
            arrowOffset = bottom - bottomScroll
            topScroll = bottom - fullHeight

        else:
            arrowOffset = 0

        return topScroll, arrowOffset

    # Draws the instruction table
    def draw(self, display, fonts, palette, newIndex, animProg):
        if newIndex is None:                # If not in the middle of an animation:
            newIndex = self.currentIndex

        centre = self.centre                            # Coordinates of center of table
        width = self.width                              # Table width
        height = self.height                            # Table height
        rowHeight = self.rowHeight                      # Table row height
        top = self.centre[1] - height//2                # Top of table y coordinate
        bottom = self.centre[1] + height//2             # Bottom of table y coordinate
        fullHeight = rowHeight * self.numInstructions   # Height that table would be if it was all visible at once (excluding the header row)
        viewHeight = height-rowHeight                   # Height of the viewing region of the table (excluding the header row)
        left = centre[0] - width//2                     # Left of table x coordinate
        right = centre[0] + width//2                    # Right of table x coordinate

        # = Border =
        #pygame.draw.rect(display, palette['main'], (centre[0]-width//2, centre[1]-height//2, width, height), 1)

        # = Table =
        currentTopScroll, currentArrowOffset = self.getDrawOffsets(self.currentIndex)   # Get draw offset for current index
        newTopScroll, newArrowOffset = self.getDrawOffsets(newIndex)                    # Get draw offset for new index

        animTopScroll = linearProgression(currentTopScroll, newTopScroll, animProg)         # Calculate top scroll for current frame of animation
        animArrowOffset = linearProgression(currentArrowOffset, newArrowOffset, animProg)   # Calculate arrow offset for current frame of animation

        # For each instruction:
        for n, i in enumerate(self.instructions):
            y = animTopScroll + (n+0.5) * rowHeight                                                             # Calculate y coordinate of center of row

            if top + rowHeight/2 < y < bottom + rowHeight/2:                                                    # If the row is withn the table viewing region:
                drawCentredText(display, str(n+1), fonts['table2'], palette['main'], (left + 2.5*width/24, y))  # Draw instruction number

                for x, part in enumerate(i):                                                                    # For each part of the instruction:
                    if part is None:                                                                            # If part is the blank character:
                        part = self.blankChar                                                                   # Set part to blank character

                    xp = left + (3 + x*2) * self.width//12                                                      # Calculate x coordinate of center of label
                    drawCentredText(display, str(part), fonts['table1'], palette['main'], (xp, y))              # Draw label for current part of instruction

            yl = y + rowHeight/2                                                                                # Calculate y coordinate of bottom border of instruction
            if top + rowHeight/2 < yl < bottom + rowHeight/2:                                                   # If border is within the viewing region:
                pygame.draw.line(display, palette['main'], (left + 2*width//12, yl), (right-1, yl))             # Draw border

        pygame.draw.rect(display, palette['secondary'], (left + 2*width//12, top, 10*width//12, rowHeight))         # Header background
        pygame.draw.rect(display, palette['bg'], (left, bottom, width, rowHeight))                                  # Bottom mask for rows that are sliding out of viewing region
        pygame.draw.rect(display, palette['bg'], (left + 1*width//24, top, 3*width//24, rowHeight))                 #  Top-left mask for instruction numbers that are sliding out of viewing region
        pygame.draw.line(display, palette['main'], (left + 2*width//12, top), (right-1, top))                       # Header top border
        pygame.draw.line(display, palette['main'], (left + 2*width//12, top+rowHeight), (right-1, top+rowHeight))   # Header bottom border

        # Header labels
        drawCentredText(display, 'S', fonts['table1'], palette['main'], (left+3*width//12, top+rowHeight//2))
        drawCentredText(display, 'R', fonts['table1'], palette['main'], (left+5*width//12, top+rowHeight//2))
        drawCentredText(display, 'W', fonts['table1'], palette['main'], (left+7*width//12, top+rowHeight//2))
        drawCentredText(display, 'M', fonts['table1'], palette['main'], (left+9*width//12, top+rowHeight//2))
        drawCentredText(display, 'N', fonts['table1'], palette['main'], (left+11*width//12, top+rowHeight//2))

        # Calculate y coordinage of bottom border of table
        lineHeight = height
        if viewHeight > fullHeight:
            lineHeight = rowHeight + fullHeight
        else:                                                                                               # If table is taller than the viewing region:
            pygame.draw.line(display, palette['main'], (left + 2*width//12, bottom), (right-1, bottom))     # Draw bottom line of table

        # Draw vertical lines
        for x in range(6):
            xp = left + 2*width//12 + x*2*width//12
            pygame.draw.line(display, palette['main'], (xp, top), (xp, top+lineHeight), 1)

        # = Arrow =
        arrowX1 = left                                                      # Calculate x coordinate of left of arrow
        arrowX2 = left + width//24                                          # Calculate x coordinate of right of arrow

        arrowYOffset = rowHeight/4                                          # Height difference in pixels between center of arrow and top/bottom of arrow
        arrowY = top + (height-rowHeight)/2 + rowHeight + animArrowOffset   # Calculate y coordinate of center of arrow

        pygame.draw.polygon(display, palette['main'], ((arrowX1, arrowY-arrowYOffset), (arrowX2, arrowY), (arrowX1, arrowY+arrowYOffset)))  # Draw arrow

# Calculates value which is a fraction p of the way from a to b
def linearProgression(a, b, p):
    return a + p * (b-a)

# Draws text which is centered at the given coordinates
def drawCentredText(display, string, font, colour, centre):
    text = font.render(string, True, colour)
    rect = text.get_rect(center = centre)
    display.blit(text, rect)

# Draws the status indicator for the given machine status
def drawStatusIndicator(display, status):
    if status == 'playing':     # Play symbol
        pygame.draw.polygon(display, (0, 0, 0), ((20, 20), (20, 40), (40, 30)))

    elif status == 'paused':    # Pause symbol
        pygame.draw.rect(display, (0, 0, 0), (20, 20, 7, 20))
        pygame.draw.rect(display, (0, 0, 0), (33, 20, 7, 20))

    elif status == 'standby':   # Ellipsis
        pygame.draw.circle(display, (0, 0, 0), (22, 30), 3)
        pygame.draw.circle(display, (0, 0, 0), (30, 30), 3)
        pygame.draw.circle(display, (0, 0, 0), (38, 30), 3)

    elif status == 'stopped':   # Stop symbol
        pygame.draw.rect(display, (0, 0, 0), (20, 20, 20, 20))

# Draws everything onto the display
def blitAll(machine, paused, display, clock, fonts, palette, dim, dimMachine, centreMachine, cellSize, drawDetail=False):
    display.fill(palette['bg'])                                                             # Background
    machine.draw(display, fonts, palette, dimMachine, centreMachine, cellSize, drawDetail)  # Draws machine, tape and instruction table

    if paused:                                                                              # If the simulation is paused:
        status = 'paused'
    else:
        status = machine.getStatus()                                                        # Get the machine's status
    drawStatusIndicator(display, status)

# Main loop of the program
def main(machine, display, FPS, clock, fonts, palette, dim, dimMachine, centreMachine, cellSize):
    paused = False                                          # Initialised paused flag
    drawDetail = False                                      # Initialise draw detail flag

    # Main loop
    while True:
        for event in pygame.event.get():                    # Get all user events
            if event.type == pygame.QUIT:                   # If user closed the window:
                pygame.quit()                               # Close pygame
                return                                      # Finish loop

            elif event.type == pygame.KEYDOWN:              # If user pressed a key:
                if event.key == pygame.K_TAB:               # If user pressed TAB key:
                    drawDetail = not drawDetail             # Toggle draw detail flag

                elif machine.running:                       # If the machine is running:
                    if not machine.isStandby():             # If the machine is not in standby:
                        if event.key == pygame.K_p:         # If the user pressed P key:
                            paused = not paused             # Toggle pause flag
                        elif event.key == pygame.K_ESCAPE:  # If user pressed ESCAPE key:
                            machine.phaseCtr = 0            # Set phase counter to 0 (stop whatever the machine is doing)

                    else:                                   # If the machine is in standby:
                        if event.key == pygame.K_SPACE:     # If the user pressed SPACE key:
                            machine.nudge('full')           # Make machine do a full step
                        elif event.key == pygame.K_t:       # If the user pressed T key:
                            machine.nudge('one')            # Make machine do one part of a step
                        elif event.key == pygame.K_r:       # If user pressed R key:
                            machine.nudge('go')             # Make machine run continuously

                else:                                       # If the machine has stopped:
                    if event.key == pygame.K_LEFT:          # If the user pressed LEFT key:
                        machine.moveHead('l')               # Move the head left
                    elif event.key == pygame.K_RIGHT:       # If the user pressed RIGHT key:
                        machine.moveHead('r')               # Move the head right
                    if event.key == pygame.K_UP:            # If the user pressed UP key:
                        machine.headUp()                    # Move the head up
                    elif event.key == pygame.K_DOWN:        # If the user pressed DOWN key:
                        machine.headDown()                  # Move the head down

        keys = pygame.key.get_pressed()                     # Get all keys currently being pressed
        if keys[pygame.K_EQUALS]:                           # If EQUALS key is being pressed:
            cellSize += 1                                   # Increment cell size

            tapeFonts = generateTapeFonts(cellSize)         # Regenerate the tape fonts
            fonts['detail'] = tapeFonts['detail']           # Reassign the fonts
            fonts['cell'] = tapeFonts['cell']

        if keys[pygame.K_MINUS]:                            # If MINUS key is being pressed:
            cellSize = max(1, cellSize-1)                   # Attempt to decrement the cell size

            tapeFonts = generateTapeFonts(cellSize)         # Regenerate the tape fonts
            fonts['detail'] = tapeFonts['detail']           # Reassign the fonts
            fonts['cell'] = tapeFonts['cell']

        # Draw everything
        blitAll(machine, paused, display, clock, fonts, palette, dim, dimMachine, centreMachine, cellSize, drawDetail)
        pygame.display.update()

        clock.tick(FPS) # Maintain FPS

        if not paused:                  # If the machine is not paused:
            machine.update(palette)     # Update the machine

# Initialises and begins the simulation
def run(instructions, acceptStates, startState, tape, startPos, blankChar, dim, cellSize, speed, FPS):
    pygame.init()                                                                                                                       # Initialise pygame
    pygame.display.set_caption('Turing Machine Simulator')                                                                              # Set window caption

    sim = initialise(dim, cellSize)     # Initialise simulation

    instructionObj = Instructions(instructions)                                                                                                 # Create instructions object
    tapeObj = Tape(blankChar, tape)                                                                                                             # Create tape object
    instructionTableObj = InstructionTable(instructions, blankChar, sim['ITcentre'], sim['ITwidth'], sim['ITheight'], sim['ITrowHeight'])       # Create instruction table ovject
    machineObj = Machine(instructionObj, tapeObj, startState, acceptStates, startPos, sim['palette'], instructionTableObj, speed)               # Create machine object

    main(machineObj, sim['display'], FPS, sim['clock'], sim['fonts'], sim['palette'], dim, sim['dimMachine'], sim['centreMachine'], cellSize)   # Begin main loop

# Debugging example
run(((0, None, '#', 'r', 0),(0, ':', 'o', 'l', 0), (0, '#', '[', 'r', 0)), (), 0, {'2':':'}, 0, '', (800, 600), 50, 1, 100)
