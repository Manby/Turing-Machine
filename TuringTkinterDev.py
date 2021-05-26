import tkinter as tk
import tkinter.font as font
from tkinter import ttk, filedialog, messagebox
import json
import TuringSim
import re

class Application(ttk.Notebook):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master

		self.fonts = {'large':font.Font(family='Helvetica', size=12, weight='bold')}

		self.tabs = {}
		self.widgets = {}
		self.instructionRows = []
		self.acceptRows = []
		self.tapeCells = {}
		self.tapeCellDivs = []

		self.tapePos = 0
		self.tape = {}

		self.createTabs()
		self.pack(side='top', expand=True, fill='both')

	def createTabs(self):
		x = self.tabs

		x['xMachine'] = machineTab = ttk.Frame(self)
		self.machineTabWidgets(machineTab)
		self.add(machineTab, text='Machine')

		x['xTape'] = tapeTab = ttk.Frame(self)
		self.tapeTabWidgets(tapeTab)
		self.add(tapeTab, text='Tape')

		x['xExecute'] = executeTab = ttk.Frame(self)
		self.executeTabWidgets(executeTab)
		self.add(executeTab, text='Execute')

	def machineTabWidgets(self, tab):
		w = self.widgets

		dTop = tk.Frame(tab, bg='brown')
		dTop.pack(side='top', expand=True, fill='both')

		dInstruction = tk.Frame(dTop, borderwidth=3, relief='sunken')
		dInstruction.pack(side='left', expand=True, fill='both')

		dInstructionScrollFrame = tk.Frame(dInstruction)
		dInstructionScrollFrame.pack(side='right', expand=True, fill='both')

		dLabels = tk.Frame(dInstructionScrollFrame, bg='green')
		dLabels.pack(side='top', fill='x')

		lState = tk.Label(dLabels, text='State')
		lState.pack(side='left', padx=(32, 34))
		lRead = tk.Label(dLabels, text='Read')
		lRead.pack(side='left', padx=(0, 42))
		lWrite = tk.Label(dLabels, text='Write')
		lWrite.pack(side='left', padx=(0, 29))
		lDir = tk.Label(dLabels, text='Direction')
		lDir.pack(side='left', padx=(0, 11))
		lNext = tk.Label(dLabels, text='Next State')
		lNext.pack(side='left')

		w['cInstruction'] = cInstruction = tk.Canvas(dInstructionScrollFrame, bg='pink')

		scrollbar = tk.Scrollbar(dInstruction, orient='vertical', command=cInstruction.yview)
		scrollbar.pack(side='left', fill='y')
		cInstruction.configure(yscrollcommand=scrollbar.set)
		cInstruction.pack(side='top', expand=True, fill='both')

		w['cdInstruction'] = cdInstruction = tk.Frame(cInstruction, bg='indigo')

		cInstruction.create_window((0, 0), window=cdInstruction, anchor='nw')
		tagUp('instructionScrollable', cdInstruction)
		tab.bind_class('instructionScrollable', '<MouseWheel>', lambda event, canvas=cInstruction: self.mouseWheel(event, canvas))

		cdInstruction.update_idletasks()

		cInstruction.config(scrollregion=cInstruction.bbox("all"))

		dRight = tk.Frame(dTop, bg='purple')
		dRight.pack(side='left', fill='y')

		dAccept = tk.Frame(dRight, borderwidth=3, relief='sunken')
		dAccept.pack(side='top')

		dAcceptScrollFrame = tk.Frame(dAccept)
		dAcceptScrollFrame.pack(side='right', anchor='nw', expand=True, fill='both')

		dLabel = tk.Frame(dAcceptScrollFrame, bg='green')
		dLabel.pack(side='top', fill='x')

		lState = tk.Label(dLabel, text='Accept States')
		lState.pack(side='left')

		w['cAccept'] = cAccept = tk.Canvas(dAcceptScrollFrame, bg='red', width=150, height=140)

		scrollbar = tk.Scrollbar(dAccept, orient='vertical', command=cAccept.yview)
		scrollbar.pack(side='left', fill='y')
		cAccept.configure(yscrollcommand=scrollbar.set)
		cAccept.pack(side='top', expand=True, fill='both')

		w['cdAccept'] = cdAccept = tk.Frame(cAccept, bg='indigo')

		cAccept.create_window((0, 0), window=cdAccept, anchor='nw')
		tagUp('acceptScrollable', cdAccept)
		tab.bind_class('acceptScrollable', '<MouseWheel>', lambda event, canvas=cAccept: self.mouseWheel(event, canvas))

		cdAccept.update_idletasks()

		cAccept.config(scrollregion=cAccept.bbox("all"))

		dFile = tk.Frame(dTop, bg='gold')
		dFile.pack(side='right', fill='y')

		bImport = tk.Button(dFile, text='Import Instructions', command=self.importMachine)
		bImport.pack(side='top')
		bExport = tk.Button(dFile, text='Export Instructions', command=self.exportMachine)
		bExport.pack(side='top', fill='x')

		dInstructionButton = tk.Frame(dInstructionScrollFrame, bg='orange')
		dInstructionButton.pack(side='top', fill='both')

		bAddInstruction = tk.Button(dInstructionButton, text='Add', command=self.addInstruction)
		bAddInstruction.pack(side='left')
		bResetInstructions = tk.Button(dInstructionButton, text='Reset', fg='red', command=lambda: self.resetInstructions(True))
		bResetInstructions.pack(side='left')

		dAcceptButton = tk.Frame(dAcceptScrollFrame, bg='orange')
		dAcceptButton.pack(side='top', fill='both')

		bAddAccept = tk.Button(dAcceptButton, text='Add', command=self.addAccept)
		bAddAccept.pack(side='left')
		bResetAccepts = tk.Button(dAcceptButton, text='Reset', fg='red', command=lambda: self.resetAccepts(True))
		bResetAccepts.pack(side='left')

		dInput = tk.Frame(tab, bg='crimson')
		dInput.pack(side='top', fill='x')

		dStart = tk.Frame(dInput, bg='teal')
		dStart.pack(side='left')

		lStart = tk.Label(dStart, text='Start State:')
		lStart.pack(side='left')
		w['eStartState'] = eStart = tk.Entry(dStart, width=5)
		eStart.pack(side='left')

	def tapeTabWidgets(self, tab):
		w = self.widgets

		dTop = tk.Frame(tab, bg='violet')
		dTop.pack(side='top', expand=True, fill='both')

		dTape = tk.Frame(dTop, bg='blue')
		dTape.pack(side='left', expand=True)

		lHead = tk.Label(dTape, text='▼')
		lHead.pack(side='top')

		dFile = tk.Frame(dTop, bg='gold')
		dFile.pack(side='right', fill='y')

		bImport = tk.Button(dFile, text='Import Tape', command=self.importTape)
		bImport.pack(side='top')
		bExport = tk.Button(dFile, text='Export Tape', command=self.exportTape)
		bExport.pack(side='top', fill='x')

		w['dCells'] = dCells = tk.Frame(dTape, bg='green')
		dCells.pack(side='top', expand=True, fill='x')

		dShift = tk.Frame(dTape, bg='purple')
		dShift.pack(side='top')

		bShiftLeft = tk.Button(dShift, text='<', width=3, command=lambda: self.shiftTape(-1))
		bShiftLeft.pack(side='left')
		bShiftRight = tk.Button(dShift, text='>', width=3, command=lambda: self.shiftTape(1))
		bShiftRight.pack(side='right')

		dAccess = tk.Frame(dTape, bg='lime')
		dAccess.pack(side='top', fill='x')

		dGoto = tk.Frame(dAccess, bg='salmon')
		dGoto.pack(side='left')

		lGoto = tk.Label(dGoto, text='Jump To:')
		lGoto.pack(side='left')
		w['eGoto'] = eGoto = tk.Entry(dGoto, width=5)
		eGoto.pack(side='left')
		eGoto.bind('<Return>', self.goto)
		bGoto = tk.Button(dGoto, text='Jump', command=self.goto)
		bGoto.pack(side='left')

		bReset = tk.Button(dAccess, text='Reset', fg='red', command=lambda: self.resetTape(True))
		bReset.pack(side='right')

		dInput = tk.Frame(tab, bg='aqua')
		dInput.pack(side='top', fill='x')

		dStart = tk.Frame(dInput, bg='teal')
		dStart.pack(side='left')

		lStart = tk.Label(dStart, text='Start Position:')
		lStart.pack(side='left')
		w['eStartPosition'] = eStart = tk.Entry(dStart, width=5)
		eStart.pack(side='left')

		dBlank = tk.Frame(dInput, bg='teal')
		dBlank.pack(side='left')

		lBlank = tk.Label(dBlank, text='Blank Character:')
		lBlank.pack(side='left')
		w['eBlank'] = eBlank = tk.Entry(dBlank, width=5)
		eBlank.pack(side='left')

		self.generateTapeWidgets()

	def executeTabWidgets(self, tab):
		w = self.widgets

		dMain = tk.Frame(tab, bg='red')
		dMain.pack(side='top', expand=True)

		dSizing = tk.Frame(dMain, bg='blue')
		dSizing.pack(side='top', pady=(10, 5))

		dDim = tk.Frame(dSizing, bg='green', borderwidth=1, relief='groove')
		dDim.pack(side='left', padx=(0, 40))

		lWidth = tk.Label(dDim, text='Width:')
		lWidth.pack(side='left')
		w['eWidth'] = eWidth = tk.Entry(dDim, width=5)
		eWidth.pack(side='left')
		eWidth.bind('<Return>', self.execute)
		eWidth.insert(0, '700')
		lHeight = tk.Label(dDim, text='Height:')
		lHeight.pack(side='left')
		w['eHeight'] = eHeight = tk.Entry(dDim, width=5)
		eHeight.pack(side='left')
		eHeight.insert(0, '600')
		eHeight.bind('<Return>', self.execute)

		dCellSize = tk.Frame(dSizing, bg='orange')
		dCellSize.pack(side='left')

		lCellSize = tk.Label(dCellSize, text='Cell Size:')
		lCellSize.pack(side='left')
		w['eCellSize'] = eCellSize = tk.Entry(dCellSize, width=4)
		eCellSize.pack(side='left')
		eCellSize.insert(0, '50')
		eCellSize.bind('<Return>', self.execute)

		dPacing = tk.Frame(dMain, bg='blue')
		dPacing.pack(side='top', pady=(5, 10))

		dSpeed = tk.Frame(dPacing, bg='green')
		dSpeed.pack(side='left', padx=(0, 10))

		lSpeed = tk.Label(dSpeed, text='Speed:')
		lSpeed.pack(side='left')
		w['eSpeed'] = eSpeed = tk.Entry(dSpeed, width=4)
		eSpeed.pack(side='left')
		eSpeed.insert(0, '1')
		eSpeed.bind('<Return>', self.execute)

		dFPS = tk.Frame(dPacing, bg='orange')
		dFPS.pack(side='left')

		lFPS = tk.Label(dFPS, text='FPS:')
		lFPS.pack(side='left')
		w['eFPS'] = eFPS = tk.Entry(dFPS, width=5)
		eFPS.pack(side='left')
		eFPS.insert(0, '100')
		eFPS.bind('<Return>', self.execute)

		bReset = tk.Button(dMain, text='Restore Defaults', command=self.restoreDefaultSettings)
		bReset.pack(side='top', pady=10)

		bExecute = tk.Button(dMain, text='Execute', font=self.fonts['large'], command=self.execute)
		bExecute.pack(side='top', fill='x', pady=30)

	def generateTapeWidgets(self):
		t = self.tape
		w = self.widgets
		c = self.tapeCells = {}
		d = self.tapeCellDivs

		for div in d:
			div.destroy()
		d = self.tapeCellDivs = []

		frame = w['dCells']

		sideCells = 5

		for i in range(-sideCells, sideCells+1):
			pos = self.tapePos + i
			cellFrame = tk.Frame(frame, bg='gray')
			cellFrame.pack(side='left', expand=True)

			cell = tk.Entry(cellFrame, justify='center', width=10)
			cell.pack(side='top', expand=True)

			if str(pos) in t.keys():
				char = t[str(pos)]
				cell.insert(0, char)

			label = tk.Label(cellFrame, text=str(pos))
			label.pack(side='top')

			c[str(pos)] = cell
			d.append(cellFrame)

	def updateInstructionCanvas(self):
		w = self.widgets
		i = self.instructionRows

		frame = w['cdInstruction']
		canvas = w['cInstruction']

		if not i:
			frame['height'] = 1

		frame.update_idletasks()
		canvas.config(scrollregion=canvas.bbox("all"))

	def updateAcceptCanvas(self):
		w = self.widgets
		a = self.acceptRows

		frame = w['cdAccept']
		canvas = w['cAccept']

		if not a:
			frame['height'] = 1

		frame.update_idletasks()
		canvas.config(scrollregion=canvas.bbox("all"))

	def addInstruction(self, data=None):
		w = self.widgets
		i = self.instructionRows

		if data is None:
			data = ('', '', '', '', '')

		frame = w['cdInstruction']
		dRow = tk.Frame(frame, bg='blue')
		dRow.pack(side='top')

		lID = tk.Label(dRow, width=2)
		lID.pack(side='left', padx=(0, 10))

		eState = tk.Entry(dRow, width=10)
		eState.pack(side='left')
		eState.insert(0, data[0])

		eRead = tk.Entry(dRow, width=10)
		eRead.pack(side='left', padx=(0, 10))
		if not data[1] is None:
			eRead.insert(0, data[1])

		eWrite = tk.Entry(dRow, width=10)
		eWrite.pack(side='left')
		if not data[2] is None:
			eWrite.insert(0, data[2])

		eNew = tk.Entry(dRow, width=10)
		eNew.pack(side='left')
		eNew.insert(0, data[3])

		eDir = tk.Entry(dRow, width=10)
		eDir.pack(side='left', padx=(0, 10))
		eDir.insert(0, data[4])

		bDelete = tk.Button(dRow, text='x', fg='red', command=lambda: self.deleteInstructionRow(dRow))
		bDelete.pack(side='right')

		i.append(dRow)
		tagUp('instructionScrollable', frame, lID, eState, eRead, eWrite, eNew, eDir, bDelete)

		self.updateInstructionRows()
		self.updateInstructionCanvas()

	def updateInstructionRows(self):
		i = self.instructionRows

		for n, row in enumerate(i):
			for part in row.winfo_children():
				if type(part) == tk.Label:
					part['text'] = str(n+1)

	def deleteInstructionRow(self, row):
		i = self.instructionRows

		row.destroy()
		i.remove(row)
		self.updateInstructionRows()
		self.updateInstructionCanvas()

	def resetInstructions(self, ask=False):
		i = self.instructionRows
		w = self.widgets

		if not i:
			return

		if ask and not messagebox.askyesno('Reset Instructions', 'Delete all instructions?'):
			return

		frame = w['cdInstruction']

		for row in i:
			row.destroy()

		self.instructionRows = []

		self.updateInstructionCanvas()

	def addAccept(self, data=None):
		w = self.widgets
		a = self.acceptRows

		if data is None:
			data = ''

		frame = w['cdAccept']
		dRow = tk.Frame(frame, bg='blue')
		dRow.pack(side='top')

		lID = tk.Label(dRow, width=2)
		lID.pack(side='left', padx=(0, 5))

		eState = tk.Entry(dRow, width=9)
		eState.pack(side='left', padx=(0, 5))
		eState.insert(0, data)

		bDelete = tk.Button(dRow, text='x', fg='red', command=lambda: self.deleteAcceptRow(dRow))
		bDelete.pack(side='right')

		a.append(dRow)
		tagUp('acceptScrollable', frame, lID, eState, bDelete)

		self.updateAcceptRows()
		self.updateAcceptCanvas()

	def updateAcceptRows(self):
		a = self.acceptRows

		for n, row in enumerate(a):
			for part in row.winfo_children():
				if type(part) == tk.Label:
					part['text'] = str(n+1)

	def deleteAcceptRow(self, row):
		a = self.acceptRows

		row.destroy()
		a.remove(row)
		self.updateAcceptRows()
		self.updateAcceptCanvas()

	def resetAccepts(self, ask=False):
		a = self.acceptRows
		w = self.widgets

		if not a:
			return

		if ask and not messagebox.askyesno('Reset Accept States', 'Delete all accept states?'):
			return

		frame = w['cdAccept']

		for row in a:
			row.destroy()

		self.acceptRows = []

		self.updateAcceptCanvas()

	def shiftTape(self, shift):
		self.updateTapeData()

		self.tapePos += shift
		self.generateTapeWidgets()

	def resetTape(self, ask=False):
		w = self.widgets

		if ask and not messagebox.askyesno('Reset Tape', 'Reset entire tape?'):
			return

		self.tape = {}
		self.tapePos = 0
		self.generateTapeWidgets()

		setEntry(w['eGoto'], '')

	def updateTapeData(self):
		c = self.tapeCells
		t = self.tape

		for index in list(c.keys()):
			entry = c[index]
			char = entry.get()

			if not char:
				if index in t.keys():
					del t[index]
			else:
				t[str(index)] = char

	def goto(self, event=None):
		w = self.widgets

		eGoto = w['eGoto']

		newPos = eGoto.get()

		if isInt(newPos):
			self.updateTapeData()
			self.tapePos = int(newPos)
			self.generateTapeWidgets()

			setEntry(eGoto, '')

	def restoreDefaultSettings(self):
		w = self.widgets

		if messagebox.askyesno('Restore Defaults', 'Restore default simulation settings?'):
			setEntry(w['eWidth'], '700')
			setEntry(w['eHeight'], '600')
			setEntry(w['eCellSize'], '50')
			setEntry(w['eSpeed'], '1')
			setEntry(w['eFPS'], '100')

	def mouseWheel(self, event, canvas):
		canvas.yview_scroll(round(-1*(event.delta/120)), 'units')

	def importMachine(self):
		w = self.widgets

		file = filedialog.askopenfile(mode='r', filetypes =(('Machine Files', '*.machine'),))
		if file is not None:
			data = json.load(file)
			instructions = data['instructions']
			acceptStates = data['acceptStates']
			startState = data['startState']

			self.setInstructions(instructions)
			self.setAcceptStates(acceptStates)

			eStartState = w['eStartState']
			eStartState.delete(0, 'end')
			eStartState.insert(0, startState)

	def exportMachine(self):
		w = self.widgets

		instructions = self.getInstructions()
		acceptStates = self.getAcceptStates()
		startState = w['eStartState'].get()

		file = filedialog.asksaveasfile(filetypes=(('Machine Files', '*.machine'),), defaultextension='.machine')
		if not file is None:
			json.dump({'instructions':instructions, 'acceptStates':acceptStates, 'startState':startState}, file)
			file.close()

	def importTape(self):
		w = self.widgets

		file = filedialog.askopenfile(mode='r', filetypes =(('Tape Files', '*.tape'),))
		if file is not None:
			data = json.load(file)
			tape = data['tape']
			startPos = data['startPos']
			blankChar = data['blankChar']

			self.tape = tape
			setEntry(w['eStartPosition'], startPos)
			setEntry(w['eBlank'], blankChar)
			self.tapePos = int(startPos)

			self.generateTapeWidgets()

	def exportTape(self):
		w = self.widgets

		startPos = w['eStartPosition'].get()
		blankChar = w['eBlank'].get()

		self.updateTapeData()

		file = filedialog.asksaveasfile(filetypes=(('Tape Files', '*.tape'),), defaultextension='.tape')
		if not file is None:
			json.dump({'tape':self.tape, 'startPos':startPos, 'blankChar':blankChar}, file)
			file.close()

	def getInstructions(self):
		i = self.instructionRows

		instructions = []

		for row in i:
			instruction = []

			for i, part in enumerate(row.winfo_children()):
				if type(part) == tk.Entry:
					value = part.get()

					#Transforms blank entries into NoneType
					if not value:
						value = None

					#Allows L and R for direction
					if not value is None and i == 4:
						value = value.lower()

					instruction.append(value)

			instructions.append(instruction)

		return instructions

	def setInstructions(self, instructions):
		self.resetInstructions()

		for instruction in instructions:
			self.addInstruction(data=instruction)

	def getAcceptStates(self):
		a = self.acceptRows

		acceptStates = []

		for row in a:
			for part in row.winfo_children():
				if type(part) == tk.Entry:
					acceptStates.append(part.get())

		return acceptStates

	def setAcceptStates(self, acceptStates):
		self.resetAccepts()

		for state in acceptStates:
			self.addAccept(data=state)

	def execute(self, event=None):
		x = self.tabs
		w = self.widgets

		self.updateTapeData()

		instructions = self.getInstructions()
		valid, errorCell = checkInstructions(instructions)
		if not valid:
			row, cellTypeID = errorCell
			cellType = {
			0:'Current State',
			1:'Read',
			2:'Write',
			3:'Direction',
			4:'Next State'
			}[cellTypeID]

			messagebox.showwarning('Invalid Configuration', 'Instructions are invalid (check '+cellType+' at row '+str(row)+').')
			self.select(x['xMachine'])
			return

		acceptStates = self.getAcceptStates()
		valid, errorRow = checkAcceptStates(acceptStates)
		if not valid:
			messagebox.showwarning('Invalid Configuration', 'Accept states are invalid (check row '+str(errorRow)+').')
			self.select(x['xMachine'])
			return

		startState = w['eStartState'].get()
		if not startState:
			messagebox.showwarning('Invalid Configuration', 'Please specify a start state.')
			self.select(x['xMachine'])
			return

		tape = self.tape

		startPos = w['eStartPosition'].get()
		if not isInt(startPos):
			messagebox.showwarning('Invalid Configuration', 'Starting tape position must be an integer.')
			self.select(x['xTape'])
			return

		startPos = int(startPos)

		blankChar = w['eBlank'].get()

		width = w['eWidth'].get()
		if not isInt(width, False, False):
			messagebox.showwarning('Invalid Configuration', 'Width must be a positive integer.')
			return
		width = int(width)

		height = w['eHeight'].get()
		if not isInt(height, False, False):
			messagebox.showwarning('Invalid Configuration', 'Height must be a positive integer.')
			return
		height = int(height)

		cellSize = w['eCellSize'].get()
		if not isInt(cellSize, False, False):
			messagebox.showwarning('Invalid Configuration', 'Cell size must be a positive integer.')
			return
		cellSize = int(cellSize)

		speed = w['eSpeed'].get()
		if not isFloat(speed, False):
			messagebox.showwarning('Invalid Configuration', 'Speed must be a positive number.')
			return
		speed = float(speed)

		FPS = w['eFPS'].get()
		if not isInt(FPS, False, True):
			messagebox.showwarning('Invalid Configuration', 'FPS must be a positive integer (or 0 for no framerate cap).')
			return
		FPS = int(FPS)

		TuringSim.run(instructions, acceptStates, startState, tape, startPos, blankChar, (width, height), cellSize, speed, FPS)

def tagUp(tag, *args):
	for widget in args:
		widget.bindtags((tag,) + widget.bindtags())

def setEntry(entry, text):
	entry.delete(0, 'end')
	entry.insert(0, text)

def isInt(string, allowNegative=True, allowZero=True):
	if not allowZero and bool(re.match(r'^-?0+$', string)):
		return False

	if not allowNegative:
		return bool(re.match(r'^[0-9]+$', string))
	else:
		return bool(re.match(r'^-?[0-9]+$', string))

#Does not support negatives - they will always evaluate to false
def isFloat(string, allowZero=True):
	if not allowZero and bool(re.match(r'(^0$)|(^0+\.0*$)|(^0*\.0+$)', string)):
		return False

	return bool(re.match(r'(^[0-9]+$)|(^[0-9]+\.[0-9]*$)|(^[0-9]*\.[0-9]+$)', string))

def checkInstructions(instructions):
	for h, instruction in enumerate(instructions):
		for i, part in enumerate(instruction):
			#Current state and Next state
			if i == 0 or i == 4:
				if not part:
					return (False, (h+1, i))

			#Direction
			if i == 3:
				if not part in ['l', 'r']:
					return (False, (h+1, i))

	return (True, None)

def checkAcceptStates(acceptStates):
	for i, state in enumerate(acceptStates):
		if not state:
			return (False, i+1)

	return (True, None)

root = tk.Tk()
root.title('Turing Machine')
root.geometry('800x600')
app = Application(master=root)

app.mainloop()
