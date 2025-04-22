import tkinter as tk
from enum import Enum

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
        self.up_destinations = set()
        self.down_destinations = set()
        self.direction = Direction.STAY
        self.open_doors = False
        self.is_emergency = False

    def __str__(self):
        return f'| id: {self.id}, floor: {self.current_floor}, dest: {self.destinations()}, dir: {self.direction.name}' + (', DOOR OPEN |' if self.open_doors else ' |')

    def move(self):
        if self.is_emergency:
            self.open_doors = True
            return
        self.open_doors = False
        self.current_floor += self.direction.value
        self.check_open_doors()
        self.update_direction()

    def check_open_doors(self):
        if not self.direction is Direction.UP and self.current_floor in self.down_destinations:
            self.down_destinations.remove(self.current_floor)
            self.open_doors = True
        if not self.direction is Direction.DOWN and self.current_floor in self.up_destinations:
            self.up_destinations.remove(self.current_floor)
            self.open_doors = True

    def update_direction(self):
        destinations = self.destinations()
        if destinations:
            if self.direction is Direction.UP and max(destinations) == self.current_floor:
                self.direction = Direction.STAY
                self.check_open_doors()
            elif self.direction is Direction.DOWN and min(destinations) == self.current_floor:
                self.direction = Direction.STAY
                self.check_open_doors()
            elif self.direction is Direction.DOWN:
                if min(destinations) >= self.current_floor:
                    self.direction = Direction.UP
            elif self.direction is Direction.UP:
                if max(destinations) <= self.current_floor:
                    self.direction = Direction.DOWN
            else:
                if max(destinations) > self.current_floor:
                    self.direction = Direction.UP
                else:
                    self.direction = Direction.DOWN
        else:
            self.direction = Direction.STAY

    def destinations(self):
        return self.up_destinations | self.down_destinations

    def get_status(self):
        return self.id, self.current_floor, self.destinations()

    def get_destination_count(self):
        return len(self.destinations())

    def add_destination(self, destination, direction):
        if self.is_emergency:
            return
        if direction is Direction.UP:
            self.up_destinations.add(destination)
        elif direction is Direction.DOWN:
            self.down_destinations.add(destination)
        self.update_direction()

class ElevatorSystem:
    def __init__(self, elevator_count=4):
        self.elevators = [Elevator(i) for i in range(elevator_count)]

    def __str__(self):
        return '\n'.join(map(str, self.elevators))

    def pickup(self, floor, direction_value):
        direction = Direction.STAY
        if direction_value > 0:
            direction = Direction.UP
        elif direction_value < 0:
            direction = Direction.DOWN

        available_elevators = [e for e in self.elevators if not e.is_emergency]
        if not available_elevators:
            return

        elevator_pick = min(available_elevators, key=lambda e: e.get_destination_count())
        elevator_pick.add_destination(floor, direction)

    def step(self):
        for elevator in self.elevators:
            elevator.move()

    def get_status(self):
        return [elevator.get_status() for elevator in self.elevators]

class ElevatorSystemGUI:
    def __init__(self, master, elevator_count=4, max_floor=9):
        self.master = master
        self.master.title("Elevator System Simulation")

        self.elevator_count = elevator_count
        self.max_floor = max_floor
        self.system = ElevatorSystem(elevator_count)
        self.pickups = set()

        self.elevator_labels = []
        self.status_labels = []
        self.emergency_buttons = []

        self.setup_ui()

    def setup_ui(self):
        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.shaft_frame = tk.Frame(self.master)
        self.shaft_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.status_frame = tk.Frame(self.master)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Controls
        tk.Label(self.control_frame, text="Controls", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        tk.Button(self.control_frame, text="Step", command=self.step, width=15).pack(pady=5)
        tk.Button(self.control_frame, text="Exit", command=self.master.quit, width=15).pack(pady=5)

        # Floor pickup buttons
        tk.Label(self.control_frame, text="Pickup Requests", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        for floor in reversed(range(self.max_floor + 1)):
            btn = tk.Button(self.control_frame, text=f"Request at Floor {floor}", width=20,
                          command=lambda f=floor: self.pickup(f))
            btn.pack(pady=2)

        # Elevator shafts
        tk.Label(self.shaft_frame, text="Elevators", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=self.elevator_count + 1)
        for floor in reversed(range(self.max_floor + 1)):
            tk.Label(self.shaft_frame, text=f"Floor {floor}", width=10).grid(row=self.max_floor - floor + 1, column=0)
            floor_row = []
            for eid in range(self.elevator_count):
                lbl = tk.Label(self.shaft_frame, text=' ', width=5, height=2, relief='ridge', bg='white')
                lbl.grid(row=self.max_floor - floor + 1, column=eid + 1, padx=2, pady=2)
                floor_row.append(lbl)
            self.elevator_labels.append(floor_row)

        # Status labels
        for i in range(self.elevator_count):
            lbl = tk.Label(self.status_frame, text="", font=("Courier", 10), anchor='w')
            lbl.pack(fill=tk.X, padx=5)
            self.status_labels.append(lbl)

        # Emergency buttons
        emergency_frame = tk.Frame(self.shaft_frame)
        emergency_frame.grid(row=self.max_floor + 2, column=0, columnspan=self.elevator_count + 1, pady=(10, 0))
        tk.Label(emergency_frame, text="Emergency:").pack(side=tk.LEFT)
        
        for eid in range(self.elevator_count):
            btn = tk.Button(emergency_frame, text=f"E{eid}", width=4, bg="lightgray",
                           command=lambda eid=eid: self.toggle_emergency(eid))
            btn.pack(side=tk.LEFT, padx=2)
            self.emergency_buttons.append(btn)

        self.update_visuals()

    def pickup(self, floor):
        available_elevators = [e for e in self.system.elevators if not e.is_emergency]
        if not available_elevators:
            print("All elevators are in emergency mode!")
            return
            
        best_elevator = min(available_elevators, key=lambda e: e.get_destination_count())
        direction = Direction.UP if best_elevator.current_floor < floor else Direction.DOWN
        best_elevator.add_destination(floor, direction)
        self.pickups.add(floor)
        self.update_visuals()

    def step(self):
        self.system.step()

        for elevator in self.system.elevators:
            if elevator.open_doors and not elevator.is_emergency:
                self.ask_if_destination(elevator.id, elevator.current_floor)

        self.pickups.clear()
        self.update_visuals()

    def toggle_emergency(self, elevator_id):
        elevator = self.system.elevators[elevator_id]
        elevator.is_emergency = not elevator.is_emergency
        
        btn = self.emergency_buttons[elevator_id]
        if elevator.is_emergency:
            btn.config(bg="red", fg="white")
            elevator.up_destinations.clear()
            elevator.down_destinations.clear()
            elevator.direction = Direction.STAY
            elevator.open_doors = True
        else:
            btn.config(bg="lightgray", fg="black")
        
        self.update_visuals()

    def ask_if_destination(self, elevator_id, current_floor):
        popup = tk.Toplevel(self.master)
        popup.title(f"Elevator {elevator_id} at Floor {current_floor}")

        tk.Label(popup, text=f"Elevator {elevator_id} doors are open at Floor {current_floor}.", 
                font=("Arial", 10, "bold")).pack(pady=10)
        tk.Label(popup, text="Would you like to choose a destination?").pack(pady=5)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=5)

        yes_btn = tk.Button(btn_frame, text="Yes", width=10,
                           command=lambda: self.show_destination_buttons(current_floor, elevator_id, popup))
        yes_btn.grid(row=0, column=0, padx=5)

        no_btn = tk.Button(btn_frame, text="No", width=10, command=popup.destroy)
        no_btn.grid(row=0, column=1, padx=5)

    def show_destination_buttons(self, current_floor, elevator_id, parent_popup):
        parent_popup.destroy()

        popup = tk.Toplevel(self.master)
        popup.title(f"Choose Destination for Elevator {elevator_id}")

        tk.Label(popup, text="Select destination floor:", font=("Arial", 10, "bold")).pack(pady=5)

        for floor in range(self.max_floor + 1):
            if floor == current_floor:
                continue
            btn = tk.Button(popup, text=f"Floor {floor}",
                          command=lambda f=floor, eid=elevator_id, cf=current_floor, win=popup: 
                          self.choose_destination(f, eid, cf, win))
            btn.pack(padx=10, pady=2)

    def choose_destination(self, floor, elevator_id, current_floor, popup_window):
        direction = Direction.UP if floor > current_floor else Direction.DOWN
        self.system.elevators[elevator_id].add_destination(floor, direction)
        popup_window.destroy()
        self.update_visuals()

    def update_visuals(self):
        for row in self.elevator_labels:
            for lbl in row:
                lbl.config(bg='white', text=' ')

        for elevator in self.system.elevators:
            floor = elevator.current_floor
            eid = elevator.id
            label = self.elevator_labels[self.max_floor - floor][eid]
            
            if elevator.is_emergency:
                label.config(bg='red', text='STOP', fg='white')
            elif elevator.open_doors:
                label.config(bg='lightgreen', text='OPEN')
            else:
                label.config(bg='skyblue', text=f'E{eid}')

        for i, elevator in enumerate(self.system.elevators):
            status = f"Elevator {i}: Floor {elevator.current_floor}"
            if elevator.is_emergency:
                status += " [EMERGENCY STOP]"
            else:
                status += f", Destinations: {sorted(elevator.destinations())}, Direction: {elevator.direction.name}"
            self.status_labels[i].config(text=status)

def ask_elevator_count():
    def confirm():
        try:
            count = int(entry.get())
            if count <= 0:
                raise ValueError
            popup.destroy()
            start_main_app(count)
        except ValueError:
            error_lbl.config(text="Enter a positive number.")

    popup = tk.Tk()
    popup.title("Startup Configuration")

    tk.Label(popup, text="Enter number of elevators:").pack(padx=10, pady=(10, 5))
    entry = tk.Entry(popup)
    entry.pack(padx=10, pady=5)
    entry.insert(0, "3")

    error_lbl = tk.Label(popup, text="", fg="red")
    error_lbl.pack(pady=2)

    tk.Button(popup, text="Start", command=confirm).pack(pady=(0, 10))
    popup.mainloop()

def start_main_app(elevator_count):
    root = tk.Tk()
    app = ElevatorSystemGUI(root, elevator_count=elevator_count, max_floor=9)
    root.mainloop()

if __name__ == "__main__":
    ask_elevator_count()
