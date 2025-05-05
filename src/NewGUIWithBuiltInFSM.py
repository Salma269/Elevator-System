import tkinter as tk
from enum import Enum
from elevator import Elevator
from direction import Direction
from elevatorsystem import ElevatorSystem
from graphviz import Digraph
from PIL import Image, ImageTk
import os
from tkinter import ttk
import tkinter.messagebox

class ElevatorSystemGUI:
    def __init__(self, master, elevator_count=4, min_floor=0, max_floor=9):
        self.master = master
        self.master.title("Elevator System Simulation")

        # Modern color scheme
        self.bg_color = '#f8f9fa'
        self.card_color = '#ffffff'
        self.primary_color = '#4e73df'
        self.secondary_color = '#6c757d'
        self.success_color = '#28a745'
        self.danger_color = '#dc3545'
        self.warning_color = '#ffc107'
        self.text_color = '#343a40'
        self.border_color = '#dee2e6'

        self.master.configure(bg=self.bg_color)

        self.elevator_count = elevator_count
        self.min_floor = min_floor
        self.max_floor = max_floor
        self.system = ElevatorSystem(elevator_count)
        self.pickups = set()

        self.elevator_labels = []
        self.status_labels = []
        self.emergency_buttons = []

        self.setup_ui()
        self.adjust_window_size()

    def adjust_window_size(self):
        self.master.update_idletasks()

        # Calculate required height based on number of floors
        floor_height = 30  # Approximate height per floor
        min_height = 500   # Minimum window height
        calculated_height = (self.max_floor - self.min_floor + 1) * floor_height + 450
        window_height = max(min_height, calculated_height)

        # Calculate required width based on number of elevators
        elevator_width = 80  # Approximate width per elevator
        min_width = 800      # Minimum window width
        calculated_width = self.elevator_count * elevator_width + 500
        window_width = max(min_width, calculated_width)

        # Set window size and center it
        self.master.geometry(f"{window_width}x{window_height}")
        x = (self.master.winfo_screenwidth() - window_width) // 2
        y = (self.master.winfo_screenheight() - window_height) // 2
        self.master.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Create main container with modern styling
        main_container = tk.Frame(self.master, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create a frame for the elevator shafts and status bar
        center_frame = tk.Frame(main_container, bg=self.bg_color)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Elevator shafts - centered in the middle
        self.shaft_frame = tk.Frame(center_frame, bg=self.card_color, bd=0,
                                    highlightbackground=self.border_color,
                                    highlightthickness=1, padx=15, pady=15)
        self.shaft_frame.pack(fill=tk.BOTH, expand=True)

        # Status bar - bottom of center frame
        self.status_frame = tk.Frame(center_frame, bg=self.card_color, bd=0,
                                     highlightbackground=self.border_color,
                                     highlightthickness=1)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))

        # Right side panel for controls and pickup requests (narrower)
        right_panel = tk.Frame(main_container, bg=self.bg_color, width=250)  # Fixed width
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)  # Prevent width changes

        # Control panel - top of right panel
        self.control_frame = tk.Frame(right_panel, bg=self.card_color, bd=0,
                                      highlightbackground=self.border_color,
                                      highlightthickness=1, padx=15, pady=15)
        self.control_frame.pack(fill=tk.X)

        # Pickup requests panel - takes remaining space in right panel
        self.pickup_frame = tk.Frame(right_panel, bg=self.card_color, bd=0,
                                     highlightbackground=self.border_color,
                                     highlightthickness=1)
        self.pickup_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Configure styles
        self.configure_styles()

        # Build UI components
        self.build_control_panel()
        self.build_elevator_shafts()
        self.build_status_bar()
        self.build_pickup_panel()

        self.update_visuals()

    def configure_styles(self):
        # Button styles
        style = ttk.Style()
        style.theme_use('clam')

        # Primary button
        style.configure('Primary.TButton',
                        background=self.primary_color,
                        foreground='white',
                        font=('Helvetica', 10, 'bold'),
                        borderwidth=0,
                        focusthickness=0,
                        focuscolor='none',
                        padding=8)
        style.map('Primary.TButton',
                  background=[('active', '#3a56b0'), ('pressed', '#2c4293')])

        # Secondary button
        style.configure('Secondary.TButton',
                        background=self.secondary_color,
                        foreground='white',
                        font=('Helvetica', 10),
                        borderwidth=0,
                        focusthickness=0,
                        focuscolor='none',
                        padding=8)  # Consistent padding
                        #width=10)  # Fixed width
        style.map('Secondary.TButton',
                  background=[('active', '#5a6268'), ('pressed', '#484e53')])

        # Success button
        style.configure('Success.TButton',
                        background=self.success_color,
                        foreground='white',
                        font=('Helvetica', 10, 'bold'),
                        padding=8)
        style.map('Success.TButton',
                  background=[('active', '#218838'), ('pressed', '#1e7e34')])

        # Danger button
        style.configure('Danger.TButton',
                        background=self.danger_color,
                        foreground='white',
                        font=('Helvetica', 10, 'bold'),
                        borderwidth=0,
                        focusthickness=0,
                        focuscolor='none',
                        padding=8,  # Consistent padding
                        width=10)  # Fixed width
        style.map('Danger.TButton',
                  background=[('active', '#c82333'), ('pressed', '#bd2130')])

    def build_control_panel(self):
        # Header
        header = tk.Label(self.control_frame, text="Controls",
                          font=('Helvetica', 14, 'bold'), bg=self.card_color)
        header.pack(pady=(0, 15))

        # Action buttons
        btn_frame = tk.Frame(self.control_frame, bg=self.card_color)
        btn_frame.pack(pady=(0, 10))

        ttk.Button(btn_frame, text="Step", style='Primary.TButton',
                   command=self.step).pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Show FSM", style='Success.TButton',
                   command=self.draw_fsm).pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Exit", style='Danger.TButton',
                   command=self.master.quit).pack(fill=tk.X, pady=5)

    def build_pickup_panel(self):
        # Pickup requests section
        pickup_header = tk.Label(self.pickup_frame, text="Pickup Requests",
                             font=('Helvetica', 14, 'bold'), bg=self.card_color)
        pickup_header.pack(pady=(0, 10))

        # Scrollable frame for pickup buttons
        pickup_canvas = tk.Canvas(self.pickup_frame, bg=self.card_color,
                              highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.pickup_frame, orient="vertical",
                              command=pickup_canvas.yview)
        scrollable_frame = tk.Frame(pickup_canvas, bg=self.card_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: pickup_canvas.configure(
                scrollregion=pickup_canvas.bbox("all")
            )
        )

        pickup_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        pickup_canvas.configure(yscrollcommand=scrollbar.set)

        pickup_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add pickup buttons to scrollable frame
        for floor in reversed(range(self.min_floor, self.max_floor + 1)):
            btn = ttk.Button(scrollable_frame,
                             text=f"Request at Floor {floor}",
                             style='Secondary.TButton',
                             command=lambda f=floor: self.pickup(f))
            btn.pack(fill=tk.X, pady=4, padx=5)




    def build_elevator_shafts(self):
        # Header
        header = tk.Label(self.shaft_frame, text="Elevators",
                          font=('Helvetica', 14, 'bold'), bg=self.card_color)
        header.pack(pady=(0, 15))

        # Create a frame to center the elevators
        center_container = tk.Frame(self.shaft_frame, bg=self.card_color)
        center_container.pack(expand=True)

        # Create floor labels and elevator cells
        for i, floor in enumerate(reversed(range(self.min_floor, self.max_floor + 1))):
            row_frame = tk.Frame(center_container, bg=self.card_color)
            row_frame.pack()

            # Floor label
            floor_lbl = tk.Label(row_frame, text=f"Floor {floor}",
                                 width=10, font=('Helvetica', 10),
                                 bg=self.card_color, anchor='w')
            floor_lbl.pack(side=tk.LEFT, pady=2)

            # Elevator cells for this floor
            floor_row = []
            for eid in range(self.elevator_count):
                cell = tk.Label(row_frame, text=' ', width=5, height=2,
                                relief='groove', bg='white', font=('Helvetica', 10),
                                bd=1, highlightbackground=self.border_color)
                cell.pack(side=tk.LEFT, padx=3, pady=3)
                floor_row.append(cell)
            self.elevator_labels.append(floor_row)

        # Emergency buttons row
        emergency_frame = tk.Frame(center_container, bg=self.card_color)
        emergency_frame.pack(pady=(15, 0))

        # Add spacer for floor label column
        tk.Label(emergency_frame, text="", width=10, bg=self.card_color).pack(side=tk.LEFT)

        for eid in range(self.elevator_count):
            btn = ttk.Button(
                emergency_frame,
                text=f"E{eid} 🚨",
                style='Secondary.TButton',  # Start with Secondary style
                command=lambda eid=eid: self.toggle_emergency(eid)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.emergency_buttons.append(btn)

    def build_status_bar(self):
        # Status header
        header = tk.Label(self.status_frame, text="Elevator Status",
                          font=('Helvetica', 12, 'bold'), bg=self.card_color)
        header.pack(anchor='w', padx=10, pady=(5, 10))

        # Status labels container
        status_container = tk.Frame(self.status_frame, bg=self.card_color)
        status_container.pack(fill=tk.X, padx=10, pady=(0, 5))

        # Create status labels with monospace font for alignment
        for i in range(self.elevator_count):
            lbl = tk.Label(status_container, text="", font=('Consolas', 10),
                           anchor='w', bg=self.card_color, fg=self.text_color)
            lbl.pack(fill=tk.X, pady=2)
            self.status_labels.append(lbl)

    def pickup(self, floor):
        available_elevators = [e for e in self.system.elevators if not e.is_emergency]
        if not available_elevators:
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
            btn.config(style='Danger.TButton')
            elevator.up_destinations.clear()
            elevator.down_destinations.clear()
            elevator.direction = Direction.STAY
            elevator.open_doors = True
        else:
            btn.config(style='Secondary.TButton')

        self.update_visuals()

    def ask_if_destination(self, elevator_id, current_floor):
        popup = tk.Toplevel(self.master)
        popup.title(f"Elevator {elevator_id} at Floor {current_floor}")
        popup.configure(bg=self.bg_color)
        popup.resizable(False, False)

        # Create card-like container
        container = tk.Frame(popup, bg=self.card_color, padx=20, pady=20,
                             highlightbackground=self.border_color,
                             highlightthickness=1)
        container.pack(padx=20, pady=20)

        # Message
        tk.Label(container,
                 text=f"Elevator {elevator_id} doors are open at Floor {current_floor}.",
                 font=('Helvetica', 11, 'bold'), bg=self.card_color).pack(pady=(0, 10))

        tk.Label(container,
                 text="Would you like to choose a destination?",
                 font=('Helvetica', 10), bg=self.card_color).pack(pady=(0, 15))

        # Button frame
        btn_frame = tk.Frame(container, bg=self.card_color)
        btn_frame.pack(pady=(0, 5))

        ttk.Button(btn_frame, text="Yes", style='Primary.TButton',
                   command=lambda: self.show_destination_buttons(current_floor, elevator_id, popup)
                   ).grid(row=0, column=0, padx=5)

        ttk.Button(btn_frame, text="No", style='Secondary.TButton',
                   command=popup.destroy).grid(row=0, column=1, padx=5)

        # Center the popup
        popup.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

    def show_destination_buttons(self, current_floor, elevator_id, parent_popup):
        parent_popup.destroy()

        popup = tk.Toplevel(self.master)
        popup.title(f"Choose Destination for Elevator {elevator_id}")
        popup.configure(bg=self.bg_color)
        popup.resizable(False, False)

        # Create card-like container
        container = tk.Frame(popup, bg=self.card_color, padx=20, pady=20,
                             highlightbackground=self.border_color,
                             highlightthickness=1)
        container.pack(padx=20, pady=20)

        # Title
        tk.Label(container,
                 text="Select destination floor:",
                 font=('Helvetica', 11, 'bold'), bg=self.card_color).pack(pady=(0, 15))

        # Floor buttons grid
        grid_frame = tk.Frame(container, bg=self.card_color)
        grid_frame.pack()

        floors = [f for f in range(self.min_floor, self.max_floor + 1) if f != current_floor]
        cols = 3  # Number of columns in the grid
        for i, floor in enumerate(floors):
            btn = ttk.Button(grid_frame, text=f"Floor {floor}", style='Success.TButton',
                             command=lambda f=floor, eid=elevator_id, cf=current_floor, win=popup:
                             self.choose_destination(f, eid, cf, win))
            btn.grid(row=i//cols, column=i%cols, padx=5, pady=5, sticky='nsew')

        # Center the popup
        popup.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

    def choose_destination(self, floor, elevator_id, current_floor, popup_window):
        direction = Direction.UP if floor > current_floor else Direction.DOWN
        self.system.elevators[elevator_id].add_destination(floor, direction)
        popup_window.destroy()
        self.update_visuals()

    def draw_fsm(self):
        fsm_window = tk.Toplevel(self.master)
        fsm_window.title("Elevator System FSM")
        fsm_window.geometry("1000x800")
        fsm_window.configure(bg=self.bg_color)

        dot = Digraph('fsm', format='png')
        dot.attr(rankdir='TB', size='10,8')
        dot.attr('graph', bgcolor=self.bg_color, fontname='Helvetica')
        dot.attr('edge', fontname='Helvetica', fontsize='12', arrowsize='1.2')

        # Define states with styles
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
                dot.edge(from_state, to_state, label=label, style='bold', color='#dc3545', fontcolor='#dc3545')
            else:
                dot.edge(from_state, to_state, label=label)

        output_path = 'fsm_diagram'
        dot.render(output_path, view=False)

        image = Image.open(f"{output_path}.png")
        image = image.resize((900, 700), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        canvas = tk.Canvas(fsm_window, width=1000, height=800, bg=self.bg_color)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(500, 400, image=photo, anchor='center')
        canvas.image = photo

        os.remove(f"{output_path}.png")
        if os.path.exists(f"{output_path}"):
            os.remove(f"{output_path}")

    def update_visuals(self):
        for row in self.elevator_labels:
            for lbl in row:
                lbl.config(bg='white', text=' ', relief='groove')

        for elevator in self.system.elevators:
            floor = elevator.current_floor
            eid = elevator.id
            row_index = (self.max_floor - floor)
            if 0 <= row_index < len(self.elevator_labels):
                label = self.elevator_labels[row_index][eid]

                if elevator.is_emergency:
                    label.config(bg=self.danger_color, text='STOP', fg='white')
                elif elevator.open_doors:
                    label.config(bg=self.success_color, text='OPEN', fg='white')
                else:
                    direction_symbol = '↑' if elevator.direction == Direction.UP else '↓' if elevator.direction == Direction.DOWN else '•'
                    label.config(bg=self.primary_color, text=f'E{eid} {direction_symbol}', fg='white')

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
    popup.title("Elevator System Configuration")

    # Modern styling variables
    bg_color = "#f8f9fa"  # Light gray background
    card_color = "#ffffff"  # White card
    primary_color = "#4e73df"  # Nice blue
    text_color = "#5a5c69"  # Dark gray text
    error_color = "#e74a3b"  # Red for errors
    border_color = "#dddfeb"  # Light border
    button_hover = "#2e59d9"  # Darker blue for button hover

    # Set window background
    popup.configure(bg=bg_color)

    # Create a card-like container frame with shadow effect
    main_frame = tk.Frame(popup, bg=card_color, padx=30, pady=30,
                          highlightbackground=border_color, highlightthickness=1)
    main_frame.pack(padx=0, pady=0)  # Changed from place() to pack() for proper sizing

    # Header with icon (using text as icon placeholder)
    header_frame = tk.Frame(main_frame, bg=card_color)
    header_frame.pack(pady=(0, 20))

    tk.Label(header_frame, text="⏏️", font=("Arial", 24), bg=card_color, fg=primary_color).pack(side=tk.LEFT)
    tk.Label(header_frame, text=" Elevator Configuration", font=("Arial", 16, "bold"),
             bg=card_color, fg=text_color).pack(side=tk.LEFT, padx=10)

    # Configure ttk styles
    style = ttk.Style()

    # Entry style
    style.configure("Custom.TEntry",
                    fieldbackground=card_color,
                    foreground=text_color,
                    bordercolor=border_color,
                    lightcolor=border_color,
                    darkcolor=border_color,
                    padding=5,
                    relief="flat",
                    font=("Arial", 11))

    # Button style
    style.configure("Primary.TButton",
                    background=primary_color,
                    foreground="blue",
                    font=("Arial", 11, "bold"),
                    padding=8,
                    borderwidth=0,
                    focusthickness=0,
                    focuscolor=primary_color)
    style.map("Primary.TButton",
              background=[('active', button_hover), ('pressed', button_hover)],
              foreground=[('active', 'blue'), ('pressed', 'blue')])

    # Input fields container
    inputs_frame = tk.Frame(main_frame, bg=card_color)
    inputs_frame.pack(pady=(0, 20))

    def create_input_field(parent, label_text, default_value):
        frame = tk.Frame(parent, bg=card_color)
        frame.pack(pady=(0, 15), fill=tk.X)

        tk.Label(frame, text=label_text, font=("Arial", 11),
                 bg=card_color, fg=text_color).pack(anchor=tk.W)

        entry = ttk.Entry(frame, style="Custom.TEntry", font=("Arial", 11))
        entry.pack(fill=tk.X, pady=(5, 0))
        entry.insert(0, default_value)

        return entry

    # Create input fields
    entry_count = create_input_field(inputs_frame, "Number of elevators:", "3")
    entry_min = create_input_field(inputs_frame, "Minimum floor:", "0")
    entry_max = create_input_field(inputs_frame, "Maximum floor:", "9")

    # Error label
    error_lbl = tk.Label(main_frame, text="", font=("Arial", 10),
                         fg=error_color, bg=card_color)
    error_lbl.pack(pady=(0, 15))

    # Start button
    ttk.Button(main_frame, text="Start Simulation", command=confirm,
               style="Primary.TButton").pack(fill=tk.X)

    # Calculate and set window size to match form content
    popup.update_idletasks()  # Update to get correct widget sizes

    # Get the required width and height of the main frame
    width = main_frame.winfo_reqwidth()
    height = main_frame.winfo_reqheight()

    # Set the window size (add a small buffer for window borders)
    popup.geometry(f"{width+4}x{height+4}")

    # Center the window on screen
    x = (popup.winfo_screenwidth() // 2) - (width // 2)
    y = (popup.winfo_screenheight() // 2) - (height // 2)
    popup.geometry(f"+{x}+{y}")

    # Prevent window resizing
    popup.resizable(False, False)

    popup.mainloop()

def start_main_app(elevator_count, min_floor, max_floor):
    root = tk.Tk()
    app = ElevatorSystemGUI(root, elevator_count=elevator_count, min_floor=min_floor, max_floor=max_floor)
    root.mainloop()

if __name__ == "__main__":
    ask_elevator_config()
