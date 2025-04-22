import tkinter as tk
from enum import Enum
from elevator import Elevator
from direction import Direction
from elevatorsystem import ElevatorSystem

class ElevatorSystemGUI:
    def __init__(self, master, elevator_count=4, min_floor=0, max_floor=9):
        self.master = master
        self.master.title("Elevator System Simulation")

        self.elevator_count = elevator_count
        self.min_floor = min_floor
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
        for floor in reversed(range(self.min_floor, self.max_floor + 1)):
            btn = tk.Button(self.control_frame, text=f"Request at Floor {floor}", width=20,
                          command=lambda f=floor: self.pickup(f))
            btn.pack(pady=2)

        # Elevator shafts
        tk.Label(self.shaft_frame, text="Elevators", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=self.elevator_count + 1)
        
        # Calculate total rows needed (floors + header + emergency buttons)
        total_rows = (self.max_floor - self.min_floor) + 2  # +1 for header, +1 for emergency buttons
        
        for i, floor in enumerate(reversed(range(self.min_floor, self.max_floor + 1))):
            row = i + 1  # Start from row 1 (row 0 is header)
            tk.Label(self.shaft_frame, text=f"Floor {floor}", width=10).grid(row=row, column=0)
            
            floor_row = []
            for eid in range(self.elevator_count):
                lbl = tk.Label(self.shaft_frame, text=' ', width=5, height=2, relief='ridge', bg='white')
                lbl.grid(row=row, column=eid + 1, padx=2, pady=2)
                floor_row.append(lbl)
            self.elevator_labels.append(floor_row)

        # Emergency buttons row - placed directly below the lowest floor
        emergency_row = (self.max_floor - self.min_floor) + 2  # +1 for header, +1 because rows start at 0
        
        for eid in range(self.elevator_count):
            btn = tk.Button(
                self.shaft_frame,
                text=f"E{eid} 🚨",
                width=5,
                bg="lightgray",
                command=lambda eid=eid: self.toggle_emergency(eid)
            )
            btn.grid(row=emergency_row, column=eid + 1, pady=(10, 0))
            self.emergency_buttons.append(btn)

        # Status labels
        for i in range(self.elevator_count):
            lbl = tk.Label(self.status_frame, text="", font=("Courier", 10), anchor='w')
            lbl.pack(fill=tk.X, padx=5)
            self.status_labels.append(lbl)

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

        for floor in range(self.min_floor, self.max_floor + 1):
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
            # Calculate the correct row index based on floor number
            row_index = (self.max_floor - floor)
            if 0 <= row_index < len(self.elevator_labels):
                label = self.elevator_labels[row_index][eid]
                
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
    root = tk.Tk()
    app = ElevatorSystemGUI(root, elevator_count=elevator_count, min_floor=min_floor, max_floor=max_floor)
    root.mainloop()

if __name__ == "__main__":
    ask_elevator_config()
