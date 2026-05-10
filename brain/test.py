
from labscript import *

class car():

    # init function
    def __init__(self, wheel_count, name):

        self.wheel_count = wheel_count
        self.name = name
        
    # class "method"
    def drive(self):
        
        print(f"Driving {self.name}")



    def add_numbers(a, b):
        return a + b



stupid_car = car(4, "poop car")

stupid_car.drive()


sum = car.add_numbers(1, 2)
print(sum)


print(math.acos(0.2))