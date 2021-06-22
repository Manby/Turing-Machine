import pygame
from math import ceil, floor, sin, pi

def initialise(dim, cellSize):
    dimMachine = dim
    centreMachine = (dim[0]//2, 4*dim[1]//5)

    display = pygame.display.set_mode(dim)
    clock = pygame.time.Clock()

    ITcentre = (4*dim[0]//5, dim[1]//3)
    ITwidth = dim[0]//3
    ITheight = dim[1]//2

    ITrowHeight = ITwidth/8

    tapeFonts = generateTapeFonts(cellSize)
    tableFonts = generateTableFonts(ITrowHeight)
    fonts = {
    'detail':tapeFonts['detail'],
    'cell':tapeFonts['cell'],
    'table1':tableFonts['table1'],
    'table2':tableFonts['table2'],
    }

    palette = {'bg':(240, 240, 240), 'main':(0, 0, 0), 'error':(255, 0, 0), 'accept':(0, 255, 0), 'state':(255, 255, 255), 'secondary':(200, 200, 200)}

    return display, clock, fonts, palette, dimMachine, centreMachine, ITcentre, ITwidth, ITheight, ITrowHeight

def generateTapeFonts(cellSize):
    return {
    'detail':pygame.font.SysFont('consolas', 20*cellSize//80, True),
    'cell':pygame.font.SysFont('consolas', 40*cellSize//70, True)
    }

def generateTableFonts(rowHeight):
    rowHeight = round(rowHeight)
    return {
    'table1':pygame.font.SysFont('consolas', 4*rowHeight//5, True),
    'table2':pygame.font.SysFont('consolas', rowHeight//2, True)
    }

class Instructions:
    def __init__(self, instructions):
        self.instructions = {}

        for n, i in enumerate(instructions):
            self.setInstruction(i[0], i[1], i[2], i[3], i[4], n)

    def setInstruction(self, state, read, written, direction, next, index):
        stateSet = self.instructions.get(state)
        if stateSet is None:
            stateSet = {}
            self.instructions[state] = stateSet

        stateSet[read] = (written, direction, next, index)

    def getInstruction(self, state, read):
        stateSet = self.instructions.get(state)
        if stateSet is None:
            return None

        return stateSet.get(read)

class Tape:
    def __init__(self, blank, definition={}):
        self.blank = blank
        self.definition = definition

    def get(self, pos):
        char = self.definition.get(str(pos))

        return char

    def set(self, pos, char):
        self.definition[str(pos)] = char

    def getBlank(self):
        return self.blank

class Machine:
    def __init__(self, instructions, tape, startState, acceptStates, startPos, palette, instructionTable, speed=1):
        self.instructions = instructions
        self.tape = tape
        self.state = startState
        self.acceptStates = acceptStates
        self.pos = startPos
        self.instructionTable = instructionTable

        self.direction = None
        self.written = None
        self.next = None
        self.instructionIndex = None
        self.running = True

        self.speed = speed
        self.phase = 0
        self.animating = None
        self.colour = palette['main']
        self.phaseCtr = 0

        self.anim = {
        'tapeOffset': 0,
        'headOffset': 0,
        'headDown': False,
        'charOffset': 0,
        'instructionTableOffset': 0
        }

    def nudge(self, mode):
        if mode == 'one':
            self.phaseCtr += 1
        elif mode == 'full':
            self.phaseCtr += 5 - self.phase
        elif mode == 'go':
            self.phaseCtr = -1

    #Machine ready for next operation?
    def isStandby(self):
        return self.phaseCtr == 0 and self.running and not self.animating

    def writeAct(self):
        self.tape.set(self.pos, self.written)

    def writeAnim(self, char):
        charOffset = self.anim['charOffset']
        charOffset += (0.005 + 0.05 * sin(charOffset*pi)) * self.speed

        if charOffset >= 1:
            self.animating = None
            self.anim['charOffset'] = 0
            self.writeAct()
        else:
            self.anim['charOffset'] = charOffset

    def write(self, char, animate=True):
        if animate:
            if self.animating is None:
                if char is None:
                    char = self.tape.getBlank()
                self.animating = 'w' + char
        else:
            self.writeAct()

    def moveHeadAct(self, direction):
        self.pos += {'l':-1, 'r':1}[direction]

    def moveHeadAnim(self, direction):
        tapeOffset = self.anim['tapeOffset']
        tapeOffset += ({'l':1, 'r':-1}[direction]) * (0.005 + 0.05 * sin(abs(tapeOffset)*pi)) * self.speed

        if abs(tapeOffset) >= 1:
            self.animating = None
            self.anim['tapeOffset'] = 0
            self.moveHeadAct(direction)
        else:
            self.anim['tapeOffset'] = tapeOffset

    def moveHead(self, direction, animate=True):
        if animate:
            if self.animating is None:
                self.animating = 'm' + direction
        else:
            self.moveHeadAct(direction)

    def headDownAnim(self):
        headOffset = self.anim['headOffset']
        headOffset += (0.005 + 0.05 * sin(headOffset*pi)) * self.speed

        if headOffset >= 1:
            self.animating = None
            self.anim['headOffset'] = 1
            self.anim['headDown'] = True
        else:
            self.anim['headOffset'] = headOffset

    def headDown(self):
        if self.animating is None and not self.anim['headDown']:
            self.animating = 'hd'

    def headUpAnim(self):
        headOffset = self.anim['headOffset']
        headOffset -= (0.005 + 0.05 * sin(abs(headOffset)*pi)) * self.speed

        if headOffset <= 0:
            self.animating = None
            self.anim['headOffset'] = 0
            self.anim['headDown'] = False
        else:
            self.anim['headOffset'] = headOffset

    def headUp(self):
        if self.animating is None and self.anim['headDown']:
            self.animating = 'hu'

    def moveInstructionTableAct(self, instructionIndex):
        self.instructionTable.currentIndex = instructionIndex

    def moveInstructionTableAnim(self, instructionIndex):
        instructionTableOffset = self.anim['instructionTableOffset']
        instructionTableOffset += (0.005 + 0.05 * sin(abs(instructionTableOffset)*pi)) * self.speed

        if instructionTableOffset >= 1:
            self.animating = None
            self.anim['instructionTableOffset'] = 0
            self.moveInstructionTableAct(instructionIndex)
        else:
            self.anim['instructionTableOffset'] = instructionTableOffset

    def moveInstructionTable(self, instructionIndex, animate=True):
        if animate:
            if self.animating is None:
                self.animating = 'i' + str(instructionIndex)
        else:
            self.moveInstructionTableAct(instructionIndex)

    def draw(self, display, fonts, palette, dim, centre, cellSize, drawDetail=False):
        #Instruction Table
        self.instructionTable.draw(display, fonts, palette, self.instructionIndex, self.anim['instructionTableOffset'])

        midX = centre[0]
        midY = centre[1]

        #Tape
        offset = self.anim['tapeOffset']
        pOffset = offset * cellSize
        truePos = self.pos - offset
        sideCells = ceil((dim[0]/cellSize - 1) / 2) + 1

        for c in range(-sideCells, sideCells+1):
            x = midX + c*cellSize
            pygame.draw.rect(display, palette['main'], (x-cellSize//2 + pOffset, midY-cellSize//2, cellSize, cellSize), 1)

            p = c + self.pos
            char = self.tape.get(p)
            if char is None:
                char = self.tape.getBlank()

            #f during write animation and on middle cell:
            if c == 0 and not self.animating is None and self.animating[0] == 'w':
                written = self.animating[1:]
                charOffset = self.anim['charOffset']
                pCharOffset = charOffset * cellSize

                drawCentredText(display, char, fonts['cell'], palette['main'], (x + pOffset, midY + pCharOffset))
                drawCentredText(display, written, fonts['cell'], palette['main'], (x + pOffset, midY - cellSize + pCharOffset))

                pygame.draw.rect(display, palette['bg'], (x-cellSize//2 + pOffset, floor(midY-3*cellSize/2), cellSize, cellSize))
                pygame.draw.rect(display, palette['bg'], (x-cellSize//2 + pOffset, ceil(midY+cellSize/2), cellSize, cellSize))

            else:
                drawCentredText(display, char, fonts['cell'], palette['main'], (x + pOffset, midY))

            if drawDetail:
                drawCentredText(display, str(p), fonts['detail'], palette['main'], (x + pOffset, midY+ 2*cellSize//3))

        #Read/Write Head
        offset = self.anim['headOffset']
        pOffset = offset * cellSize//4
        arrowTop = midY - 5*cellSize//4 + pOffset
        arrowBottom = midY - 3*cellSize//4 + pOffset
        arrowMiddle = (2*arrowTop+arrowBottom)//3

        pygame.draw.polygon(display, self.colour, ((midX, arrowBottom), (midX-cellSize//2, arrowTop), (midX+cellSize//2, arrowTop)))
        if drawDetail:
            drawCentredText(display, str(self.state), fonts['detail'], palette['state'], (midX, arrowMiddle))

    def animate(self):
        if self.animating[0] == 'm':
            direction = self.animating[1]
            self.moveHeadAnim(direction)

        elif self.animating[0] == 'h':
            direction = self.animating[1]
            if direction == 'd':
                self.headDownAnim()
            elif direction == 'u':
                self.headUpAnim()

        elif self.animating[0] == 'w':
            char = self.animating[1:]
            self.writeAnim(char)

        elif self.animating[0] == 'i':
            index = int(self.animating[1:])
            self.moveInstructionTableAnim(index)

    def update(self, palette):
        #If animating:
        if not self.animating is None:
            self.animate()

        #If not animating and running and phase counter allows phase change:
        elif self.running and self.phaseCtr != 0:
            #Head Down
            if self.phase == 0:
                self.headDown()

            #Read
            elif self.phase == 1:
                cell = self.tape.get(self.pos)
                instruction = self.instructions.getInstruction(self.state, cell)

                #If transition not defined:
                if instruction is None:
                    self.colour = palette['error']
                    self.running = False
                    return

                written, direction, next, index = instruction

                self.next = next
                self.direction = direction
                self.written = written

                self.instructionIndex = index
                self.moveInstructionTable(index)

            #Write
            elif self.phase == 2:
                self.instructionIndex = None

                self.write(self.written)

            #Change State & Head Up
            elif self.phase == 3:
                self.written = None
                self.state = self.next

                #If reached an accept state:
                if self.state in self.acceptStates:
                    self.colour = palette['accept']

                self.next = None
                self.headUp()

            #Move Tape
            elif self.phase == 4:
                self.moveHead(self.direction)
                self.direction = None

                if self.state in self.acceptStates:
                    self.running = False

            self.phase = (self.phase+1) % 5
            if self.phaseCtr > 0:
                self.phaseCtr -= 1

        #Automatically progress from phase 0 to phase 1
        elif self.running and self.phase == 1:
            self.phaseCtr += 1

    def getStatus(self):
        if not self.running:
            return 'stopped'

        if self.animating or self.phaseCtr != 0 or self.phase == 1:
            return 'playing'

        return 'standby'

class InstructionTable:
    def __init__(self, instructions, blankChar, centre, width, height, rowHeight):
        self.instructions = instructions
        self.numInstructions = len(instructions)
        self.blankChar = blankChar
        self.centre = centre
        self.width = width
        self.height = height
        self.rowHeight = rowHeight

        self.currentIndex = -1

    def getDrawOffsets(self, index):
        height = self.height
        rowHeight = self.rowHeight
        top = self.centre[1] - height//2
        bottom = self.centre[1] + height//2
        fullHeight = rowHeight * self.numInstructions
        viewHeight = height-rowHeight

        topScroll = top + height/2 - (index*rowHeight)
        bottomScroll = topScroll + fullHeight

        if topScroll > top + rowHeight or fullHeight <= viewHeight:
            arrowOffset = - (topScroll - (top + rowHeight))
            topScroll = top + rowHeight

        elif bottomScroll < bottom:
            arrowOffset = bottom - bottomScroll
            topScroll = bottom - fullHeight

        else:
            arrowOffset = 0

        return topScroll, arrowOffset

    def draw(self, display, fonts, palette, newIndex, animProg):
        if newIndex is None:
            newIndex = self.currentIndex

        centre = self.centre
        width = self.width
        height = self.height
        rowHeight = self.rowHeight
        left = centre[0] - width//2
        right = centre[0] + width//2
        top = centre[1] - height//2
        bottom = centre[1] + height//2
        viewHeight = height - rowHeight
        fullHeight = self.numInstructions * rowHeight

        #Border
        #pygame.draw.rect(display, palette['main'], (centre[0]-width//2, centre[1]-height//2, width, height), 1)

        #Table
        currentTopScroll, currentArrowOffset = self.getDrawOffsets(self.currentIndex)
        newTopScroll, newArrowOffset = self.getDrawOffsets(newIndex)

        animTopScroll = linearProgression(currentTopScroll, newTopScroll, animProg)
        animArrowOffset = linearProgression(currentArrowOffset, newArrowOffset, animProg)

        for n, i in enumerate(self.instructions):
            y = animTopScroll + (n+0.5) * rowHeight

            if top + rowHeight/2 < y < bottom + rowHeight/2:
                drawCentredText(display, str(n+1), fonts['table2'], palette['main'], (left + 2.5*width/24, y))

                for x, part in enumerate(i):
                    if part is None:
                        part = self.blankChar

                    xp = left + (3 + x*2) * self.width//12
                    drawCentredText(display, str(part), fonts['table1'], palette['main'], (xp, y))

            yl = y + rowHeight/2
            if top + rowHeight/2 < yl < bottom + rowHeight/2:
                pygame.draw.line(display, palette['main'], (left + 2*width//12, yl), (right-1, yl))


        pygame.draw.rect(display, palette['secondary'], (left + 2*width//12, top, 10*width//12, rowHeight))
        pygame.draw.rect(display, palette['bg'], (left, bottom, width, rowHeight))
        pygame.draw.rect(display, palette['bg'], (left + 1*width//24, top, 3*width//24, rowHeight))
        pygame.draw.line(display, palette['main'], (left + 2*width//12, top), (right-1, top))
        pygame.draw.line(display, palette['main'], (left + 2*width//12, top+rowHeight), (right-1, top+rowHeight))

        drawCentredText(display, 'S', fonts['table1'], palette['main'], (left+3*width//12, top+rowHeight//2))
        drawCentredText(display, 'R', fonts['table1'], palette['main'], (left+5*width//12, top+rowHeight//2))
        drawCentredText(display, 'W', fonts['table1'], palette['main'], (left+7*width//12, top+rowHeight//2))
        drawCentredText(display, 'M', fonts['table1'], palette['main'], (left+9*width//12, top+rowHeight//2))
        drawCentredText(display, 'N', fonts['table1'], palette['main'], (left+11*width//12, top+rowHeight//2))

        lineHeight = height
        if viewHeight > fullHeight:
            lineHeight = rowHeight + fullHeight
        else:
            pygame.draw.line(display, palette['main'], (left + 2*width//12, bottom), (right-1, bottom))

        for x in range(6):
            xp = left + 2*width//12 + x*2*width//12
            pygame.draw.line(display, palette['main'], (xp, top), (xp, top+lineHeight), 1)

        #Arrow
        arrowX1 = left
        arrowX2 = left + width//24

        arrowYOffset = rowHeight/4
        arrowY = top + (height-rowHeight)/2 + rowHeight + animArrowOffset

        pygame.draw.polygon(display, palette['main'], ((arrowX1, arrowY-arrowYOffset), (arrowX2, arrowY), (arrowX1, arrowY+arrowYOffset)))


def linearProgression(a, b, p):
    return a + p * (b-a)

def drawCentredText(display, string, font, colour, centre):
    text = font.render(string, True, colour)
    rect = text.get_rect(center = centre)
    display.blit(text, rect)

def drawStatusIndicator(display, status):
    if status == 'playing':
        pygame.draw.polygon(display, (0, 0, 0), ((20, 20), (20, 40), (40, 30)))

    elif status == 'paused':
        pygame.draw.rect(display, (0, 0, 0), (20, 20, 7, 20))
        pygame.draw.rect(display, (0, 0, 0), (33, 20, 7, 20))

    elif status == 'standby':
        pygame.draw.circle(display, (0, 0, 0), (22, 30), 3)
        pygame.draw.circle(display, (0, 0, 0), (30, 30), 3)
        pygame.draw.circle(display, (0, 0, 0), (38, 30), 3)

    elif status == 'stopped':
        pygame.draw.rect(display, (0, 0, 0), (20, 20, 20, 20))

def blitAll(machine, paused, display, clock, fonts, palette, dim, dimMachine, centreMachine, cellSize, drawDetail=False):
    display.fill(palette['bg'])
    machine.draw(display, fonts, palette, dimMachine, centreMachine, cellSize, drawDetail)
    #pygame.draw.rect(display, (0, 0, 0), (centreMachine[0]-dimMachine[0]//2, centreMachine[1]-dimMachine[1]//2, dimMachine[0], dimMachine[1]), 1)

    if paused:
        status = 'paused'
    else:
        status = machine.getStatus()
    drawStatusIndicator(display, status)

def main(machine, display, FPS, clock, fonts, palette, dim, dimMachine, centreMachine, cellSize):
    paused = False
    drawDetail = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    drawDetail = not drawDetail

                elif machine.running:
                    if not machine.isStandby():
                        if event.key == pygame.K_p:
                            paused = not paused
                        elif event.key == pygame.K_ESCAPE:
                            machine.phaseCtr = 0

                    #If machine is idle
                    else:
                        if event.key == pygame.K_SPACE:
                            machine.nudge('full')
                        elif event.key == pygame.K_t:
                            machine.nudge('one')
                        elif event.key == pygame.K_r:
                            machine.nudge('go')

                else:
                    if event.key == pygame.K_LEFT:
                        machine.moveHead('l')
                    elif event.key == pygame.K_RIGHT:
                        machine.moveHead('r')
                    if event.key == pygame.K_UP:
                        machine.headUp()
                    elif event.key == pygame.K_DOWN:
                        machine.headDown()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_EQUALS]:
            cellSize += 1
            tapeFonts = generateTapeFonts(cellSize)
            fonts['detail'] = tapeFonts['detail']
            fonts['cell'] = tapeFonts['cell']
        if keys[pygame.K_MINUS]:
            cellSize -= 1
            if cellSize < 1:
                cellSize = 1

            tapeFonts = generateTapeFonts(cellSize)
            fonts['detail'] = tapeFonts['detail']
            fonts['cell'] = tapeFonts['cell']

        blitAll(machine, paused, display, clock, fonts, palette, dim, dimMachine, centreMachine, cellSize, drawDetail)
        pygame.display.update()
        clock.tick(FPS)

        if not paused:
            machine.update(palette)

def run(instructions, acceptStates, startState, tape, startPos, blankChar, dim, cellSize, speed, FPS):
    pygame.init()
    pygame.display.set_caption('Turing Machine Simulator')

    display, clock, fonts, palette, dimMachine, centreMachine, ITcentre, ITwidth, ITheight, ITrowHeight = initialise(dim, cellSize)

    instructionObj = Instructions(instructions)
    tapeObj = Tape(blankChar, tape)
    instructionTableObj = InstructionTable(instructions, blankChar, ITcentre, ITwidth, ITheight, ITrowHeight)
    machineObj = Machine(instructionObj, tapeObj, startState, acceptStates, startPos, palette, instructionTableObj, speed)

    main(machineObj, display, FPS, clock, fonts, palette, dim, dimMachine, centreMachine, cellSize)

#run(((0, None, '#', 'r', 0),(0, ':', 'o', 'l', 0), (0, '#', '[', 'r', 0)), (), 0, {'2':':'}, 0, '', (800, 600), 50, 1, 100)
