import tkinter as tk
import tkinter.font as font
from tkinter import ttk, filedialog, messagebox
import json
import simulator
import re

# = Widget prefix naming convention =
# d  - Frame (division)
# l  - Label
# c  - Canvas
# cd - Canvas frame (the frame that sits within a canvas)
# b  - Button
# e -  Entry

class Application(ttk.Notebook):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master

		# Load and store fonts
		self.fonts = {'large':font.Font(family='Helvetica', size=12, weight='bold')}

		self.tabs = {}				# Tabs of the application
		self.widgets = {}			# Widgets of the application that must be referenced by several methods
		self.instructionRows = []	# List of frames that contain widgets for an instruction row
		self.acceptRows = []		# List of frames that contain widgets for an accept row
		self.tapeCells = {}			# List of entry boxes used on the tape tab for the tape's cells
		self.tapeCellDivs = []		# List of frames that contain one of those entry boxes and the label for the position of the cell

		self.tapePos = 0			# Position of the cell at the center of the screen
		self.tape = {}				# Contains the info about non-default tape cells 	key: 	position of tape (str)
									#												  	value:	character at this position (str)

		# Initialise all tabs and all of their widgets
		self.createTabs()
		self.pack(side='top', expand=True, fill='both')

	# Initialises all tabs and all of their widgets
	def createTabs(self):
		x = self.tabs

		# Machine tab
		x['xMachine'] = machineTab = ttk.Frame(self)	# Create new tab frame and store it in the tabs dictionary
		self.machineTabWidgets(machineTab)				# Initialise all widgets
		self.add(machineTab, text='Machine')			# Add tab to notebook

		# Tape tab
		x['xTape'] = tapeTab = ttk.Frame(self)
		self.tapeTabWidgets(tapeTab)
		self.add(tapeTab, text='Tape')

		# Execute tab
		x['xExecute'] = executeTab = ttk.Frame(self)
		self.executeTabWidgets(executeTab)
		self.add(executeTab, text='Execute')

	# Initialises all widgets for the machine tab
	def machineTabWidgets(self, tab):
		w = self.widgets

		# Top frame
		dTop = tk.Frame(tab)
		dTop.pack(side='top', expand=True, fill='both')

		# Instruction frame
		dInstruction = tk.Frame(dTop, borderwidth=3, relief='sunken')
		dInstruction.pack(side='left', expand=True, fill='both')

		# Instruction scroll frame
		dInstructionScrollFrame = tk.Frame(dInstruction)
		dInstructionScrollFrame.pack(side='right', expand=True, fill='both')

		# Instruction column headers frame
		dLabels = tk.Frame(dInstructionScrollFrame)
		dLabels.pack(side='top', fill='x')

		# Instruction column header labels
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

		# Instruction scroll canvas
		w['cInstruction'] = cInstruction = tk.Canvas(dInstructionScrollFrame, height=100)

		# Instruction scrollbar
		scrollbar = tk.Scrollbar(dInstruction, orient='vertical', command=cInstruction.yview)
		scrollbar.pack(side='left', fill='y')
		# Bind scrollbar to scroll canvas
		cInstruction.configure(yscrollcommand=scrollbar.set)
		cInstruction.pack(side='top', expand=True, fill='both')

		# Instruction canvas frame
		w['cdInstruction'] = cdInstruction = tk.Frame(cInstruction)

		# Bind canvas frame to canvas
		cInstruction.create_window((0, 0), window=cdInstruction, anchor='nw')
		# Bind scroll event to sliding the canvas frame
		tagUp('instructionScrollable', cdInstruction, cInstruction)
		tab.bind_class('instructionScrollable', '<MouseWheel>', lambda event, canvas=cInstruction: self.mouseWheel(event, canvas))

		cdInstruction.update_idletasks()
		cInstruction.config(scrollregion=cInstruction.bbox("all"))

		# Right frame
		dRight = tk.Frame(dTop)
		dRight.pack(side='left', fill='y')

		# Accept states frame
		dAccept = tk.Frame(dRight, borderwidth=3, relief='sunken')
		dAccept.pack(side='bottom')

		# Accept states scroll frame
		dAcceptScrollFrame = tk.Frame(dAccept)
		dAcceptScrollFrame.pack(side='right', anchor='nw', expand=True, fill='both')

		# Accept states label frame
		dLabel = tk.Frame(dAcceptScrollFrame)
		dLabel.pack(side='top', fill='x')

		# Accept states label
		lState = tk.Label(dLabel, text='Accept States')
		lState.pack(side='left')

		# Accept states scroll canvas
		w['cAccept'] = cAccept = tk.Canvas(dAcceptScrollFrame, width=105, height=140)

		# Accept states scrollbar
		scrollbar = tk.Scrollbar(dAccept, orient='vertical', command=cAccept.yview)
		scrollbar.pack(side='left', fill='y')
		# Bind scrollbar to scroll canvas
		cAccept.configure(yscrollcommand=scrollbar.set)
		cAccept.pack(side='top', expand=True, fill='both')

		# Accept states canvas frame
		w['cdAccept'] = cdAccept = tk.Frame(cAccept)

		# Bind canvas frame to canvas
		cAccept.create_window((0, 0), window=cdAccept, anchor='nw')
		# Bind scroll event to sliding the canvas frame
		tagUp('acceptScrollable', cdAccept, cAccept)
		tab.bind_class('acceptScrollable', '<MouseWheel>', lambda event, canvas=cAccept: self.mouseWheel(event, canvas))

		cdAccept.update_idletasks()
		cAccept.config(scrollregion=cAccept.bbox("all"))

		# File options frame
		dFile = tk.Frame(dRight)
		dFile.pack(side='right', fill='y')

		# Import button
		bImport = tk.Button(dFile, text='Import Instructions', command=self.importMachine)
		bImport.pack(side='top')
		# Export button
		bExport = tk.Button(dFile, text='Export Instructions', command=self.exportMachine)
		bExport.pack(side='top', fill='x')

		# Instruction buttons frame
		dInstructionButton = tk.Frame(dInstructionScrollFrame)
		dInstructionButton.pack(side='top', fill='both')

		# Add instruction button
		bAddInstruction = tk.Button(dInstructionButton, text='Add', command=self.addInstruction)
		bAddInstruction.pack(side='left')
		# Reset instructions button
		bResetInstructions = tk.Button(dInstructionButton, text='Reset', fg='red', command=lambda: self.resetInstructions(True))
		bResetInstructions.pack(side='left')

		# Accept state buttons frame
		dAcceptButton = tk.Frame(dAcceptScrollFrame)
		dAcceptButton.pack(side='top', fill='both')

		# Add accept state button
		bAddAccept = tk.Button(dAcceptButton, text='Add', command=self.addAccept)
		bAddAccept.pack(side='left')
		# Reset accept states button
		bResetAccepts = tk.Button(dAcceptButton, text='Reset', fg='red', command=lambda: self.resetAccepts(True))
		bResetAccepts.pack(side='left')

		# Bottom frame
		dInput = tk.Frame(tab)
		dInput.pack(side='top', fill='x')

		# Start state control frame
		dStart = tk.Frame(dInput)
		dStart.pack(side='left')

		# Start state label
		lStart = tk.Label(dStart, text='Start State:')
		lStart.pack(side='left')
		# Start state entry
		w['eStartState'] = eStart = tk.Entry(dStart, width=5)
		eStart.pack(side='left')

	# Initialises all widgets for the tape tab
	def tapeTabWidgets(self, tab):
		w = self.widgets

		# Top frame
		dTop = tk.Frame(tab)
		dTop.pack(side='top', expand=True, fill='both')

		# Tape control frame
		dTape = tk.Frame(dTop)
		dTape.pack(side='bottom', expand=True)

		# Tape head label
		lHead = tk.Label(dTape, text='▼')
		lHead.pack(side='top')

		# File options frame
		dFile = tk.Frame(dTop)
		dFile.pack(side='top', fill='x')

		# File buttons frame
		dFileButtons = tk.Frame(dFile)
		dFileButtons.pack(side='right')

		# Import button
		bImport = tk.Button(dFileButtons, text='Import Tape', command=self.importTape)
		bImport.pack(side='top')
		# Export button
		bExport = tk.Button(dFileButtons, text='Export Tape', command=self.exportTape)
		bExport.pack(side='top', fill='x')

		# Cells frame
		w['dCells'] = dCells = tk.Frame(dTape)
		dCells.pack(side='top', expand=True, fill='x')

		# Shift tape buttons frame
		dShift = tk.Frame(dTape)
		dShift.pack(side='top', pady=(0, 20))

		# Shift tape left button
		bShiftLeft = tk.Button(dShift, text='<', width=3, command=lambda: self.shiftTape(-1))
		bShiftLeft.pack(side='left')
		# Shift tape right button
		bShiftRight = tk.Button(dShift, text='>', width=3, command=lambda: self.shiftTape(1))
		bShiftRight.pack(side='right')

		# Access control frame
		dAccess = tk.Frame(dTape)
		dAccess.pack(side='top', fill='x')

		# Goto widgets frame
		dGoto = tk.Frame(dAccess)
		dGoto.pack(side='left')

		# Goto label
		lGoto = tk.Label(dGoto, text='Jump To:')
		lGoto.pack(side='left')
		# Goto entry box
		w['eGoto'] = eGoto = tk.Entry(dGoto, width=5)
		eGoto.pack(side='left', padx=(0, 5))
		# Bind enter key to goto method
		eGoto.bind('<Return>', self.goto)
		# Goto button
		bGoto = tk.Button(dGoto, text='Jump', command=self.goto)
		bGoto.pack(side='left')

		# Reset tape button
		bReset = tk.Button(dAccess, text='Reset', fg='red', command=lambda: self.resetTape(True))
		bReset.pack(side='right')

		# Other inputs frame
		dInput = tk.Frame(tab)
		dInput.pack(side='top', fill='x')

		# Start position frame
		dStart = tk.Frame(dInput)
		dStart.pack(side='left')

		# Start position label
		lStart = tk.Label(dStart, text='Start Position:')
		lStart.pack(side='left')
		# Start position entry box
		w['eStartPosition'] = eStart = tk.Entry(dStart, width=5)
		eStart.pack(side='left')

		# Blank character frame
		dBlank = tk.Frame(dInput)
		dBlank.pack(side='left')

		# Blank character label
		lBlank = tk.Label(dBlank, text='Blank Character:')
		lBlank.pack(side='left')
		# Blank character entry box
		w['eBlank'] = eBlank = tk.Entry(dBlank, width=5)
		eBlank.pack(side='left')

		# Generate the tape character entry widgets (the dynamic aspect of the tab)
		self.generateTapeWidgets()

	# Initialises all widgets for the execute tab
	def executeTabWidgets(self, tab):
		w = self.widgets

		# Main frame
		dMain = tk.Frame(tab)
		dMain.pack(side='top', expand=True)

		# Sizing control frame
		dSizing = tk.Frame(dMain)
		dSizing.pack(side='top', pady=(10, 5))

		# Dimension control frame
		dDim = tk.Frame(dSizing, borderwidth=1, relief='groove')
		dDim.pack(side='left', padx=(0, 40))

		# Width label
		lWidth = tk.Label(dDim, text='Width:')
		lWidth.pack(side='left')
		# Width entry box
		w['eWidth'] = eWidth = tk.Entry(dDim, takefocus=False, width=5)
		eWidth.pack(side='left')
		# Bind enter key to execute method
		eWidth.bind('<Return>', self.execute)
		# Set default value
		eWidth.insert(0, '800')

		# Height label
		lHeight = tk.Label(dDim, text='Height:')
		lHeight.pack(side='left')
		# Height entry box
		w['eHeight'] = eHeight = tk.Entry(dDim, takefocus=False, width=5)
		eHeight.pack(side='left')
		# Bind enter key to execute method
		eHeight.bind('<Return>', self.execute)
		# Set default value
		eHeight.insert(0, '600')

		# Cell size control frame
		dCellSize = tk.Frame(dSizing)
		dCellSize.pack(side='left')

		# Cell size label
		lCellSize = tk.Label(dCellSize, text='Cell Size:')
		lCellSize.pack(side='left')
		# Cell size entry box
		w['eCellSize'] = eCellSize = tk.Entry(dCellSize, takefocus=False, width=4)
		eCellSize.pack(side='left')
		# Bind enter key to execute method
		eCellSize.bind('<Return>', self.execute)
		# Set defualt value
		eCellSize.insert(0, '50')

		# Pacing control frame
		dPacing = tk.Frame(dMain)
		dPacing.pack(side='top', pady=(5, 10))

		# Speed control frame
		dSpeed = tk.Frame(dPacing)
		dSpeed.pack(side='left', padx=(0, 10))

		# Speed label
		lSpeed = tk.Label(dSpeed, text='Speed:')
		lSpeed.pack(side='left')
		# Speed entry box
		w['eSpeed'] = eSpeed = tk.Entry(dSpeed, takefocus=False, width=4)
		eSpeed.pack(side='left')
		# Bind enter key to execute method
		eSpeed.bind('<Return>', self.execute)
		# Set default value
		eSpeed.insert(0, '1')

		# FPS control frame
		dFPS = tk.Frame(dPacing)
		dFPS.pack(side='left')

		# FPS label
		lFPS = tk.Label(dFPS, text='FPS:')
		lFPS.pack(side='left')
		# FPS entry box
		w['eFPS'] = eFPS = tk.Entry(dFPS, takefocus=False, width=5)
		eFPS.pack(side='left')
		# Bind enter key to execute method
		eFPS.bind('<Return>', self.execute)
		# Set default value
		eFPS.insert(0, '100')

		# Reset button
		bReset = tk.Button(dMain, text='Restore Defaults', takefocus=False, command=self.restoreDefaultSettings)
		bReset.pack(side='top', pady=10)

		# Execute button
		bExecute = tk.Button(dMain, text='Execute', font=self.fonts['large'], command=self.execute)
		bExecute.pack(side='top', fill='x', pady=30)
		# Bind enter key to execute method
		bExecute.bind('<Return>', self.execute)

	# Generates tape character entry widgets
	def generateTapeWidgets(self):
		t = self.tape
		w = self.widgets
		# Initialise dictionary
		c = self.tapeCells = {}
		d = self.tapeCellDivs

		# Destroy all tape cell frames
		for div in d:
			div.destroy()
		# Initialise dictionary
		d = self.tapeCellDivs = []

		frame = w['dCells']

		# Number of cells shown either side of central one
		sideCells = 5

		# Create all cells and labels
		for i in range(-sideCells, sideCells+1):
			pos = self.tapePos + i
			cellFrame = tk.Frame(frame)
			cellFrame.pack(side='left', expand=True)

			# Create character entry box
			cell = tk.Entry(cellFrame, justify='center', width=5)
			cell.pack(side='top', expand=True)

			# If cell at given position has a defined (non-default) character:
			if str(pos) in t.keys():
				char = t[str(pos)]
				# Set entry to the char
				cell.insert(0, char)

			# Create position label
			label = tk.Label(cellFrame, text=str(pos))
			label.pack(side='top')

			# Add cell entry box to dictionary
			c[str(pos)] = cell
			# Add cell frame to list
			d.append(cellFrame)

	# Updates and re-renders instruction canvas
	def updateInstructionCanvas(self):
		w = self.widgets
		i = self.instructionRows

		frame = w['cdInstruction']
		canvas = w['cInstruction']

		# If no instructons are defined:
		if not i:
			frame['height'] = 1

		frame.update_idletasks()
		canvas.config(scrollregion=canvas.bbox("all"))

	# Updates and re-renders accept state canvas
	def updateAcceptCanvas(self):
		w = self.widgets
		a = self.acceptRows

		frame = w['cdAccept']
		canvas = w['cAccept']

		# If no accept states are defined:
		if not a:
			frame['height'] = 1

		frame.update_idletasks()
		canvas.config(scrollregion=canvas.bbox("all"))

	# Add an instruction row
	def addInstruction(self, data=('', '', '', '', '')):
		w = self.widgets
		i = self.instructionRows

		# Get the instruction canvas frame
		frame = w['cdInstruction']

		# Row frame (contains everything)
		dRow = tk.Frame(frame)
		dRow.pack(side='top')

		# ID label
		lID = tk.Label(dRow, width=2)
		lID.pack(side='left', padx=(0, 10))

		# State entry box
		eState = tk.Entry(dRow, width=10)
		eState.pack(side='left')
		# Fill with value (won't be filled if add instruction button was clicked)
		eState.insert(0, data[0])

		# Read entry box
		eRead = tk.Entry(dRow, width=10)
		eRead.pack(side='left', padx=(0, 10))
		# Fill with value (won't be filled if add instruction button was clicked)
		if not data[1] is None:
			eRead.insert(0, data[1])

		# Write entry box
		eWrite = tk.Entry(dRow, width=10)
		eWrite.pack(side='left')
		# Fill with value (won't be filled if add instruction button was clicked)
		if not data[2] is None:
			eWrite.insert(0, data[2])

		# Direction entry box
		eDir = tk.Entry(dRow, width=10)
		eDir.pack(side='left')
		# Fill with value (won't be filled if add instruction button was clicked)
		eDir.insert(0, data[3])

		# Next state entry box
		eNew = tk.Entry(dRow, width=10)
		eNew.pack(side='left', padx=(0, 10))
		# Fill with value (won't be filled if add instruction button was clicked)
		eNew.insert(0, data[4])

		# Delete button
		bDelete = tk.Button(dRow, text='x', fg='red', command=lambda: self.deleteInstructionRow(dRow))
		bDelete.pack(side='right')

		# Add to list of instruction rows
		i.append(dRow)
		# Bind scrolling to all widgets
		tagUp('instructionScrollable', frame, lID, eState, eRead, eWrite, eDir, eNew, bDelete)

		# Update tab
		self.updateInstructionRows()
		self.updateInstructionCanvas()

	# Updates all ID labels for instruction rows after adding or deleting a row
	def updateInstructionRows(self):
		i = self.instructionRows

		for n, row in enumerate(i):
			for part in row.winfo_children():
				if type(part) == tk.Label:		# If the current widget is a label:
					part['text'] = str(n+1)		# Update its value
					break						# Stop checking the rest of the widgets for this row

	# Deletes the instruction row after clicking the delete button
	def deleteInstructionRow(self, row):
		i = self.instructionRows

		# Destroy frame and all of its children
		row.destroy()
		i.remove(row)
		# Update tab
		self.updateInstructionRows()
		self.updateInstructionCanvas()

	# Deletes all instruction rows
	def resetInstructions(self, ask=False):
		i = self.instructionRows
		w = self.widgets

		# If there are no instructions:
		if not i:
			return

		# Ask for confirmation before continuing
		if ask and not messagebox.askyesno('Reset Instructions', 'Delete all instructions?'):
			return

		frame = w['cdInstruction']

		# Destroy all frames and their children
		for row in i:
			row.destroy()

		# Initialise list
		self.instructionRows = []

		# Update tab
		self.updateInstructionCanvas()

	# Add an accept state row
	def addAccept(self, data=None):
		w = self.widgets
		a = self.acceptRows

		# If no data was passed in (occurs when the add accept state button is clicked)
		if data is None:
			data = ''

		# Get the accept state canvas frame
		frame = w['cdAccept']

		# Row frame (contains everything)
		dRow = tk.Frame(frame)
		dRow.pack(side='top')

		# ID label
		lID = tk.Label(dRow, width=2)
		lID.pack(side='left', padx=(0, 5))

		# State entry
		eState = tk.Entry(dRow, width=9)
		eState.pack(side='left', padx=(0, 5))
		# Fill with value (won't be filled if add instruction button was clicked)
		eState.insert(0, data)

		# Delete button
		bDelete = tk.Button(dRow, text='x', fg='red', command=lambda: self.deleteAcceptRow(dRow))
		bDelete.pack(side='right')

		# Add to list of accept state rows
		a.append(dRow)
		# Bind scrolling to all widgets
		tagUp('acceptScrollable', frame, lID, eState, bDelete)

		# Update tab
		self.updateAcceptRows()
		self.updateAcceptCanvas()

	# Updates all ID labels for accept state rows after adding or deleting a row
	def updateAcceptRows(self):
		a = self.acceptRows

		for n, row in enumerate(a):
			for part in row.winfo_children():
				if type(part) == tk.Label:		# If the current widget is a label:
					part['text'] = str(n+1)		# Update its value
					break						# Stop checking the rest of the widgets for this row

	# Deletes the accept state row after clicking the delete button
	def deleteAcceptRow(self, row):
		a = self.acceptRows

		# Destroy frame and all of its children
		row.destroy()
		a.remove(row)
		# Update tab
		self.updateAcceptRows()
		self.updateAcceptCanvas()

	# Deletes all accept state rows
	def resetAccepts(self, ask=False):
		a = self.acceptRows
		w = self.widgets

		# If there are no accept states:
		if not a:
			return

		# Ask for confirmation before continuing
		if ask and not messagebox.askyesno('Reset Accept States', 'Delete all accept states?'):
			return

		frame = w['cdAccept']

		# Destroy all frames and their children
		for row in a:
			row.destroy()

		# Initialise list
		self.acceptRows = []

		# Update tab
		self.updateAcceptCanvas()

	# Shifts the tape one cell across
	def shiftTape(self, shift):
		# Store any edits made
		self.updateTapeData()

		self.tapePos += shift
		self.generateTapeWidgets()

	# Clears the entire tape and sets tape position back to 0
	def resetTape(self, ask=False):
		w = self.widgets

		# Ask for confirmation before continuing
		if ask and not messagebox.askyesno('Reset Tape', 'Reset entire tape?'):
			return

		self.tape = {}						# Initialise tape dictionary
		self.tapePos = 0					# Initialise tape position
		setEntry(w['eStartPosition'], '')	# Clear start position entry box
		setEntry(w['eBlank'], '')			# Clear blank character entry box
		setEntry(w['eGoto'], '')			# Clear goto entry box

		self.generateTapeWidgets()

	# Reads from the tape entry cells and updates the tape dictionary
	def updateTapeData(self):
		c = self.tapeCells
		t = self.tape

		# For every tape cell entry box on screen:
		for index in list(c.keys()):
			entry = c[index]			# Get the entry box object
			char = entry.get()			# Get the string typed inside the entry box

			if not char:				# If string is empty:
				if index in t.keys():	# If there is an existing entry in the tape dictionary at this cell position:
					del t[index]		# Delete that entry (because blank (default) cells are not stored in the dictionary)

			else:						# If string is non-empty:
				t[str(index)] = char	# Store the entered string in the tape dictionary

	# Jumps to the entered position on the tape
	def goto(self, event=None):
		w = self.widgets

		# Get the entry box
		eGoto = w['eGoto']

		# Get the entered string from the box
		newPos = eGoto.get()

		if isInt(newPos):				# If the entered string is an integer:
			self.updateTapeData()		# Store any edits made
			self.tapePos = int(newPos)	# Set the sape position
			self.generateTapeWidgets()

			setEntry(eGoto, '')			# Clear the entry box

	# Restores the default settings in the execute tab
	def restoreDefaultSettings(self):
		w = self.widgets

		# Ask for confiirmation before continuing
		if messagebox.askyesno('Restore Defaults', 'Restore default simulation settings?'):
			# Set entry boxes to their default values
			setEntry(w['eWidth'], '800')
			setEntry(w['eHeight'], '600')
			setEntry(w['eCellSize'], '50')
			setEntry(w['eSpeed'], '1')
			setEntry(w['eFPS'], '100')

	# Maps the mouse scroll inputs and scrolls the canvas
	def mouseWheel(self, event, canvas):
		canvas.yview_scroll(round(-1*(event.delta/120)), 'units')

	# Imports a machine definition from an external file
	def importMachine(self):
		w = self.widgets

		# Open the operating system's file explorer
		file = filedialog.askopenfile(mode='r', filetypes =(('Machine Files', '*.machine'),))
		if file is not None:					# If user actually selected a file (and did not close the file explorer)
			data = json.load(file)				# Load JSON data from the file
			instructions = data['instructions']	# Get instructions
			acceptStates = data['acceptStates']	# Get accept states
			startState = data['startState']		# Get start state

			self.setInstructions(instructions)	# Creates instruction rows
			self.setAcceptStates(acceptStates)	# Creates accept state rows

			# Sets the start state
			eStartState = w['eStartState']		# Get start state entry box
			eStartState.delete(0, 'end')		# Clear entry
			eStartState.insert(0, startState)	# Set to start state from file

	# Reads entered data and exports the machine to an external file
	def exportMachine(self):
		w = self.widgets

		instructions = self.getInstructions()	# Get all instructions
		acceptStates = self.getAcceptStates()	# Get all accept states
		startState = w['eStartState'].get()		# Get start state

		# Open the operating system's file explorer
		file = filedialog.asksaveasfile(filetypes=(('Machine Files', '*.machine'),), defaultextension='.machine')
		if not file is None:												# If user actually selected a file (and did not close the file explorer)
			json.dump({'instructions':instructions,							# Compose dictionary and dump into json file
			'acceptStates':acceptStates, 'startState':startState}, file)
			file.close()

	# Imports a tape from an external file
	def importTape(self):
		w = self.widgets

		# Open the operating system's file explorer
		file = filedialog.askopenfile(mode='r', filetypes =(('Tape Files', '*.tape'),))
		if file is not None:						# If user actually selected a file (and did not close the file explorer)
			data = json.load(file)					# Load JSON data from the file
			tape = data['tape']						# Get tape data
			startPos = data['startPos']				# Get start position
			blankChar = data['blankChar']			# Get blank character

			self.tape = tape						# Set tape dictionary
			setEntry(w['eStartPosition'], startPos)	# Set start position entry
			setEntry(w['eBlank'], blankChar)		# Set blank character entry

			if isInt(startPos):						# If the start position is an integer:
				self.tapePos = int(startPos)		# Set the tape position to the start position
			else:									# Otherwise:
				self.tapePos = 0					# Set the tape position to 0

			self.generateTapeWidgets()

	# Reads entered data and exports the tape to an external file
	def exportTape(self):
		w = self.widgets

		startPos = w['eStartPosition'].get()	# Get start position
		blankChar = w['eBlank'].get()			# Get blank character

		self.updateTapeData()	# Store any edits made to the tape

		# Open the operating system's file explorer
		file = filedialog.asksaveasfile(filetypes=(('Tape Files', '*.tape'),), defaultextension='.tape')
		if not file is None:									# If user actually selected a file (and did not close the file explorer)
			json.dump({'tape':self.tape, 'startPos':startPos,	# Compose dictionary and dump into json file
			'blankChar':blankChar}, file)
			file.close()

	# Reads all entered instructions and compiles them into a list
	def getInstructions(self):
		i = self.instructionRows

		instructions = []

		# For every instruction row:
		for row in i:
			instruction = []

			# For every widget within the row:
			for i, part in enumerate(row.winfo_children()):
				if type(part) == tk.Entry:	# If current widget is an entry box:
					value = part.get()		# Get the entry

					# Converts blank entries into NoneType
					if not value:
						value = None

					# Allows L and R for direction
					if not value is None and i == 4:
						value = value.lower()

					instruction.append(value)

			instructions.append(instruction)

		return instructions

	# Takes a list of instructions and creates the instruction rows
	def setInstructions(self, instructions):
		# Clear instruction rows
		self.resetInstructions()

		# Add a new instruction row for every instruction in the list
		for instruction in instructions:
			self.addInstruction(data=instruction)

	# Reads all entered accept states and compiles them into a list
	def getAcceptStates(self):
		a = self.acceptRows

		acceptStates = []

		# For every accept state row:
		for row in a:
			# For every widget within the row:
			for part in row.winfo_children():
				if type(part) == tk.Entry:			# If current widget is an entry box:
					acceptStates.append(part.get())	# Get the entry and add it to the list

		return acceptStates

	# Takes a list of accept states and creates the accept state rows
	def setAcceptStates(self, acceptStates):
		# Clear instruction rows
		self.resetAccepts()

		# Add a new accept state row for every accept state in the list
		for state in acceptStates:
			self.addAccept(data=state)

	# Reads all of the entered data, checks all inputs are valid and starts the simulation
	def execute(self, event=None):
		x = self.tabs
		w = self.widgets

		# Stores any edits made to the tape
		self.updateTapeData()

		instructions = self.getInstructions()				# Get instructions
		valid, errorCell = checkInstructions(instructions)	# Check instructions

		# If the instructions are invalid:
		if not valid:
			# Decode the location of the error
			row, cellTypeID = errorCell
			cellType = {
			0:'Current State',
			1:'Read',
			2:'Write',
			3:'Direction',
			4:'Next State'
			}[cellTypeID]

			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'Instructions are invalid (check '+cellType+' at row '+str(row)+').')
			# Take user to the machine tab
			self.select(x['xMachine'])
			return

		acceptStates = self.getAcceptStates()				# Get accept states
		valid, errorRow = checkAcceptStates(acceptStates)	# Check accept states

		# If accept states are invalid:
		if not valid:

			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'Accept states are invalid (check row '+str(errorRow)+').')
			# Take user to tape tab
			self.select(x['xMachine'])
			return

		# Get start state
		startState = w['eStartState'].get()
		# If start state is blank:
		if not startState:
			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'Please specify a start state.')
			# Take user to the machine tab
			self.select(x['xMachine'])
			return

		tape = self.tape

		# Get start position
		startPos = w['eStartPosition'].get()
		#If start position is not an integer:
		if not isInt(startPos):
			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'Starting tape position must be an integer.')
			# Take user to the tape tab
			self.select(x['xTape'])
			return

		startPos = int(startPos)	# Convert start position to an integer

		# Get blank character
		blankChar = w['eBlank'].get()

		# Get width
		width = w['eWidth'].get()
		# If width is not a non-negative, non-zero integer:
		if not isInt(width, False, False):
			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'Width must be a positive integer.')
			return
		width = int(width)	# Convert width to an integer
		# If width is too large:
		if width > 2000:
			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'Width is too large (maximum is 2000).')
			return

		# Get height
		height = w['eHeight'].get()
		# If height is not a non-negative, non-zero integer:
		if not isInt(height, False, False):
			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'Height must be a positive integer.')
			return
		height = int(height)	# Convert height to an integer
		# If height is too large:
		if height > 2000:
			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'Height is too large (maximum is 2000).')
			return

		# Get cell size
		cellSize = w['eCellSize'].get()
		# If cell size is not a non-negative, non-zero integer:
		if not isInt(cellSize, False, False):
			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'Cell size must be a positive integer.')
			return
		cellSize = int(cellSize)	# Convert cell size to an integer

		# Get speed
		speed = w['eSpeed'].get()
		# If speed is not a non-negative, non-zero number:
		if not isFloat(speed, False):
			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'Speed must be a positive number.')
			return
		speed = float(speed)	# Convert speed to a float

		# Get FPS
		FPS = w['eFPS'].get()
		# If FPS is not a non-negative, non-zer integer:
		if not isInt(FPS, False, True):
			# Display an error message
			messagebox.showwarning('Invalid Configuration', 'FPS must be a positive integer (or 0 for no framerate cap).')
			return
		FPS = int(FPS)	# Convert FPS to an integer

		# Run the simulation
		simulator.run(instructions, acceptStates, startState, tape, startPos, blankChar, (width, height), cellSize, speed, FPS)

# Takes a tag and applies it to all given widgets
def tagUp(tag, *args):
	for widget in args:
		widget.bindtags((tag,) + widget.bindtags())

# Sets the contents of the given entry box to the given string
def setEntry(entry, text):
	entry.delete(0, 'end')
	entry.insert(0, text)

# Checks if the given string is a valid integer
def isInt(string, allowNegative=True, allowZero=True):
	# If zero not allowed and string is zero of some form:
	if not allowZero and bool(re.match(r'^-?0+$', string)):
		return False

	# If negatives not allowed:
	if not allowNegative:
		return bool(re.match(r'^[0-9]+$', string))		# Only matches positive integers of some form
	else:
		return bool(re.match(r'^-?[0-9]+$', string))	# Matches all integers of some form

# Checks if the given string is a valid decimal number
# Does not support negatives - they will always evaluate to False
def isFloat(string, allowZero=True):
	# If zero not allowed and string is zero of some form:
	if not allowZero and bool(re.match(r'(^0$)|(^0+\.0*$)|(^0*\.0+$)', string)):
		return False

	return bool(re.match(r'(^[0-9]+$)|(^[0-9]+\.[0-9]*$)|(^[0-9]*\.[0-9]+$)', string))	# Matches all positive decimal numbers of some form

# Checks if the given list of instructions is valid
#
# = Format of return value =
# If all instructions valid: 			(True, None)
# If at least one instruction invalid:	(False, (invalid instruction row number, index of column of invalid instruction part))
def checkInstructions(instructions):
	# For every instruction in the list:
	for h, instruction in enumerate(instructions):
		# For every part of the current instruction:
		for i, part in enumerate(instruction):
			if i == 0 or i == 4:				# If the current part is the current state or the next state:
				if not part:					# If blank:
					return (False, (h+1, i))

			if i == 3:							# If the current part is the direction:
				if not part in ['l', 'r']:		# If not left or right:
					return (False, (h+1, i))

	return (True, None)

# Checks if the given list of accept states is valid
#
# = Format of return value =
# If all accept states valid: 			(True, None)
# If at least one accept state invalid:	(False, invalid accept state row number)
def checkAcceptStates(acceptStates):
	# For every accept state in the list:
	for i, state in enumerate(acceptStates):
		if not state:				# If blank:
			return (False, i+1)

	return (True, None)

root = tk.Tk()					# Create tkinter root object
root.title('Turing Machine')	# Set window title
root.geometry('550x320')		# Set window dimensions
app = Application(master=root)	# Create application instance

app.mainloop()
