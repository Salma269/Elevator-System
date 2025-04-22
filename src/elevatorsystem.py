from elevator import Elevator
from direction import Direction


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

