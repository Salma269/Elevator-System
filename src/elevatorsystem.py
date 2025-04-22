from elevator import Elevator
from direction import Direction


class ElevatorSystem:
    def __init__(self, elevator_count=4):
        self.elevators = [Elevator(i) for i in range(elevator_count)]

    def __str__(self):
        return '\n'.join(map(str, self.elevators))

    def pickup(self, floor, direction_value):
        '''
            executed when the button next to an elevator is pressed
        '''
        direction = Direction.STAY

        if direction_value > 0:
            direction = Direction.UP
        elif direction_value < 0:
            direction = Direction.DOWN

        # choosing an elevator
        elevator_pick = min(
            self.elevators, key=lambda elevator: elevator.get_destination_count())

        elevator_pick.add_destination(floor, direction)

    def choose_floor(self, elevatorId, current_floor, floor):
        '''
            executed when the button inside an elevator is pressed
        '''
        direction = Direction.STAY
        if current_floor < floor:
            direction = Direction.UP
        elif current_floor > floor:
            direction = Direction.DOWN

        self.elevators[elevatorId].add_destination(floor, direction)

    def step(self):
        '''
            move all elevators by max 1 floor
        '''
        for elevator in self.elevators:
            elevator.move()

    def get_open_doors(self, floor):
        '''
            returns a set of elevator ids of those which currently have their doors open on the specific floor
        '''
        open_elevators = set()

        for elevator in self.elevators:
            if elevator.current_floor == floor and elevator.open_doors:
                open_elevators.add(elevator.id)

        return open_elevators

    def get_status(self):
        '''
            returns a list of tuples representing the state of each elevator
        '''
        return [elevator.get_status() for elevator in self.elevators]
