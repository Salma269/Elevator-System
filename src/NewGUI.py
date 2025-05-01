import tkinter as tk
from enum import Enum
from graphviz import Digraph
import tempfile
import webbrowser
import os

class Direction(Enum):
    UP = 1
    STAY = 0
    DOWN = -1

    @staticmethod
    def opposite(dir):
        if dir == Direction.UP:
            return Direction.DOWN
        if dir == Direction.DOWN:
            return Direction.UP

class Elevator:
    def __init__(self, id):
        self.id = id
        self.current_floor = 0
        self.destination_queue = []  # Changed to ordered list
        self.direction = Direction.STAY
        self.open_doors = False
        self.is_emergency = False

    def __str__(self):
        return f'Elevator {self.id}: Floor {self.current_floor}, Queue: {self.destination_queue}, Dir: {self.direction.name}, Doors: {"OPEN" if self.open_doors else "CLOSED"}'

    def move(self):
        if self.is_emergency:
            self.open_doors = True
            return
            
        if not self.destination_queue:
            self.direction = Direction.STAY
            return

        self.open_doors = False
        
        # Move toward next destination in queue
        next_floor = self.destination_queue[0]
        if self.current_floor < next_floor:
            self.direction = Direction.UP
            self.current_floor += 1
        elif self.current_floor > next_floor:
            self.direction = Direction.DOWN
            self.current_floor -= 1
        
        # Check if reached destination
        if self.current_floor == next_floor:
            self.destination_queue.pop(0)  # Remove from queue
            self.open_doors = True
            self.update_direction()

    def update_direction(self):
        if not self.destination_queue:
            self.direction = Direction.STAY
            return
            
        next_floor = self.destination_queue[0]
        if next_floor > self.current_floor:
            self.direction = Direction.UP
        elif next_floor < self.current_floor:
            self.direction = Direction.DOWN
        else:
            self.direction = Direction.STAY

    def add_destination(self, floor, direction):
        if self.is_emergency:
            return
            
        if floor == self.current_floor:
            return
            
        # Add to queue in the correct position based on direction
        if not self.destination_queue:
            self.destination_queue.append(floor)
            self.update_direction()
            return
            
        if direction == Direction.UP:
            # Insert floors in ascending order
            if floor not in self.destination_queue:
                self.destination_queue.append(floor)
                self.destination_queue.sort()
        else:
            # Insert floors in descending order
            if floor not in self.destination_queue:
                self.destination_queue.append(floor)
                self.destination_queue.sort(reverse=True)
                
        self.update_direction()

    def get_status(self):
        return {
            'id': self.id,
            'current_floor': self.current_floor,
            'queue': self.destination_queue.copy(),
            'direction': self.direction,
            'doors_open': self.open_doors,
            'emergency': self.is_emergency
        }

    def generate_fsm_diagram(self, current_state=None):
        """Generate FSM diagram showing current state and queue"""
        fsm = Digraph(f'Elevator_{self.id}_FSM', filename=f'elevator_{self.id}_fsm.gv')
        fsm.attr(rankdir='LR', size='12,8', dpi='300')
        
        # Highlight current state if provided
        node_attrs = {'shape': 'ellipse', 'fontsize': '14'}
        if current_state:
            node_attrs['color'] = 'blue' if current_state != 'EMERGENCY' else 'red'
            node_attrs['penwidth'] = '2'
        
        # States
        fsm.node('IDLE', label='IDLE\nQueue: '+str(self.destination_queue), **node_attrs if current_state=='IDLE' else {})
        fsm.node('MOVING_UP', label='MOVING UP\nQueue: '+str(self.destination_queue), **node_attrs if current_state=='MOVING_UP' else {})
        fsm.node('MOVING_DOWN', label='MOVING DOWN\nQueue: '+str(self.destination_queue), **node_attrs if current_state=='MOVING_DOWN' else {})
        fsm.node('DOORS_OPEN', label='DOORS OPEN\nQueue: '+str(self.destination_queue), **node_attrs if current_state=='DOORS_OPEN' else {})
        fsm.node('EMERGENCY', label='EMERGENCY\nQueue Cleared', color='red', fontcolor='red', **node_attrs if current_state=='EMERGENCY' else {})
        
        # Transitions
        fsm.attr('edge', fontsize='12')
        fsm.edge('IDLE', 'MOVING_UP', label='New destination above')
        fsm.edge('IDLE', 'MOVING_DOWN', label='New destination below')
        fsm.edge('IDLE', 'DOORS_OPEN', label='At destination')
        
        fsm.edge('MOVING_UP', 'DOORS_OPEN', label='Reached floor')
        fsm.edge('MOVING_UP', 'MOVING_DOWN', label='No more up destinations')
        
        fsm.edge('MOVING_DOWN', 'DOORS_OPEN', label='Reached floor')
        fsm.edge('MOVING_DOWN', 'MOVING_UP', label='No more down destinations')
        
        fsm.edge('DOORS_OPEN', 'IDLE', label='Queue empty')
        fsm.edge('DOORS_OPEN', 'MOVING_UP', label='Next destination above')
        fsm.edge('DOORS_OPEN', 'MOVING_DOWN', label='Next destination below')
        
        # Emergency transitions
        fsm.edge('IDLE', 'EMERGENCY', label='Emergency!', color='red')
        fsm.edge('MOVING_UP', 'EMERGENCY', label='Emergency!', color='red')
        fsm.edge('MOVING_DOWN', 'EMERGENCY', label='Emergency!', color='red')
        fsm.edge('DOORS_OPEN', 'EMERGENCY', label='Emergency!', color='red')
        fsm.edge('EMERGENCY', 'IDLE', label='Resolved', color='green')
        
        return fsm

class ElevatorSystem:
    def __init__(self, elevator_count=4):
        self.elevators = [Elevator(i) for i in range(elevator_count)]

    def step(self):
        for elevator in self.elevators:
            elevator.move()

    def pickup(self, floor, direction):
        available = [e for e in self.elevators if not e.is_emergency]
        if not available:
            return
            
        # Find elevator with fewest destinations
        best = min(available, key=lambda e: len(e.destination_queue))
        best.add_destination(floor, direction)

    def get_status(self):
        return [e.get_status() for e in self.elevators]

class ElevatorSystemGUI:
    def __init__(self, master, elevator_count=4, min_floor=0, max_floor=9):
        self.master = master
        self.master.title("Elevator System Simulation")
        self.elevator_count = elevator_count
        self.min_floor = min_floor
        self.max_floor = max_floor
        self.system = ElevatorSystem(elevator_count)
        
        self.setup_ui()

    def setup_ui(self):
        # Main frames
        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.shaft_frame = tk.Frame(self.master)
        self.shaft_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.status_frame = tk.Frame(self.master)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Control buttons
        tk.Label(self.control_frame, text="Controls", font=("Arial", 12, "bold")).pack()
        tk.Button(self.control_frame, text="Step", command=self.step_simulation, width=15).pack(pady=5)
        
        # Floor requests
        tk.Label(self.control_frame, text="Request Elevator", font=("Arial", 12, "bold")).pack(pady=(20,5))
        for floor in reversed(range(self.min_floor, self.max_floor+1)):
            frame = tk.Frame(self.control_frame)
            frame.pack(pady=2)
            tk.Button(frame, text=f"Floor {floor} Up", width=8,
                     command=lambda f=floor: self.request_elevator(f, Direction.UP)).pack(side=tk.LEFT)
            tk.Button(frame, text=f"Floor {floor} Down", width=8,
                     command=lambda f=floor: self.request_elevator(f, Direction.DOWN)).pack(side=tk.LEFT)

        # Elevator shafts
        tk.Label(self.shaft_frame, text="Elevators", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=self.elevator_count+1)
        
        # Floor indicators
        for i, floor in enumerate(reversed(range(self.min_floor, self.max_floor+1))):
            row = i + 1
            tk.Label(self.shaft_frame, text=f"Floor {floor}", width=8).grid(row=row, column=0)
            
            # Elevator positions
            for eid in range(self.elevator_count):
                lbl = tk.Label(self.shaft_frame, text=" ", width=6, height=2, relief='ridge', bg='white')
                lbl.grid(row=row, column=eid+1, padx=2, pady=2)
                if i == 0:  # Initialize labels list
                    if not hasattr(self, 'elevator_labels'):
                        self.elevator_labels = []
                    self.elevator_labels.append(lbl)

        # Emergency and FSM buttons
        button_row = (self.max_floor - self.min_floor) + 2
        
        for eid in range(self.elevator_count):
            # Emergency button
            emerg_btn = tk.Button(self.shaft_frame, text=f"E{eid} Emergency", 
                                bg="lightgray", command=lambda e=eid: self.toggle_emergency(e))
            emerg_btn.grid(row=button_row, column=eid+1, pady=(10,2))
            
            # FSM button
            fsm_btn = tk.Button(self.shaft_frame, text=f"FSM {eid}", 
                              bg="lightblue", command=lambda e=eid: self.show_fsm(e))
            fsm_btn.grid(row=button_row+1, column=eid+1, pady=2)
            
            # Store buttons for later reference
            if not hasattr(self, 'emergency_buttons'):
                self.emergency_buttons = []
                self.fsm_buttons = []
            self.emergency_buttons.append(emerg_btn)
            self.fsm_buttons.append(fsm_btn)

        # Status displays
        for i in range(self.elevator_count):
            lbl = tk.Label(self.status_frame, text="", font=("Courier", 10), anchor='w')
            lbl.pack(fill=tk.X, padx=5)
            if i == 0:  # Initialize status labels list
                self.status_labels = []
            self.status_labels.append(lbl)

        self.update_display()

    def request_elevator(self, floor, direction):
        self.system.pickup(floor, direction)
        self.update_display()

    def step_simulation(self):
        self.system.step()
        self.update_display()
        
        # Check for doors opening to request destinations
        for i, elevator in enumerate(self.system.elevators):
            if elevator.open_doors and not elevator.is_emergency:
                self.prompt_destination(i, elevator.current_floor)

    def toggle_emergency(self, elevator_id):
        elevator = self.system.elevators[elevator_id]
        elevator.is_emergency = not elevator.is_emergency
        
        btn = self.emergency_buttons[elevator_id]
        if elevator.is_emergency:
            btn.config(bg="red", fg="white")
            elevator.destination_queue = []  # Clear queue
        else:
            btn.config(bg="lightgray", fg="black")
            
        self.update_display()

    def show_fsm(self, elevator_id):
        elevator = self.system.elevators[elevator_id]
        
        # Determine current state for highlighting
        current_state = None
        if elevator.is_emergency:
            current_state = 'EMERGENCY'
        elif elevator.open_doors:
            current_state = 'DOORS_OPEN'
        elif elevator.direction == Direction.UP:
            current_state = 'MOVING_UP'
        elif elevator.direction == Direction.DOWN:
            current_state = 'MOVING_DOWN'
        else:
            current_state = 'IDLE'
            
        fsm = elevator.generate_fsm_diagram(current_state)
        
        try:
            # Create temp file for diagram
            with tempfile.NamedTemporaryFile(prefix=f'elevator_{elevator_id}_', suffix='.html', delete=False) as tmp:
                temp_path = tmp.name
            
            # Render diagram
            fsm.format = 'png'
            fsm.render(temp_path.replace('.html', ''), view=False)
            
            # Create HTML to display
            img_path = temp_path.replace('.html', '.png')
            html = f"""
            <html>
                <head><title>Elevator {elevator_id} FSM</title></head>
                <body>
                    <h1>Elevator {elevator_id} State Machine</h1>
                    <p>Current floor: {elevator.current_floor}</p>
                    <p>Destination queue: {elevator.destination_queue}</p>
                    <img src="{img_path}">
                </body>
            </html>
            """
            
            with open(temp_path, 'w') as f:
                f.write(html)
                
            webbrowser.open(f'file://{temp_path}')
        except Exception as e:
            print(f"Error showing FSM: {e}")
            self.show_text_fsm(elevator_id, current_state)

    def show_text_fsm(self, elevator_id, current_state):
        """Fallback text display of FSM"""
        elevator = self.system.elevators[elevator_id]
        popup = tk.Toplevel(self.master)
        popup.title(f"Elevator {elevator_id} State Diagram")
        
        text = tk.Text(popup, wrap=tk.WORD, width=80, height=25)
        text.insert(tk.END, f"Elevator {elevator_id} State Machine\n")
        text.insert(tk.END, f"Current State: {current_state}\n")
        text.insert(tk.END, f"Current Floor: {elevator.current_floor}\n")
        text.insert(tk.END, f"Destination Queue: {elevator.destination_queue}\n\n")
        
        text.insert(tk.END, "Transitions:\n")
        text.insert(tk.END, "IDLE → MOVING_UP (when destination above exists)\n")
        text.insert(tk.END, "IDLE → MOVING_DOWN (when destination below exists)\n")
        text.insert(tk.END, "MOVING_UP → DOORS_OPEN (when reaching destination)\n") 
        text.insert(tk.END, "MOVING_DOWN → DOORS_OPEN (when reaching destination)\n")
        text.insert(tk.END, "DOORS_OPEN → MOVING_UP/DOWN (next destination in queue)\n")
        text.insert(tk.END, "ANY STATE → EMERGENCY (when emergency button pressed)\n")
        text.insert(tk.END, "EMERGENCY → IDLE (when emergency resolved)\n")
        
        text.config(state=tk.DISABLED)
        text.pack()

    def prompt_destination(self, elevator_id, current_floor):
        """Prompt for new destination when doors open"""
        popup = tk.Toplevel(self.master)
        popup.title(f"Elevator {elevator_id} at Floor {current_floor}")
        
        tk.Label(popup, text=f"Elevator {elevator_id} doors are open at Floor {current_floor}").pack(pady=10)
        tk.Label(popup, text="Add destination to queue:").pack()
        
        frame = tk.Frame(popup)
        frame.pack(pady=10)
        
        for floor in range(self.min_floor, self.max_floor+1):
            if floor != current_floor:
                btn = tk.Button(frame, text=f"Floor {floor}", width=8,
                              command=lambda f=floor, e=elevator_id, p=popup: self.add_destination(f, e, p))
                btn.pack(side=tk.LEFT, padx=2)

    def add_destination(self, floor, elevator_id, popup):
        """Add destination to elevator's queue"""
        elevator = self.system.elevators[elevator_id]
        
        # Determine direction based on current floor
        if floor > elevator.current_floor:
            direction = Direction.UP
        else:
            direction = Direction.DOWN
            
        elevator.add_destination(floor, direction)
        popup.destroy()
        self.update_display()

    def update_display(self):
        """Update all visual elements"""
        # Update elevator positions
        for eid, elevator in enumerate(self.system.elevators):
            for floor_idx in range(self.min_floor, self.max_floor+1):
                row = (self.max_floor - floor_idx) + 1
                lbl = self.elevator_labels[eid]
                
                if elevator.current_floor == floor_idx:
                    if elevator.is_emergency:
                        lbl.config(bg='red', text='EMERG', fg='white')
                    elif elevator.open_doors:
                        lbl.config(bg='lightgreen', text='OPEN')
                    else:
                        lbl.config(bg='skyblue', text=f'E{eid}')
                else:
                    lbl.config(bg='white', text=' ')
        
        # Update status labels
        for i, elevator in enumerate(self.system.elevators):
            status = f"Elevator {i}: Floor {elevator.current_floor}, "
            if elevator.is_emergency:
                status += "EMERGENCY STOP"
            else:
                status += f"Queue: {elevator.destination_queue}, "
                status += f"Direction: {elevator.direction.name}, "
                status += "Doors: " + ("OPEN" if elevator.open_doors else "CLOSED")
            self.status_labels[i].config(text=status)

def ask_elevator_config():
    def confirm():
        try:
            count = int(entry_count.get())
            min_floor = int(entry_min.get())
            max_floor = int(entry_max.get())
            
            if count <= 0:
                raise ValueError("Number of elevators must be positive")
            if min_floor >= max_floor:
                raise ValueError("Minimum floor must be less than maximum floor")
            
            popup.destroy()
            start_main_app(count, min_floor, max_floor)
        except ValueError as e:
            error_lbl.config(text=str(e))

    popup = tk.Tk()
    popup.title("Startup Configuration")

    # Elevator count
    tk.Label(popup, text="Number of elevators:").pack(padx=10, pady=(10, 5))
    entry_count = tk.Entry(popup)
    entry_count.pack(padx=10, pady=5)
    entry_count.insert(0, "3")

    # Min floor
    tk.Label(popup, text="Minimum floor:").pack(padx=10, pady=5)
    entry_min = tk.Entry(popup)
    entry_min.pack(padx=10, pady=5)
    entry_min.insert(0, "0")

    # Max floor
    tk.Label(popup, text="Maximum floor:").pack(padx=10, pady=5)
    entry_max = tk.Entry(popup)
    entry_max.pack(padx=10, pady=5)
    entry_max.insert(0, "9")

    error_lbl = tk.Label(popup, text="", fg="red")
    error_lbl.pack(pady=2)

    tk.Button(popup, text="Start", command=confirm).pack(pady=(0, 10))
    popup.mainloop()

def start_main_app(elevator_count, min_floor, max_floor):
    """Start the main application"""
    root = tk.Tk()
    app = ElevatorSystemGUI(root, elevator_count, min_floor, max_floor)
    root.mainloop()

if __name__ == "__main__":
    ask_elevator_config()
