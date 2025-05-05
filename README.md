# Elevator System Simulation 🏢🛗

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![GUI](https://img.shields.io/badge/Interface-Tkinter-yellow.svg)

A sophisticated elevator management system simulation with graphical interface and intelligent dispatching algorithms.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [System Architecture](#system-architecture)
  - [Path Selection Algorithm](##path-selection-algorithm)
  - [Elevator Dispatching](##elevator-dispatching)

## Features

- **Configurable System**: Supports up to 8 elevators and 10 floors
- **Intelligent Dispatching**: Least-busy elevator selection algorithm
- **Real-time Visualization**: Graphical display of elevator positions and statuses
- **State Machine**: Interactive FSM diagram of elevator logic
- **Emergency Controls**: Individual emergency stop for each elevator
- **Responsive UI**: Scrollable interface for large configurations

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Salma269/Elevator-System.git
   cd elevator-simulation

2. **Install dependencies:**:
   ```bash
    Install Graphviz (for FSM visualization)
    Install tkinter
    Install PIL

3. **Install Graphviz (for FSM visualization):**:

- **Windows:** Download installer

- **macOS:** brew install graphviz

- **Linux:** sudo apt-get install graphviz

4. **Usage:**
  Run the simulation:
   ```bash
   python elevator_system.py

5. **Configuration:**
 - Set number of elevators (1-8)
 - Define floor range (max 10 floors total)

6. **System Architecture:**
   
  6.1.***Path Selection Algorithm***
    Implements a SCAN (elevator) algorithm with these behaviors:
      - Continues in current direction while destinations remain
      - Changes direction only when current direction is exhausted
      - Becomes idle when no destinations remain
      - Prioritizes destinations based on travel direction

  6.2. ***Elevator Dispatching:***
    -**Least-Busy Selection:** Chooses elevator with fewest pending destinations
    - **Direction Awareness:** Considers current movement direction
    - **Emergency Priority:** Immediately handles emergency stops
