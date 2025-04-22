import tkinter as tk
from elevator import Elevator
from direction import Direction
from elevatorsystem import ElevatorSystem


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
        self.destination_buttons = {}
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

        # Emergency buttons for each elevator
        self.emergency_frame = tk.Frame(self.master)
        self.emergency_frame.pack(side=tk.BOTTOM, padx=10, pady=(5, 10))

        for eid in range(self.elevator_count):
            btn = tk.Button(self.emergency_frame, text=f"Emergency {eid}", command=lambda eid=eid: self.toggle_emergency(eid))
            btn.grid(row=eid // 2, column=eid % 2, padx=5, pady=5)

        self.update_visuals()

    def pickup(self, floor):
        best_elevator = min(self.system.elevators, key=lambda e: e.get_destination_count())
        direction = Direction.UP if best_elevator.current_floor < floor else Direction.DOWN
        best_elevator.add_destination(floor, direction)
        self.pickups.add(floor)
        self.update_visuals()

    def step(self):
        self.system.step()

        for elevator in self.system.elevators:
            if elevator.open_doors:
                self.ask_if_destination(elevator.id, elevator.current_floor)

        self.pickups.clear()
        self.update_visuals()

    def ask_if_destination(self, elevator_id, current_floor):
        popup = tk.Toplevel(self.master)
        popup.title(f"Elevator {elevator_id} at Floor {current_floor}")

        tk.Label(popup, text=f"Elevator {elevator_id} doors are open at Floor {current_floor}.", font=("Arial", 10, "bold")).pack(pady=10)
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
                            command=lambda f=floor, eid=elevator_id, cf=current_floor, win=popup: self.choose_destination(f, eid, cf, win))
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
            # Elevator is in emergency mode, color it red
            if elevator.is_emergency:
                label.config(bg='red', text='E (EMERGENCY)')
            else:
                label.config(
                    bg='lightgreen' if elevator.open_doors else 'skyblue',
                    text='E*' if elevator.open_doors else 'E'
                )

        for i, elevator in enumerate(self.system.elevators):
            dests = sorted(elevator.destinations())
            next_floor = None
            if elevator.direction == Direction.UP:
                next_floor = min((f for f in dests if f > elevator.current_floor), default=None)
            elif elevator.direction == Direction.DOWN:
                next_floor = max((f for f in dests if f < elevator.current_floor), default=None)
            self.status_labels[i].config(
                text=f"Elevator {i}: Current = {elevator.current_floor}, Next = {next_floor}, Destinations = {dests}, Direction = {elevator.direction.name}"
            )

    def toggle_emergency(self, elevator_id):
        elevator = self.system.elevators[elevator_id]
        # Toggle the emergency state
        elevator.is_emergency = not elevator.is_emergency
        self.update_visuals()

