def dep_basis(X, V, G, F=[]):
    '''
    X: the leaft-hand side of the dependency (phased as a set)
    V: the set of attributes
    G: the set of MVDs
    F: the set of FDs
    '''
    # Initialize NEWD
    NEWX = set(X)
    complement_X = V - NEWX
    NEWD = [set([a]) for a in NEWX] + [complement_X]
    change_flag = True

    while change_flag:
        OLDX = NEWX
        OLDD = NEWD
        #FDs
        if F:
            for (W, Z) in F:
                W_set, V = set(W), set(Z)
                # Union of all R in NEWD intersecting with W
                DBU = set()
                for R in NEWD:
                    if type(R) == int or type(R) == str:
                        R = {R}
                    if type(R) == set or type(R) == frozenset:
                        if R & W_set:
                            if len(R) == 1:
                                DBU.add(*R)
                            else:
                                DBU.add(frozenset(R))
                DBV = V - DBU
                
                if DBV:
                    
                    X = X | DBV
                    NEWX = NEWX | DBV
                    NEWD = {frozenset(R - DBV) for R in NEWD if (isinstance(R, set) or isinstance(R,frozenset)) and R - DBV}
                    NEWD = NEWD | {A for A in DBV}
                    change_flag = True
        #MVDs
        if G:
            for (W, Z) in G:
                W_set, V = set(W), set(Z)
                DBU = set()
                for R in NEWD:
                    if isinstance(R, int) or isinstance(R, str):
                        R = {R}
                    if R & W_set:
                        if len(R) == 1:
                            DBU.add(*R)
                        else:
                            DBU.add(frozenset(R))
                DBV = V - DBU
                if DBV:
                    temp_D = NEWD.copy()
                    for R in temp_D:
                        if isinstance(R, int) or isinstance(R, str):
                            R = {R}
                        if R & DBV and R & DBV != R:
                            NEWD.remove(R)
                            right = {R & DBV, R - DBV}
                            NEWD = NEWD | right
                            change_flag = True
        if NEWX == OLDX and NEWD == OLDD:
            break
    XPULS = NEWX
    DEPBX = {frozenset({R}) for R in NEWD if isinstance(R, int) or isinstance(R,str)} | {R for R in NEWD if isinstance(R, set) or isinstance(R, frozenset)}
    return XPULS, DEPBX


def get_all_subsets(s):
    n = len(s)
    elements = list(s)
    all_subsets = []
    
    # 从 0 到 2^n - 1
    for i in range(2 ** n):
        subset = []
        for j in range(n):
            # 检查第 j 位是否是 1
            if i & (1 << j):
                subset.append(elements[j])
        all_subsets.append(subset)
    
    all_subsets = all_subsets + [frozenset(subset) for subset in s]
    
    return all_subsets


def membership_test(X, Y, V, G, F):
    '''
    X: the leaft-hand side of the dependency (phased as a set)
    Y: the right-hand side of the dependency (phased as a set)
    V: the set of attributes
    G: the set of MVDs
    F: the set of FDs
    '''
    # F, G = parse_dependencies(F, G)
    X_plus, dependency_basis = dep_basis(X, V, G, F)
    print("Resulting NEWD:",dependency_basis)
    all_possible_subsets = get_all_subsets(dependency_basis)
    for R in all_possible_subsets:
        if R == frozenset(Y):
            return True, dependency_basis
    return False, dependency_basis

# if __name__ == "__main__":
#     V = set(range(1000))  # A large set of attributes
#     FDs = [
#         "[576, 498, 619] -> [369]",
#         "[763, 463, 256] -> [328]",
#         "[188, 946, 850] -> [382]"
#     ]
#     MVDs = [
#         "[169, 467, 265] -> [593]",
#         "[579, 656, 888, 649] -> [545, 349]",
#         "[941] -> [864, 16]",
#         "[806, 726, 624, 752, 372, 385, 177, 282] -> [359]",
#         "[300, 54, 281, 388, 61, 561, 297, 510, 158, 129, 663] -> [276]"
#     ]
#     X = {576, 498, 619}  # Example set X, modify as needed

#     F, G = parse_dependencies(FDs, MVDs)
#     result = dep_basis(X, V, G, F)
#     print("Resulting BASIS:", result)
def parse_dependency_string(dep_string):
    # Remove brackets and split by '->'
    parts = dep_string.replace('[', '').replace(']', '').split(' -> ')
    if len(parts) != 2:
        raise ValueError("Invalid dependency string: " + dep_string)
    # Convert the left and right parts from string to sets of integers
    left = set(map(int, parts[0].split(', ')))
    right = set(map(int, parts[1].split(', ')))
    return (left, right)

def parse_dependency_test(dep_string):
    # Remove brackets and split by '->'
    print(dep_string)
    parts = dep_string.replace('[', '').replace(']', '').split(' -> ')

    #print(len(parts))
    if len(parts) != 2:
        raise ValueError("Invalid dependency string: " + dep_string)
    # Convert the left and right parts from string to sets of integers
    left = set(parts[0].split(', '))
    right = set(parts[1].split(', '))
    return (left, right)

def parse_single_dependency(dep_string):
    left, right = dep_string.split('->')
    left = set(map(int, left.strip('[]').split(', ')))
    right = set(map(int, right.strip('[]').split(', ')))
    return left, right

def parse_dependencies(fd_list, mvd_list):
    F = [parse_dependency_string(fd) for fd in fd_list]
    G = [parse_dependency_string(mvd) for mvd in mvd_list]
    return F, G

def parse_dependencies_test(fd_list, mvd_list):
    F = [parse_dependency_test(fd) for fd in fd_list]
    G = [parse_dependency_test(mvd) for mvd in mvd_list]
    return F, G


# if __name__ == "__main__":
#     V = set(["s_upi", "s_name", "s_email", "t_name", "c_name", "t_email", "e_time"])  # A large set of attributes
#     FDs = [
#         "[s_email] -> [c_name]"
#     ]
#     MVDs = [
#         "[s_upi, s_name] -> [s_email, t_name]",
#         "[s_email] -> [c_name]"
#     ]
#     X = {"s_upi", "s_name"}  # Example set X, modify as needed

#     F, G = parse_dependencies_test(FDs, MVDs)
#     result = dep_basis(X, V, G, F)
#     print("Resulting BASIS:", result)
    
if __name__ == "__main__":
    V = set(["A", "B", "C", "D", "E", "F", "G"])  # A large set of attributes
    FDs = [
        "[C] -> [E]"
    ]
    MVDs = [
        "[A, B] -> [C, D]",
        "[C] -> [F]"
    ]
    X = {"A", "B"}  # Example set X, modify as needed

    F, G = parse_dependencies_test(FDs, MVDs)
    xplus, depx = dep_basis(X, V, G, F)
    print("Resulting X+:", xplus)
    print("Resulting BASIS:", depx)