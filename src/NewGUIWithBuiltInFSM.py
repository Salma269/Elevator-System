import tkinter as tk
from enum import Enum
from elevator import Elevator
from direction import Direction
from elevatorsystem import ElevatorSystem
from graphviz import Digraph
from PIL import Image, ImageTk
import os
from tkinter import ttk

class ElevatorSystemGUI:
    def __init__(self, master, elevator_count=4, min_floor=0, max_floor=9):
        self.master = master
        self.master.title("Elevator System Simulation")
        # STYLE CHANGE: Set a modern background color for the main window
        self.master.configure(bg='#f0f2f5')
        
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
        # STYLE CHANGE: Added border and padding to control frame with a clean white background
        self.control_frame = tk.Frame(self.master, bg='white', bd=2, relief='groove')
        self.control_frame.pack(side=tk.LEFT, padx=15, pady=15, fill=tk.Y)

        # STYLE CHANGE: Added shadow effect to shaft frame
        self.shaft_frame = tk.Frame(self.master, bg='#e8ecef', bd=2, relief='ridge')
        self.shaft_frame.pack(side=tk.LEFT, padx=15, pady=15)

        # STYLE CHANGE: Modernized status frame with subtle border
        self.status_frame = tk.Frame(self.master, bg='#f0f2f5', bd=1, relief='flat')
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Controls
        # STYLE CHANGE: Updated font and added padding
        tk.Label(self.control_frame, text="Controls", font=("Helvetica", 14, "bold"), bg='white').pack(pady=(0, 15))
        # STYLE CHANGE: Modern button styling with hover effect
        tk.Button(self.control_frame, text="Step", command=self.step, width=15, bg='#007bff', fg='white', 
                 font=("Helvetica", 10), relief='flat', activebackground='#0056b3').pack(pady=8)
        tk.Button(self.control_frame, text="Show FSM", command=self.draw_fsm, width=15, bg='#28a745', fg='white', 
                 font=("Helvetica", 10), relief='flat', activebackground='#218838').pack(pady=8)
        tk.Button(self.control_frame, text="Exit", command=self.master.quit, width=15, bg='#dc3545', fg='white', 
                 font=("Helvetica", 10), relief='flat', activebackground='#c82333').pack(pady=8)

        # Floor pickup buttons
        # STYLE CHANGE: Enhanced typography and spacing
        tk.Label(self.control_frame, text="Pickup Requests", font=("Helvetica", 14, "bold"), bg='white').pack(pady=(25, 10))
        for floor in reversed(range(self.min_floor, self.max_floor + 1)):
            # STYLE CHANGE: Gradient-like button color and rounded edges
            btn = tk.Button(self.control_frame, text=f"Request at Floor {floor}", width=20,
                          command=lambda f=floor: self.pickup(f), bg='#6c757d', fg='white', 
                          font=("Helvetica", 10), relief='flat', activebackground='#5a6268')
            btn.pack(pady=4, padx=5)
            # STYLE CHANGE: Add hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#5a6268'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#6c757d'))

        # Elevator shafts
        # STYLE CHANGE: Centered and modernized header
        tk.Label(self.shaft_frame, text="Elevators", font=("Helvetica", 14, "bold"), bg='#e8ecef').grid(row=0, column=0, columnspan=self.elevator_count + 1, pady=(0, 10))
        
        total_rows = (self.max_floor - self.min_floor) + 2
        
        for i, floor in enumerate(reversed(range(self.min_floor, self.max_floor + 1))):
            row = i + 1
            # STYLE CHANGE: Improved floor label styling
            tk.Label(self.shaft_frame, text=f"Floor {floor}", width=10, font=("Helvetica", 10), bg='#e8ecef').grid(row=row, column=0, pady=2)
            
            floor_row = []
            for eid in range(self.elevator_count):
                # STYLE CHANGE: Added shadow and modern look to elevator cells
                lbl = tk.Label(self.shaft_frame, text=' ', width=5, height=2, relief='ridge', bg='white', 
                              font=("Helvetica", 10), bd=1)
                lbl.grid(row=row, column=eid + 1, padx=3, pady=3)
                floor_row.append(lbl)
            self.elevator_labels.append(floor_row)

        # Emergency buttons row
        emergency_row = (self.max_floor - self.min_floor) + 2
        
        for eid in range(self.elevator_count):
            # STYLE CHANGE: Enhanced emergency button with icon and modern styling
            btn = tk.Button(
                self.shaft_frame,
                text=f"E{eid} 🚨",
                width=5,
                bg="#f8f9fa",
                fg="black",
                font=("Helvetica", 10),
                relief='flat',
                command=lambda eid=eid: self.toggle_emergency(eid),
                activebackground='#e9ecef'
            )
            btn.grid(row=emergency_row, column=eid + 1, pady=(15, 0))
            self.emergency_buttons.append(btn)

        # Status labels
        for i in range(self.elevator_count):
            # STYLE CHANGE: Monospace font with better readability
            lbl = tk.Label(self.status_frame, text="", font=("Courier New", 11), anchor='w', bg='#f0f2f5')
            lbl.pack(fill=tk.X, padx=10, pady=2)
            self.status_labels.append(lbl)

        self.update_visuals()

    def pickup(self, floor):
        available_elevators = [e for e in self.system.elevators if not e.is_emergency]
        if not available_elevators:
            # STYLE CHANGE: Updated error message to show in a messagebox
            tk.messagebox.showwarning("Warning", "All elevators are in emergency mode!")
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
            # STYLE CHANGE: More vivid emergency color
            btn.config(bg="#dc3545", fg="white")
            elevator.up_destinations.clear()
            elevator.down_destinations.clear()
            elevator.direction = Direction.STAY
            elevator.open_doors = True
        else:
            # STYLE CHANGE: Reset to neutral color
            btn.config(bg="#f8f9fa", fg="black")
        
        self.update_visuals()

    def ask_if_destination(self, elevator_id, current_floor):
        popup = tk.Toplevel(self.master)
        popup.title(f"Elevator {elevator_id} at Floor {current_floor}")
        # STYLE CHANGE: Styled popup window
        popup.configure(bg='#f8f9fa')
        
        # STYLE CHANGE: Enhanced popup label styling
        tk.Label(popup, text=f"Elevator {elevator_id} doors are open at Floor {current_floor}.", 
                font=("Helvetica", 11, "bold"), bg='#f8f9fa').pack(pady=15)
        tk.Label(popup, text="Would you like to choose a destination?", font=("Helvetica", 10), bg='#f8f9fa').pack(pady=5)

        btn_frame = tk.Frame(popup, bg='#f8f9fa')
        btn_frame.pack(pady=10)

        # STYLE CHANGE: Modern button styling for popup
        yes_btn = tk.Button(btn_frame, text="Yes", width=10, bg='#007bff', fg='white', 
                           font=("Helvetica", 10), relief='flat', activebackground='#0056b3',
                           command=lambda: self.show_destination_buttons(current_floor, elevator_id, popup))
        yes_btn.grid(row=0, column=0, padx=8)

        no_btn = tk.Button(btn_frame, text="No", width=10, bg='#6c757d', fg='white', 
                          font=("Helvetica", 10), relief='flat', activebackground='#5a6268',
                          command=popup.destroy)
        no_btn.grid(row=0, column=1, padx=8)

    def show_destination_buttons(self, current_floor, elevator_id, parent_popup):
        parent_popup.destroy()

        popup = tk.Toplevel(self.master)
        popup.title(f"Choose Destination for Elevator {elevator_id}")
        # STYLE CHANGE: Consistent popup styling
        popup.configure(bg='#f8f9fa')

        # STYLE CHANGE: Enhanced typography
        tk.Label(popup, text="Select destination floor:", font=("Helvetica", 11, "bold"), bg='#f8f9fa').pack(pady=10)

        for floor in range(self.min_floor, self.max_floor + 1):
            if floor == current_floor:
                continue
            # STYLE CHANGE: Modern floor selection buttons
            btn = tk.Button(popup, text=f"Floor {floor}", bg='#28a745', fg='white', 
                          font=("Helvetica", 10), relief='flat', activebackground='#218838',
                          command=lambda f=floor, eid=elevator_id, cf=current_floor, win=popup: 
                          self.choose_destination(f, eid, cf, win))
            btn.pack(padx=15, pady=4)

    def choose_destination(self, floor, elevator_id, current_floor, popup_window):
        direction = Direction.UP if floor > current_floor else Direction.DOWN
        self.system.elevators[elevator_id].add_destination(floor, direction)
        popup_window.destroy()
        self.update_visuals()

    def draw_fsm(self):
        fsm_window = tk.Toplevel(self.master)
        fsm_window.title("Elevator System FSM")
        fsm_window.geometry("1000x800")
        # STYLE CHANGE: Consistent background for FSM window
        fsm_window.configure(bg='#f8f9fa')

        dot = Digraph('fsm', format='png')
        # STYLE CHANGE: Modernized FSM graph styling
        dot.attr(rankdir='TB', size='10,8')
        dot.attr('graph', bgcolor='#f8f9fa', fontname='Helvetica')
        dot.attr('edge', fontname='Helvetica', fontsize='12', arrowsize='1.2')

        # Define states with styles
        # STYLE CHANGE: Updated colors for better contrast
        dot.node("IDLE", style='filled', fillcolor='#add8e6', shape='ellipse')
        dot.node("MOVING_UP", style='filled', fillcolor='#fff3cd', shape='box')
        dot.node("MOVING_DOWN", style='filled', fillcolor='#fff3cd', shape='box')
        dot.node("DOORS_OPEN", style='filled', fillcolor='#c3e6cb', shape='diamond')
        dot.node("EMERGENCY_STOP", style='filled', fillcolor='#dc3545', fontcolor='white', shape='octagon')

        transitions = [
            ("IDLE", "MOVING_UP", "Pickup above"),
            ("IDLE", "MOVING_DOWN", "Pickup below"),
            ("MOVING_UP", "DOORS_OPEN", "Reach destination"),
            ("MOVING_DOWN", "DOORS_OPEN", "Reach destination"),
            ("DOORS_OPEN", "IDLE", "No destinations"),
            ("DOORS_OPEN", "MOVING_UP", "New pickup above"),
            ("DOORS_OPEN", "MOVING_DOWN", "New pickup below"),
            ("IDLE", "EMERGENCY_STOP", "Emergency", True),
            ("MOVING_UP", "EMERGENCY_STOP", "Emergency", True),
            ("MOVING_DOWN", "EMERGENCY_STOP", "Emergency", True),
            ("DOORS_OPEN", "EMERGENCY_STOP", "Emergency", True),
            ("EMERGENCY_STOP", "IDLE", "Emergency cleared")
        ]

        for t in transitions:
            from_state, to_state, label = t[0], t[1], t[2]
            is_critical = len(t) > 3 and t[3]
            if is_critical:
                # STYLE CHANGE: Enhanced critical transition styling
                dot.edge(from_state, to_state, label=label, style='bold', color='#dc3545', fontcolor='#dc3545')
            else:
                dot.edge(from_state, to_state, label=label)

        output_path = 'fsm_diagram'
        dot.render(output_path, view=False)

        image = Image.open(f"{output_path}.png")
        image = image.resize((900, 700), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        # STYLE CHANGE: Consistent canvas background
        canvas = tk.Canvas(fsm_window, width=1000, height=800, bg='#f8f9fa')
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(500, 400, image=photo, anchor='center')
        canvas.image = photo

        os.remove(f"{output_path}.png")
        if os.path.exists(f"{output_path}"):
            os.remove(f"{output_path}")

    def update_visuals(self):
        for row in self.elevator_labels:
            for lbl in row:
                # STYLE CHANGE: Reset to clean white with shadow
                lbl.config(bg='white', text=' ', relief='ridge')

        for elevator in self.system.elevators:
            floor = elevator.current_floor
            eid = elevator.id
            row_index = (self.max_floor - floor)
            if 0 <= row_index < len(self.elevator_labels):
                label = self.elevator_labels[row_index][eid]
                
                if elevator.is_emergency:
                    # STYLE CHANGE: Vivid emergency color
                    label.config(bg='#dc3545', text='STOP', fg='white')
                elif elevator.open_doors:
                    # STYLE CHANGE: Softer green for open doors
                    label.config(bg='#28a745', text='OPEN', fg='white')
                else:
                    # STYLE CHANGE: Modern blue for active elevator
                    label.config(bg='#007bff', text=f'E{eid}', fg='white')

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
    # STYLE CHANGE: Set background to match the blue header from the image
    popup.configure(bg='#007bff')

    # STYLE CHANGE: Create a frame with white background and padding to mimic the card layout
    main_frame = tk.Frame(popup, bg='white', padx=20, pady=20)
    main_frame.place(relx=0.5, rely=0.5, anchor='center')

    # STYLE CHANGE: Use ttk for styled entry fields with modern look
    style = ttk.Style()
    style.configure("Custom.TEntry", fieldbackground="white", background="white", borderwidth=1)
    style.map("Custom.TEntry", background=[('disabled', 'gray'), ('active', 'white')])

    # Elevator count
    # STYLE CHANGE: Styled label and entry to match the image's typography and layout
    tk.Label(main_frame, text="Number of elevators:", font=("Arial", 12), bg='white').pack(pady=(0, 5))
    entry_count = ttk.Entry(main_frame, style="Custom.TEntry", font=("Arial", 11))
    entry_count.pack(pady=(0, 10))
    entry_count.insert(0, "3")

    # Min floor
    tk.Label(main_frame, text="Minimum floor:", font=("Arial", 12), bg='white').pack(pady=(0, 5))
    entry_min = ttk.Entry(main_frame, style="Custom.TEntry", font=("Arial", 11))
    entry_min.pack(pady=(0, 10))
    entry_min.insert(0, "0")

    # Max floor
    tk.Label(main_frame, text="Maximum floor:", font=("Arial", 12), bg='white').pack(pady=(0, 5))
    entry_max = ttk.Entry(main_frame, style="Custom.TEntry", font=("Arial", 11))
    entry_max.pack(pady=(0, 10))
    entry_max.insert(0, "9")

    # STYLE CHANGE: Error label with red text and centered alignment
    error_lbl = tk.Label(main_frame, text="", font=("Arial", 10), fg="#dc3545", bg='white')
    error_lbl.pack(pady=(0, 10))

    # STYLE CHANGE: Custom button style with rounded corners and blue color from the image
    style.configure("Custom.TButton", background="#007bff", foreground="white", font=("Arial", 11), padding=6)
    style.map("Custom.TButton", background=[('active', '#0056b3')], foreground=[('active', 'white')])
    ttk.Button(main_frame, text="Start", command=confirm, style="Custom.TButton").pack(pady=(0, 20))

    popup.mainloop()

def start_main_app(elevator_count, min_floor, max_floor):
    root = tk.Tk()
    app = ElevatorSystemGUI(root, elevator_count=elevator_count, min_floor=min_floor, max_floor=max_floor)
    root.mainloop()

if __name__ == "__main__":
    ask_elevator_config()
