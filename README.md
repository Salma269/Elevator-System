
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
  - [Path Selection Algorithm](#path-selection-algorithm)
  - [Elevator Dispatching](#elevator-dispatching)

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
   ```

2. **Install dependencies**:

   - Graphviz (for FSM visualization)
   - tkinter (usually comes with Python)
   - PIL (Python Imaging Library)

3. **Install Graphviz**:

   - **Windows**: Download the installer from [graphviz.org](https://graphviz.org)
   - **macOS**:  
     ```bash
     brew install graphviz
     ```
   - **Linux**:  
     ```bash
     sudo apt-get install graphviz
     ```

## Usage

Run the simulation:
```bash
python elevator_system.py
```

## Configuration

- Set number of elevators (1–8)  
- Define floor range (max 10 floors total)

## System Architecture

### Path Selection Algorithm

Implements a SCAN (elevator) algorithm with the following behaviors:

- Continues in current direction while destinations remain  
- Changes direction only when current direction is exhausted  
- Becomes idle when no destinations remain  
- Prioritizes destinations based on travel direction  

### Elevator Dispatching

- **Least-Busy Selection**: Chooses elevator with fewest pending destinations  
- **Direction Awareness**: Considers current movement direction  
- **Emergency Priority**: Immediately handles emergency stops  
