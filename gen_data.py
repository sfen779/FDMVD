import time
import random
import os

import pandas as pd
def generate_single_dependency(in_chunk_id,universe,test_id):
    # Generate a single dependency
    dep_type = 'FD' if random.random() < 0.5 else 'MVD'
    lhs = []
    rhs = []
    # Generate LHS - ensure at least one attribute
    while len(lhs) == 0 or random.random() > 0.25:
        attr = random.choice(universe)
        if attr not in lhs:
            lhs.append(attr)

        # Generate RHS - ensure at least one attribute
    while len(rhs) == 0 or random.random() > 0.25:
        attr = random.choice(universe)
        if attr not in rhs and attr not in lhs:
            rhs.append(attr)
                # current_size += 1
            if dep_type == 'FD':
                break  # Only one attribute on the RHS for FDs
    return [in_chunk_id,test_id,dep_type,lhs,rhs]


def generate_dependencies_struct(target_size, universe,test_id=0):
    dependencies = []
    
    start_time = time.time()

    for current_size in range(0, target_size):
        # Append the generated dependency to the list
        dep = generate_single_dependency(current_size, universe,test_id)
        dependencies.append(dep)

    end_time = time.time()
    return dependencies, end_time - start_time

def gen_dependency_pandas(file_path, file_name, test_id, target_size, chunk_size=1000000, universe_size=1000):
    '''
    generate the dependencies and save the data to a pandas dataframe
    '''

    # Generate the dependencies
    columns = ["ID","test_id","dep_type", "lhs", "rhs"]

    # get the size of the dependency test data
    universe = list(range(universe_size))  # Large pool of attribute identifiers
    total_gen_time = 0

    for start in range(0, target_size, chunk_size):
        end = min(start + chunk_size, target_size)
        time.sleep(0.1)  # don't take 100% CPU
        dependency,temp_time = generate_dependencies_struct(end-start, universe, test_id)
        df = pd.DataFrame(dependency, columns=columns)
        df.to_csv(file_path, mode='a', header=not os.path.exists(file_name), index=False, sep=';')
        total_gen_time += temp_time
        
    # self.status_label.setText(f"Dependencies saved to {file_path}")
    print("Finished generating test data")
    return file_path, total_gen_time


if __name__ == '__main__':
    # deps, time_taken,X,universe = generate_dependencies(50)
    # deps, time_taken, X, universe = generate_dependencies_struct(target_size=50)
    # print(f"Universe: {universe}")
    # print(f"X: {X}")
    # for dep in deps:
    #     print(dep)
    # print(f"Time taken: {time_taken:.4f} seconds")
    
    dep = generate_single_dependency(1,[1,2,3,4,5,6,7,8,9,10])
    print(dep)