from tqdm.contrib.concurrent import process_map
import time

# Define a function that will be applied to each item in the iterable
def square(n):
    time.sleep(0.5)  # Simulate a time-consuming operation
    return n ** 2

# Define an iterable
numbers = range(100)

# Use process_map to apply the function to each item in the iterable in parallel
squares = process_map(square, numbers, max_workers=4)

print(squares)