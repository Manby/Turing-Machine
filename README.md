# Turing-Machine

## Editor

#### Machine Instructions
States can have any name, although numerical names (e.g. 0, 1, 2...) are recommended as they appear nicely on the read-write head during simulation.

Any string can be read to or written from the cells on the tape, although single characters are recommended as they appear nicely during simulation.

When defining an instruction, the **direction** refers to the movement of the **head**, and must be `l` or `r` (case-insensitive).

When defining an instruction, reading/writing a **blank cell** is represented by a blank entry.

#### Tape
The **start position** of the tape is the position at which the read-write head will be when simulation begins.

The **blank character** of the tape is what will be drawn at any blank cell on the tape. This can be left empty.


## Simulation
Each **step** of the machine consists of 4 parts:
1. Read the current cell and find the appropriate transition instruction
2. Write the new string
3. Transition to the next state
4. Move the read-write head

The read-write head will turn **red** if it is in a situation that has no transition function defined.

The read-write head will turn **green** if it reaches an accept state.

The **status** of the machine is indicated by the symbol at the top-left of the window:
Symbol | Meaning
-- | --
… | Standby
► | Running
❚❚ | Paused
■ | Stopped


### Controls

#### When the machine is in standby:
* SPACE:    Do one full step
* T:        Do one part of a step
* R:        Run machine automatically

#### When the machine is running:
* P:        Pause execution

#### When the machine is paused:
* P:        Unpause execution

#### When the machine has stopped:
* Left:     Move head left
* Right:    Move head right
* Up:       Raise head
* Down:     Lower head


(Manually raising/lowering the head has no practical purpose, only demonstrational purpose.)

#### At any time:
* Tab:      Toggle detail
* Equals:   Zoom in
* Minus:    Zoom out
