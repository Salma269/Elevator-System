# Elevator System

## Table of Contents
- [Elevator System](#elevator-system)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Algorithm](#algorithm)
    - [Path choosing](#path-choosing)
    - [Elevator choosing](#elevator-choosing)
  - [Ways to improve](#ways-to-improve)
  - [Simulation](#simulation)
  - [Usage](#usage)


## Description

The project provides an implementation for an elevator system, as well as a simple console simulation to test its usage and features.

## Algorithm

### Path choosing
The logic of the elevator path choosing is reminiscent of a classic SCAN approach. The elevator travels in the same direction, as long as there are any destinations to be reached in it. If there are none and some destinations of the opposite direction are present, then it switches. If the destinations' sets are empty, the elevator becomes idle.

The elevator stops only at destinations if it travels in the direction corresponding to the particular destination, which is determined e.g. during pickup request, based on which button was pressed.


### Elevator choosing
When the user presses a button next to the elevators, the specific elevator that will take up the pickup is chosen based on which one is the least busy, that is has the fewest destinations assigned. However the metrics that determine the choice could be easily replaced to improve the workload balance.


## Ways to improve
* Using better data structures for the destinations, that would allow quicker access to min and max, e.g. the min-max heap.
* Using more complex metrics or even an AI model to pick the elevator used for pickup.
  

## Simulation

The console program allows simulating the functioning of an elevator management system.

It accepts the number of elevators in the system and offers the user a set of actions to perform:

* step - make one step of the simulation, each elevator will move by 0 or 1 floor
* pickup - the program prompts the user to enter the floor number and the direction of the pickup seperated by a comma. The direction should be input as an integer - a positive number meaning UP and negative meaning DOWN. The prompt to choose floor destination when entering the elevator comes up once the elevator reaches the pickup floor and the directions match.
* exit - terminate the program

After each action the simulation lists all of the elevator's state with information including:
* id number
* current floor
* set of destinations
* current direction
* if the doors are open or not

## Usage

To run the simulation, please execute:
```
python3 src/main.py
```
in the project's directory.