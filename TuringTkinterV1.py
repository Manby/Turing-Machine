import tkinter as tk
from tkinter import ttk, filedialog
import json
import TuringMachine
import re

class Application(ttk.Notebook):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master

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
		machineTab = ttk.Frame(self)
		self.machineTabWidgets(machineTab)
		self.add(machineTab, text='Machine')

		tapeTab = ttk.Frame(self)
		self.tapeTabWidgets(tapeTab)
		self.add(tapeTab, text='Tape')

		executeTab = ttk.Frame(self)
		self.executeTabWidgets(executeTab)
		self.add(executeTab, text='Execute')

	def machineTabWidgets(self, tab):
		w = self.widgets

		dTop = tk.Frame(tab)
		dTop.pack(side='top', expand=True, fill='both')

		dInstruction = tk.Frame(dTop)
		dInstruction.pack(side='left', expand=True, fill='both')

		dInstructionScrollFrame = tk.Frame(dInstruction)
		dInstructionScrollFrame.pack(side='right', expand=True, fill='both')

		dLabels = tk.Frame(dInstructionScrollFrame)
		dLabels.pack(side='top', fill='x')

		lState = tk.Label(dLabels, text='State')
		lState.pack(side='left', padx=(0, 34))
		lRead = tk.Label(dLabels, text='Read')
		lRead.pack(side='left', padx=(0, 42))
		lWrite = tk.Label(dLabels, text='Write')
		lWrite.pack(side='left', padx=(0, 29))
		lDir = tk.Label(dLabels, text='Direction')
		lDir.pack(side='left', padx=(0, 11))
		lNext = tk.Label(dLabels, text='Next State')
		lNext.pack(side='left')

		w['cInstruction'] = cInstruction = tk.Canvas(dInstructionScrollFrame)

		scrollbar = tk.Scrollbar(dInstruction, orient='vertical', command=cInstruction.yview)
		scrollbar.pack(side='left', fill='y')
		cInstruction.configure(yscrollcommand=scrollbar.set)
		cInstruction.pack(side='top', expand=True, fill='both')

		w['cdInstruction'] = cdInstruction = tk.Frame(cInstruction)

		cInstruction.create_window((0, 0), window=cdInstruction, anchor='nw')
		tagUp('instructionScrollable', cdInstruction)
		tab.bind_class('instructionScrollable', '<MouseWheel>', lambda event, canvas=cInstruction: self.mouseWheel(event, canvas))

		cdInstruction.update_idletasks()

		cInstruction.config(scrollregion=cInstruction.bbox("all"))

		dRight = tk.Frame(dTop)
		dRight.pack(side='left', fill='y')

		dAccept = tk.Frame(dRight)
		dAccept.pack(side='top')

		dAcceptScrollFrame = tk.Frame(dAccept)
		dAcceptScrollFrame.pack(side='right', anchor='nw', expand=True, fill='both')

		dLabel = tk.Frame(dAcceptScrollFrame)
		dLabel.pack(side='top', fill='x')

		lState = tk.Label(dLabel, text='Accept State')
		lState.pack(side='left')

		w['cAccept'] = cAccept = tk.Canvas(dAcceptScrollFrame, width=100)

		scrollbar = tk.Scrollbar(dAccept, orient='vertical', command=cAccept.yview)
		scrollbar.pack(side='left', fill='y')
		cAccept.configure(yscrollcommand=scrollbar.set)
		cAccept.pack(side='top', expand=True, fill='both')

		w['cdAccept'] = cdAccept = tk.Frame(cAccept)

		cAccept.create_window((0, 0), window=cdAccept, anchor='nw')
		tagUp('acceptScrollable', cdAccept)
		tab.bind_class('acceptScrollable', '<MouseWheel>', lambda event, canvas=cAccept: self.mouseWheel(event, canvas))

		cdAccept.update_idletasks()

		cAccept.config(scrollregion=cAccept.bbox("all"))

		dFile = tk.Frame(dTop)
		dFile.pack(side='right', fill='y')

		bImport = tk.Button(dFile, text='Import Instructions', command=self.importMachine)
		bImport.pack(side='top')
		bExport = tk.Button(dFile, text='Export Instructions', command=self.exportMachine)
		bExport.pack(side='top', fill='x')

		dInstructionButton = tk.Frame(dInstructionScrollFrame)
		dInstructionButton.pack(side='top', fill='both')

		bAddInstruction = tk.Button(dInstructionButton, text='Add', command=self.addInstruction)
		bAddInstruction.pack(side='left')
		bResetInstructions = tk.Button(dInstructionButton, text='Reset', command=self.resetInstructions)
		bResetInstructions.pack(side='left')

		dAcceptButton = tk.Frame(dAcceptScrollFrame)
		dAcceptButton.pack(side='top', fill='both')

		bAddAccept = tk.Button(dAcceptButton, text='Add', command=self.addAccept)
		bAddAccept.pack(side='left')
		bResetAccepts = tk.Button(dAcceptButton, text='Reset', command=self.resetAccepts)
		bResetAccepts.pack(side='left')

		dInput = tk.Frame(tab)
		dInput.pack(side='top', fill='x')

		dStart = tk.Frame(dInput)
		dStart.pack(side='left')

		lStart = tk.Label(dStart, text='Start State:')
		lStart.pack(side='left')
		w['eStartState'] = eStart = tk.Entry(dStart, width=5)
		eStart.pack(side='left')

	def tapeTabWidgets(self, tab):
		w = self.widgets

		dTop = tk.Frame(tab)
		dTop.pack(side='top', expand=True, fill='both')

		dTape = tk.Frame(dTop)
		dTape.pack(side='left', expand=True)

		lHead = tk.Label(dTape, text='▼')
		lHead.pack(side='top')

		dFile = tk.Frame(dTop)
		dFile.pack(side='right', fill='y')

		bImport = tk.Button(dFile, text='Import Tape', command=self.importTape)
		bImport.pack(side='top')
		bExport = tk.Button(dFile, text='Export Tape', command=self.exportTape)
		bExport.pack(side='top', fill='x')

		w['dCells'] = dCells = tk.Frame(dTape)
		dCells.pack(side='top', expand=True, fill='x')

		dShift = tk.Frame(dTape)
		dShift.pack(side='top')

		bShiftLeft = tk.Button(dShift, text='<', command=lambda: self.shiftTape(-1))
		bShiftLeft.pack(side='left')
		bShiftRight = tk.Button(dShift, text='>', command=lambda: self.shiftTape(1))
		bShiftRight.pack(side='right')

		dAccess = tk.Frame(dTape)
		dAccess.pack(side='top', fill='x')

		dGoto = tk.Frame(dAccess)
		dGoto.pack(side='left')

		lGoto = tk.Label(dGoto, text='Jump To:')
		lGoto.pack(side='left')
		w['eGoto'] = eGoto = tk.Entry(dGoto)
		eGoto.pack(side='left')
		eGoto.bind('<Return>', self.goto)
		bGoto = tk.Button(dGoto, text='Jump', command=self.goto)
		bGoto.pack(side='left')

		bReset = tk.Button(dAccess, text='Reset', command=self.resetTape)
		bReset.pack(side='right')

		dInput = tk.Frame(tab)
		dInput.pack(side='top', fill='x')

		dStart = tk.Frame(dInput)
		dStart.pack(side='left')

		lStart = tk.Label(dStart, text='Start Position:')
		lStart.pack(side='left')
		w['eStartPosition'] = eStart = tk.Entry(dStart, width=5)
		eStart.pack(side='left')

		dBlank = tk.Frame(dInput)
		dBlank.pack(side='left')

		lBlank = tk.Label(dBlank, text='Blank Character:')
		lBlank.pack(side='left')
		w['eBlank'] = eBlank = tk.Entry(dBlank, width=5)
		eBlank.pack(side='left')

		self.generateTapeWidgets()

	def executeTabWidgets(self, tab):
		w = self.widgets

		dMain = tk.Frame(tab)
		dMain.pack(side='top', expand=True, fill='x')

		dSizing = tk.Frame(dMain)
		dSizing.pack(side='top')

		dDim = tk.Frame(dSizing)
		dDim.pack(side='left')

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

		dCellSize = tk.Frame(dSizing)
		dCellSize.pack(side='left')

		lCellSize = tk.Label(dCellSize, text='Cell Size:')
		lCellSize.pack(side='left')
		w['eCellSize'] = eCellSize = tk.Entry(dCellSize, width=4)
		eCellSize.pack(side='left')
		eCellSize.insert(0, '50')
		eCellSize.bind('<Return>', self.execute)

		dPacing = tk.Frame(dMain)
		dPacing.pack(side='top')

		dSpeed = tk.Frame(dPacing)
		dSpeed.pack(side='left')

		lSpeed = tk.Label(dSpeed, text='Speed:')
		lSpeed.pack(side='left')
		w['eSpeed'] = eSpeed = tk.Entry(dSpeed, width=4)
		eSpeed.pack(side='left')
		eSpeed.insert(0, '1')
		eSpeed.bind('<Return>', self.execute)

		dFPS = tk.Frame(dPacing)
		dFPS.pack(side='left')

		lFPS = tk.Label(dFPS, text='FPS:')
		lFPS.pack(side='left')
		w['eFPS'] = eFPS = tk.Entry(dFPS, width=5)
		eFPS.pack(side='left')
		eFPS.insert(0, '100')
		eFPS.bind('<Return>', self.execute)

		bExecute = tk.Button(dMain, text='Execute', command=self.execute)
		bExecute.pack(side='top')

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
			cellFrame = tk.Frame(frame)
			cellFrame.pack(side='left', expand=True)

			cell = tk.Entry(cellFrame, width=10)
			cell.pack(side='top', expand=True)

			if str(pos) in t.keys():
				char = t[str(pos)]
				cell.insert(0, char)

			label = tk.Label(cellFrame, text=str(pos))
			label.pack(side='top')

			c[str(pos)] = cell
			d.append(cellFrame)

	'''def updateTab(self):
		tab = self.tab(self.select(), "text").upper()

		if tab == 'CROP':
			self.resizeCropTab()
		elif tab == 'SAVE':
			self.updateCrops('SAVE')
		elif tab == 'PDF':
			self.updateCrops('PDF')'''

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
		dRow = tk.Frame(frame)
		dRow.pack(side='top')

		eState = tk.Entry(dRow, width=10)
		eState.pack(side='left')
		eState.insert(0, data[0])

		eRead = tk.Entry(dRow, width=10)
		eRead.pack(side='left', padx=(0, 10))
		eRead.insert(0, data[1])

		eWrite = tk.Entry(dRow, width=10)
		eWrite.pack(side='left')
		eWrite.insert(0, data[2])

		eNew = tk.Entry(dRow, width=10)
		eNew.pack(side='left')
		eNew.insert(0, data[3])

		eDir = tk.Entry(dRow, width=10)
		eDir.pack(side='left', padx=(0, 5))
		eDir.insert(0, data[4])

		bDelete = tk.Button(dRow, text='x', command=lambda: self.deleteInstructionRow(dRow))
		bDelete.pack(side='right')

		i.append(dRow)
		tagUp('instructionScrollable', frame, eState, eRead, eWrite, eNew, eDir, bDelete)

		self.updateInstructionCanvas()

	def deleteInstructionRow(self, row):
		i = self.instructionRows

		row.destroy()
		i.remove(row)
		self.updateInstructionCanvas()

	def resetInstructions(self):
		i = self.instructionRows
		w = self.widgets

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
		dRow = tk.Frame(frame)
		dRow.pack(side='top')

		eState = tk.Entry(dRow, width=8)
		eState.pack(side='left')
		eState.insert(0, data)

		bDelete = tk.Button(dRow, text='x', command=lambda: self.deleteAcceptRow(dRow))
		bDelete.pack(side='right')

		a.append(dRow)
		tagUp('acceptScrollable', eState, bDelete)

		self.updateAcceptCanvas()

	def deleteAcceptRow(self, row):
		a = self.acceptRows

		row.destroy()
		a.remove(row)
		self.updateAcceptCanvas()

	def resetAccepts(self):
		a = self.acceptRows
		w = self.widgets

		frame = w['cdAccept']

		for row in a:
			row.destroy()

		self.acceptRows = []

		self.updateAcceptCanvas()

	def shiftTape(self, shift):
		self.updateTapeData()

		self.tapePos += shift
		self.generateTapeWidgets()

	def resetTape(self):
		w = self.widgets

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

			for part in row.winfo_children():
				if type(part) == tk.Entry:
					instruction.append(part.get())

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
		w = self.widgets

		self.updateTapeData()

		instructions = self.getInstructions()
		acceptStates = self.getAcceptStates()
		startState = w['eStartState'].get()

		tape = self.tape
		startPos = int(w['eStartPosition'].get())
		blankChar = w['eBlank'].get()

		width = int(w['eWidth'].get())
		height = int(w['eHeight'].get())
		cellSize =int( w['eCellSize'].get())
		speed = int(w['eSpeed'].get())
		FPS = int(w['eFPS'].get())

		TuringMachine.run(instructions, acceptStates, startState, tape, startPos, blankChar, (width, height), cellSize, speed, FPS)


def tagUp(tag, *args):
	for widget in args:
		widget.bindtags((tag,) + widget.bindtags())

def setEntry(entry, text):
	entry.delete(0, 'end')
	entry.insert(0, text)

def isInt(string, allowNegative=True):
	if not allowNegative:
		return bool(re.match(r'^[0-9]+$', string))
	else:
		return bool(re.match(r'^-?[0-9]+$', string))

root = tk.Tk()
root.title('Turing Machine')
root.geometry('800x600')
app = Application(master=root)

app.mainloop()
