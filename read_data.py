import pandas as pd

def read_text_data(file_path):
    total_input_dict = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # Assuming the first line is for the universe, second for X, and remaining for MVDs
        if lines:
            for line in lines:
                    parts = line.split(':')
                    if len(parts) == 2:
                        if parts[0].strip() == "test":
                            index = parts[1].strip()
                            temp_dict = {}
                            MVDs = []
                            FDs = []
                        elif parts[0].strip() == "universe":
                            temp_universe = parts[1].strip()
                        elif parts[0].strip() == "X":
                            temp_X = parts[1].strip()
                        elif parts[0].strip() == "MVD":
                            MVDs.append(parts[1].strip())
                        elif parts[0].strip() == "FD":
                            FDs.append(parts[1].strip())
                    if line.strip() == "end:":
                        temp_dict["MVDs"] = MVDs
                        temp_dict["FDs"] = FDs
                        temp_dict["universe"] = temp_universe
                        temp_dict["X"] = temp_X
                        total_input_dict[f"test:{index}"] = temp_dict
    return total_input_dict

def read_csv_data(file_path, chunk_size = 10000):
    for chunk in pd.read_csv(file_path, chunksize=chunk_size, sep=';'):
        yield chunk
