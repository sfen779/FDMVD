import time
import random

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

array_sizes = [100, 1000, 10000, 100000]
for size in array_sizes:
    data = [random.randint(0, 100000) for _ in range(size)]
    start_time = time.time()
    sorted_data = quick_sort(data)
    end_time = time.time()
    print(f"Size: {size}, Time: {end_time - start_time}")