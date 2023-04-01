"""
    According to https://www.numbersaplenty.com/2023, there are exactly 2023 ways to tile a 4x4 grid using only L tiles and monominos. It does not clarify if rotations or reflections count as different ways, or prove the statement. This Python program will attempt to verify it.
"""
# Note: Profile by doing 'python -m cProfile -s tottime Tiling_2023.py'
import numpy as np, itertools as it, bisect as b, copy, math, matplotlib.pyplot as plt, matplotlib.ticker as mticker, functools, os

def setupCalculationGlobals(givenWidth, givenHeight):
    global WIDTH,  HEIGHT,  TOTAL,  MAX_POSSIBLE_L_TILES,  L_TILES,  LOCATIONS,  L_TILE_OFFSETS

    WIDTH = givenWidth
    HEIGHT = givenHeight
    TOTAL = WIDTH * HEIGHT
    #Locations is an ndarry of all the coordinates, where each coordinate is a 1d array in the form [y x], where [0 0] is top left
    LOCATIONS = []
    for h in range(HEIGHT):
        for w in range(WIDTH):
            LOCATIONS.append(np.array([h, w]))
    LOCATIONS = np.array(LOCATIONS)
    #offsets[i] are used calculate the other 2 tiles of an L tile of type i given the coord of its top left tile 
    L_TILE_OFFSETS = np.array(
            [
                [[0,1], [1,1]],   #TOP_RIGHT
                [[1, -1], [1,0]], #BOTTOM_RIGHT
                [[1,0], [1,1]],   #BOTTOM_LEFT
                [[1,0], [0, 1]]   #TOP_LEFT
            ]
        )
    # Note integer division below. Finds minimal size tile (minimum number of offsets + 1) and uses it to calculate maximum possible number of tiles
    MAX_POSSIBLE_L_TILES = TOTAL // (min(map(lambda l: len(l), L_TILE_OFFSETS)) + 1)
    L_TILES = np.array(range(len(L_TILE_OFFSETS))) 

def setupOutputGlobals(printIndividualTilings, printFilterTest, printProgress):
    global PRINT_INDIVIDUAL_TILINGS, PRINT_FILTER_TEST, PRINT_PROGRESS, COLORS
    PRINT_INDIVIDUAL_TILINGS = printIndividualTilings
    PRINT_FILTER_TEST = printFilterTest
    PRINT_PROGRESS = printProgress

def rgb(r,g,b):
    #Make it easy to use VS Code's built-in color picker to quickly change colors
    return([r,g,b])
#Always define COLORS, even outside setupOutputGlobals
COLORS = np.array([
    rgb(125, 125, 125),  # Color for the monominos
    rgb(224, 130, 7),
    rgb(48, 173, 10),
    rgb(9, 17, 173),
    rgb(173, 9, 159),
    rgb(217, 11, 11),
    rgb(21, 176, 155),
    rgb(28, 74, 33),
    rgb(172, 136, 191),
    rgb(69, 5, 23),
    rgb(255, 244, 28),
    rgb(7, 227, 209),
    rgb(13, 54, 4),
    #NOTE: will need to add more colors if want to graph tilings with more than 12 L tiles. Consider picking new colors randomly.
    ], dtype=int)

def addAllTilingsForNumLTiles(tilings_container, num_L_tiles, filter_file):
    """
        num_L_tiles: a number of L_tiles from 0 up to MAX_POSSIBLE_L_TILES
        adds all possible tilings and their sym_reps to tilings_container. 
        Writes filter test output to filter file if it isn't None.
    """
    #A combo is a sorted list of which L_tiles present
    #L_tile_combos is all such combos for the given total number of L_tiles
    L_tile_combos = it.combinations_with_replacement(L_TILES, num_L_tiles) 
    num_combos = int(math.factorial(len(L_TILES) + num_L_tiles - 1) / (math.factorial(num_L_tiles) * math.factorial(len(L_TILES) - 1)))
    index = 0
    for L_tile_combo in L_tile_combos:
        if(PRINT_PROGRESS):
            index += 1
            print(f"num_L_tiles: {str(num_L_tiles).rjust(3, ' ')} out of: {str(MAX_POSSIBLE_L_TILES).rjust(3, ' ')}")
            print(f"      combo: {str(index).rjust(3, ' ')} out of: {str(num_combos).rjust(3, ' ')}")
        filtered_L_tile_locations = getFilteredL_TileLocations(L_tile_combo, filter_file)
        loop_rec(0, getEmptyTiling(), filtered_L_tile_locations, 1, tilings_container, [])
        if(filter_file):
            print("Filtered Locations:", file = filter_file)
            printPotentialL_TileLocations(filtered_L_tile_locations, filter_file)
            print(file = filter_file)

def loop_rec(n, tiling, filtered_L_tile_locations, start_label, tilings_container, combo_accumulator):
    """
        Recursive helper function for above
    """
    for combo_type_n in filtered_L_tile_locations[n]:
        if(attemptToAddCombo(tiling, n, combo_type_n, start_label)):
            #adding combo succeeded
            combo_accumulator.append(tuple(tuple(i) for i in combo_type_n))
            if(n == (len(L_TILE_OFFSETS) - 1)): #on the last group of tiles
                tilings_container[0].append(copy.deepcopy(tiling))
                tilings_container[1].append(tuple(combo_accumulator))
            else:
                loop_rec(n + 1, tiling, filtered_L_tile_locations, start_label + len(combo_type_n), tilings_container, combo_accumulator)
            removeCombo(tiling, n, combo_type_n)
            combo_accumulator.pop()
        
def findRightMost(l, item):
    """
        l: a sorted iterable 
        Returns the index of the rightmost occurence of item in l, or -1 if item is not in l. Uses binary search.
    """
    index = b.bisect_right(l, item)
    return((index - 1) if ((index != 0) and l[index - 1] == item) else -1)

def getNumsOfEachL_tile(L_tile_combo):
    """
        Given a sorted L_tile combo (for example, [0, 0, 0, 2, 3, 3, 3]), return a length 4 array that says how many of each type of L_tile is in the combo. In this case, answer would be [3, 0, 1, 3]
        Edit: updated so that can handle any number of different tiles of any shapes, not just the 4 L_tiles. Specified entirely by L_TILE_OFFSETS.
    """
    nums_of_each_L_tile = np.zeros(len(L_TILE_OFFSETS), dtype=np.short)
    previous_index = -1
    for L_tile_type in L_TILES:
        potential_rightmost_occurence = findRightMost(L_tile_combo, L_tile_type)
        if(potential_rightmost_occurence == -1):
            #None of this type of L_tile in this combo
            nums_of_each_L_tile[L_tile_type] = 0
        else:
            #There is at least 1 of this type of L_tile in this combo
            nums_of_each_L_tile[L_tile_type] = potential_rightmost_occurence - previous_index
            previous_index = potential_rightmost_occurence
    return(nums_of_each_L_tile)

def getPotentialL_tileLocations(L_tile_combo, filter_file):
    """
        Given a combo of which L tiles are present, returns a list with 4 elements, where element i is a list corresponding to L_tile type i.
        The list contains tuples of coordinates, where each tuple is 1 possible combination of locations for element i. The empty tuple corresponds to no usage of L_tile i.
        A coordinate is a 1d array of [y x], where [0 0]  is top left.
        See potentialL_tileLocations.txt for example for a width 4 height 2 grid.
        potential_L_tile_locations - list of 4 lists, each corresponding to a L_tile type
        potential_L_tile_locations[i] - list of tuples for L_tile type i, where each tuple is a combination of coords for that L_tile type
        potential_L_tile_locations[i][j] - a tuple of coords, corresponding to a combo of locations for L_tile type i. (can be empty tuple if that tile is not used - empty combo)
        potential_L_tile_locations[i][j][k] - a coord in combo j for tile i 
    """
    nums_of_each_L_tile = getNumsOfEachL_tile(L_tile_combo)
    potential_L_tile_locations = []
    for L_tile_type in L_TILES:
        potential_L_tile_locations.append( 
            list(it.combinations(LOCATIONS, nums_of_each_L_tile[L_tile_type]) 
            ))
    if(filter_file):
        print(f"L_tile_combo: {L_tile_combo}", file = filter_file)
        print(f"nums_of_each_L_tile: {nums_of_each_L_tile}", file = filter_file)
        print(f"potential_L_tile_locations:", file = filter_file)
        printPotentialL_TileLocations(potential_L_tile_locations, filter_file)
        print(file = filter_file)
    return(potential_L_tile_locations)

def printPotentialL_TileLocations(potential_L_tile_locations, filter_file):
    """
        Pretty prints the potential_L_tile_locations. filter_file is an already open file object.
    """
    print("[", file = filter_file)
    for L_tile_type in L_TILES:
        #print the tuple of combos
        if(len(potential_L_tile_locations[L_tile_type]) == 1): #There's only the empty tuple; can print all on one line
            print(f"    {potential_L_tile_locations[L_tile_type]}", file = filter_file)
        else:
            print(f"    [\n", end="", file = filter_file)
            for combo in potential_L_tile_locations[L_tile_type]:
                print(f"        (", end="", file = filter_file)
                for coord in combo:
                    print(f"{coord},", end="", file = filter_file)
                print(f"),\n", end="", file = filter_file)
            print(f"    ]\n", file = filter_file)
    print("]", file = filter_file)

def onBoardAndEmpty(tiling, location):
    """
        returns True if the location (y,x) is within bounds of the tiling and unoccupied. Otherwise returns False.
    """
    if((location[0] < 0) or (location[0] >= HEIGHT)):
        return(False)
    if((location[1] < 0) or (location[1] >= WIDTH)):
        return(False)
    return(not(tiling[tuple(location)]))

def attemptToAddL_Tile(tiling, L_tile_type, location, label):
    """
        Given a tiling (a 2d np array of shorts, where a 0 represents a monomino and higher integers represent L tiles, where all the squares in the same L tile have the same integer), attempts to add the given L_tile_type by placing its upper left square at the given location coord. Modifies tiling (by putting the integer label in all 3 tiles of the L_tile) and returns True if possible, and returns False if not possible. If not possible, leaves tiling unchanged.
    """
    if(tiling[tuple(location)]):
        #encountered non-zero element here; this means there's already another L_tile here
        return(False)
    else:
        #There is not another L_tile at the top left coord. Checking offsets
        offsets = L_TILE_OFFSETS[L_tile_type]
        first_coord = np.add(location, offsets[0])
        second_coord = np.add(location, offsets[1])
        if(not(onBoardAndEmpty(tiling, first_coord))):
            return(False)
        if(not(onBoardAndEmpty(tiling, second_coord))):
            return(False)
        #both other coords are on board and empty; can place tile
        tiling[tuple(location)] = label
        tiling[tuple(first_coord)]  = label
        tiling[tuple(second_coord)] = label 
        return(True)

def removeL_Tile(tiling, L_tile_type, location):
    """
        Removes L_tile. NOTE: only use this on already placed valid L tiles.
    """
    offsets = L_TILE_OFFSETS[L_tile_type]
    first_coord = np.add(location, offsets[0])
    second_coord = np.add(location, offsets[1])
    tiling[tuple(location)] = 0
    tiling[tuple(first_coord)]  = 0
    tiling[tuple(second_coord)] = 0 

def getEmptyTiling():
    return(np.zeros([HEIGHT, WIDTH], dtype=np.short))

def attemptToAddCombo(tiling, L_tile_type, combo, start_label):
    """
        Given an L_tile combo (a tuple of coords from the potential_L_tile_locations) and a start_label which is the label of the lowest number tile, modifies tiling and returns whether it succeeded or not. If fails, leaves tiling in a consistent state.
    """
    didFail = False
    for (index, coord) in enumerate(combo):
        addSucceeded = attemptToAddL_Tile(tiling, L_tile_type, coord, start_label + index)
        if(not(addSucceeded)):
            #undo everything
            undoLimit = index
            didFail = True
            break
    if(didFail):
        for j in range(0, undoLimit):
            removeL_Tile(tiling, L_tile_type, combo[j])
    return(not(didFail)) 

def removeCombo(tiling, L_tile_type, combo):
    """
        NOTE: only use this on fully added valid combos
    """
    for location in combo:
        removeL_Tile(tiling, L_tile_type, location)

def getFilteredL_TileLocations(L_tile_combo, filter_file):
    """
        Given an L_tile_combo that says which L_tiles will be in use, get the potential l tile combo locations, but filtered of the internally inconsistent combos.
        If PRINT_FILTER_TEST is True, will print filter test outputs to a file called filter_test_{WIDTH}x{HEIGHT}.txt
    """
    # tup[0] is l_tile_type, and tup[1] is single_type_list_of_combos, which is potential_L_tile_locations[l_tile_type], which is a list of tuples, where each tuple is a combo
    
    potential_L_tile_locations = getPotentialL_tileLocations(L_tile_combo, filter_file)
    filtered_L_tile_locations = list(map(lambda tup: list(filter(lambda combo_tuple: attemptToAddCombo(getEmptyTiling(), tup[0], combo_tuple, 1), tup[1])), enumerate(potential_L_tile_locations)))
    return(filtered_L_tile_locations)

def getAllTilings(filter_file):
    """
        Setup: Globals need to be set up.
        Returns: tilings_container [[contains all tilings], [item is is tilings[i]'s symmetry representation]]
    """
    tilings_container = [[], []]
    for num_L_tiles in range(0, MAX_POSSIBLE_L_TILES + 1):
        addAllTilingsForNumLTiles(tilings_container, num_L_tiles, filter_file)
    return(tilings_container)

def lenLol(lol):
    return (functools.reduce(lambda length, lst: length + len(lst), lol, 0))

def printOutput(tilings_original_order, symmetry_representations, tilings_ordered_by_symmetry_lol, original_tiling_sym_indexes):
    """
        If PRINT_INDIVIDUAL_TILINGS is True, will print all tilings as well as how many there are, otherwise only prints number of tilings.
        Prints output to a file called tilings_{WIDTH}x{HEIGHT}.txt
    """
    if(not(PRINT_INDIVIDUAL_TILINGS)):
        return
    #TODO: print the symmetry representations, and then stop printing them.
    original_tilings_filename = os.path.join(FILE_PREFIX, f"tilings_{WIDTH}x{HEIGHT}_{len(tilings_original_order)}.txt")
    with open(original_tilings_filename, 'w') as f:
        for index, tiling in enumerate(tilings_original_order):
            print(f"{index + 1}:\n{tiling}", file = f)
            # print(f"{symmetry_representations[index]}", file = f)
            print(f"The above tiling is: " + (f"first in its symmetry group." if(original_tiling_sym_indexes[index] == -1) else f"symmetric to tiling {original_tiling_sym_indexes[index] + 1}."),  file = f, end="\n\n")
        print(f"For {WIDTH} x {HEIGHT} rectangles:", file = f)
        print(f"The number of tilings is: {len(tilings_original_order)}", file = f)

    symmetrically_unique_tilings_filename = os.path.join(FILE_PREFIX, f"sym_unique_{WIDTH}x{HEIGHT}_{len(tilings_ordered_by_symmetry_lol)}.txt")
    with open(symmetrically_unique_tilings_filename, 'w') as f:
        for index, sym_group in enumerate(tilings_ordered_by_symmetry_lol):
            print(f"{index + 1}:\n{sym_group[0]}\n", file = f)
        print(f"For {WIDTH} x {HEIGHT} rectangles:", file = f)
        print(f"The number of symmetrically unique tilings is: {len(tilings_ordered_by_symmetry_lol)}", file = f)

    tilings_ordered_by_symmetry_filename = os.path.join(FILE_PREFIX, f"sym_order_{WIDTH}x{HEIGHT}_{len(tilings_ordered_by_symmetry_lol)}.txt")
    with open(tilings_ordered_by_symmetry_filename, 'w') as f:
        index = 1
        for sym_group_num, sym_group in enumerate(tilings_ordered_by_symmetry_lol):
            print(f"Symmetry group: {sym_group_num + 1}", file = f)
            for tiling in sym_group:
                print(f"{index}:\n{tiling}\n", file = f)
                index += 1
            print("-" * 50, file = f)
        print(f"For {WIDTH} x {HEIGHT} rectangles:", file = f)
        print(f"The number of tilings is: {lenLol(tilings_ordered_by_symmetry_lol)}", file = f)

"""
    WARN: 
        The below code for symmetries does not actually work. Consider this: 
        33:
       [[2 2 0]
        [2 0 1]
        [0 1 1]]
        Above tiling taken from 3x3. That is the same as:
       [[1 1 0]
        [1 0 2]
        [0 2 2]]   
        rotated 180 degrees. But current code will not catch b/c 2 != 1.

    IDEA: 
        Have loop_rec make the tilings list a list of 2 things: 1st is the original tilings list, and second is a corresponding (tilings[0][i], which is original tilings corresponds to tilings[1][i]) list of lists (say, l) [[], [], [], []], where each second-level list corresponds to one of the 4 types of L tiles. l[i] will be a list of coordinates of the upper left corners of L tile type i, sorted by being nearest top, then leftmost (upper left is first, then upper right, etc) (so, 1 combo from the filtered_L_tile_locations). These are guaranteed to be exactly the same for the same tiling. Then, make a function that 'rotates/reflects' this representation, since you know that a transformation will transform one type of L tile into another and where its new upper left corner will be. Then, can compare those for symmetries.
    STEPS:
        0) Write a test case using known output that you know would fail using below method, and verify it fails: DONE

        1) Modify loop_rec to attach the needed information to make new_tilings = [original_tilings, new_info_list], and modify printing to print it out with the original tilings.: DONE

        2) Make a function that rotates this representation 90 degrees counterclockwise. DONE

        3) Make a function that reflects this representation vertically. DONE
        
        4) Test both functions as listed in test_symmetry.py.
        5) Modify below 2 symmetry functions to use this representation.
        6) testGetSymmetries.
        7) Change getTilingsFilteredBySymmetry to give all tilings ordered by symmetry as well as only symmetrically unique tilings, and configure printing/plotting for those. For testing purposes, print out text that says which of the original tilings are symmetrical to which earlier tiling.
        8) Stop printing the symmetry_representation in the tilings*.txt file once no longer needed for testing.
"""

def transformComputerCoords(num_times, coord, height, width, flip):
    """
        given a coords array in form [y,x], returns new coords which are these rotated 90 degrees counterclockwise num_times. In form [y,x]
        NOTE: only call with num_times from 1 to 3 inclusive
        flip is a boolean. If True, do a vertical flip (ignore num_times). If False, do a 90 degree ccw rotation num_times.
    """
    #given y,x of upper left square of an L tile of L_tile_type, calculate where the upper left square of the rotated result would be, given height and width
    #   With real coords, a 90 degree counter clockwise rotation centered at origin does this:
    # (x, y) -> (-y, x) -> (-x, -y) -> (y, -x) -> (x, y)
    # vertical flip is (x,y) -> (-x, y)

    # Imagine a shadow coordinate system centered at center of matrix. (In the computer, the coordinates of a cell in the array are the coordinates of the upper left corner)
    
    # computerX = shadowX + (width - 1)/2
    # computerY = -shadowY + (height - 1)/2
    # To rotate 90 degrees in computer coords:
    # computer coords: (computerX, computerY)
    #                 |
    #                 V
    # shadow coords:   (computerX - (width - 1)/2, -computerY + (height - 1)/2)
    #                |
    #                V
    # shadow coords transformed: (computerY - (height - 1)/2, computerX - (width - 1)/2)
    #                |
    #                V
    # computer coords transformed: (computerY - (height - 1)/2 + (width - 1)/2,
    #                                -computerX + (width - 1)/2 + (height - 1)/2)
    computerY, computerX = coord
    if(flip):
        transformed_computerX = -1*computerX + width - 1
        transformed_computerY = computerY
    else:
        if(num_times == 1):
            transformed_computerX = int(computerY - (height - 1)/2 + (width -1)/2)
            transformed_computerY = int(-1*computerX + (width - 1)/2 + (height - 1)/2)
        elif(num_times == 2):
            transformed_computerX = -1*computerX + (width - 1)
            transformed_computerY = -1*computerY + (height - 1)
        elif(num_times == 3):
            transformed_computerX = int(-1*computerY + (height - 1)/2 + (width - 1)/2)
            transformed_computerY = int(computerX - (width - 1)/2 + (height - 1)/2)
    return((transformed_computerY, transformed_computerX)) 

def insertTransformedL_TileComboIntoNewSymRep(L_tile_type, L_tile_location_combo, num_times, new_symmetry_representation, height, width, flip):
    new_top_left_locs = []
    if(flip):
        offset_indexes = (0, None, None, 1)
        offset_index = offset_indexes[L_tile_type]
    else:
        offset_indexes = ((0, None, 1, 1), (1, 1, 1, 0), (None, 0, 0, 0))
        offset_index = offset_indexes[num_times - 1][L_tile_type] 
    for L_tile_location in L_tile_location_combo:
        future_identifier_loc = L_tile_location if(offset_index is None) else (np.add(L_tile_location, L_TILE_OFFSETS[L_tile_type][offset_index]))
        new_top_left_loc = transformComputerCoords(num_times, future_identifier_loc, height, width, flip)
        new_top_left_locs.append(new_top_left_loc)

    new_top_left_locs.sort()
    if(flip):
        new_L_type = -1*L_tile_type + 3
    else:
        new_L_type = (L_tile_type - num_times) % 4
    new_symmetry_representation[new_L_type] = tuple(new_top_left_locs)

def transformSymRep(symmetry_representation, num_times, height, width, flip):
    #NOTE: returns a new sym rep; does not mutate old one
    #num_times corresponds to how many 90 degree counterclockwise turns
    #flip is a boolean. If true, flip. Otherwise, rotate ccw num_times.
    new_symmetry_representation = [(), (), (), ()]
    #NOTE: L_tile_location_combo is a tuple
    for (L_tile_type, L_tile_location_combo) in enumerate(symmetry_representation):
        insertTransformedL_TileComboIntoNewSymRep(L_tile_type, L_tile_location_combo, num_times, new_symmetry_representation, height, width, flip)
    return(tuple(new_symmetry_representation))

def getTilingsFilteredForSymmetry(tilings_container):
    original_tilings, symmetry_representations = tilings_container
    original_tiling_sym_indexes = np.empty(len(original_tilings), dtype=np.int32) #@ list[i] contains j means original_tilings[i] is symmetric to original_tilings[j], or is first of its sym_group if j = -1
    tilings_ordered_by_symmetry_lol = [] #a list of lists. Each list is a sym_group of tilings

    filtered_tiling_symmetry_representations = dict() #dict from sym_rep to a tuple: (index in original_tilings, index of the list in lol to append to)
    for original_tiling_index, symmetry_representation in enumerate(symmetry_representations):
        duplicate = False
        symmetry_reps_this_tiling = getSymmetries(symmetry_representation)
        for symmetry in symmetry_reps_this_tiling:
            index_tuple = filtered_tiling_symmetry_representations.get(symmetry, None)
            if(index_tuple):
                duplicate = True
                original_tiling_sym_indexes[original_tiling_index] = index_tuple[0]
                tilings_ordered_by_symmetry_lol[index_tuple[1]].append(original_tilings[original_tiling_index])
                break
        if(not(duplicate)):
            filtered_tiling_symmetry_representations[symmetry_representation] = (original_tiling_index, len(tilings_ordered_by_symmetry_lol))
            original_tiling_sym_indexes[original_tiling_index] = -1
            tilings_ordered_by_symmetry_lol.append([original_tilings[original_tiling_index]])
    return((tilings_ordered_by_symmetry_lol, original_tiling_sym_indexes))

def getSymmetries(symmetry_representation):

    #NOTE: Prove that there are 8 symmetries in a square:
    #      A symmetry leaves distances unchanged, so if vertices 1 and 2 are diagonal
    #      from each other before, they will be diagonal afterwards. Therefore, a 
    #      square has 8 symmetries, the ones below. 1 and 3 are diagonal, and so 
    #      are 2 and 4. The 1 3 can be in any of 4 orientations, and for each 1 3 
    #      orientation, 2 and 4 can be in two orientations.
    #      Same for rectangle, except ignore the 4 symmetries that turn rectangle
    #      sideways.
    """
        ccw0    ccw1    ccw2    ccw3
        12      23      34      41
        43      14      21      32

        14      43      32      21
        23      12      41      34
     ccw3,vf ccw2,vf  ccw1,vf   vf
    """

    symmetriesSet = set()
    if(HEIGHT == WIDTH):
        #square, 8 symmetries
        rot0 = symmetry_representation
        rot90 = transformSymRep(symmetry_representation, 1, HEIGHT, WIDTH, False)
        rot180 = transformSymRep(symmetry_representation, 2, HEIGHT, WIDTH, False)
        rot270 = transformSymRep(symmetry_representation, 3, HEIGHT, WIDTH, False)

        #reflect vertical means across vertical axis
        rot0_reflect_vertical = transformSymRep(symmetry_representation, None, HEIGHT, WIDTH, True)
        rot90_reflect_vertical = transformSymRep(rot90, None, HEIGHT, WIDTH, True)
        rot180_reflect_vertical = transformSymRep(rot180, None, HEIGHT, WIDTH, True)
        rot270_reflect_vertical = transformSymRep(rot270, None, HEIGHT, WIDTH, True)
        
        symmetriesSet.update([rot0, rot90, rot180, rot270, rot0_reflect_vertical, rot90_reflect_vertical, rot180_reflect_vertical, rot270_reflect_vertical])

    else:
        # rectangle, 4 symmetries
        rot0 = symmetry_representation
        rot180 = transformSymRep(symmetry_representation, 2, HEIGHT, WIDTH, False)

        #reflect vertical means across vertical axis
        rot0_reflect_vertical = transformSymRep(symmetry_representation, None, HEIGHT, WIDTH, True)
        rot180_reflect_vertical = transformSymRep(rot180, None, HEIGHT, WIDTH, True)
        
        symmetriesSet.update([rot0, rot180, rot0_reflect_vertical, rot180_reflect_vertical])

    return(symmetriesSet)
    
def insertRectangleInColors(coord, tiling, colors, height, width):
    for y in range(coord[0], coord[0] + height):
        for x in range(coord[1], coord[1] + width):
            colors[y, x] = COLORS[ tiling[(y-coord[0], x-coord[1])] ]

def get_sym_group_dimensions(symmetry_lol):
    tilings_per_sym_group = max(map(lambda l: len(l), symmetry_lol))
    num_sym_groups = len(symmetry_lol)
    # sym_groups_per_column = math.ceil(num_sym_groups ** .5)
    # sym_groups_per_row = math.ceil(num_sym_groups / sym_groups_per_column)
    
    GAP_BETWEEN_SYM_GROUPS = 2
    sym_group_width = tilings_per_sym_group * WIDTH 
    #Want the whole image to be as close to square as possible. 
    # Each sym group graphing is (sym_group_width * WIDTH + GAP_BETWEEN_SYM_GROUPS) / HEIGHT times wider than 
    # it is tall, so want the number of sg per column to be as close as possible to sym_groups_per_row * above
    # also, sg_row * sg_column must be >= total sg. Substitute those in to obtain below equation.
    sym_groups_per_row = max(1, round(((HEIGHT / (sym_group_width + GAP_BETWEEN_SYM_GROUPS)) * num_sym_groups) ** .5))
    sym_groups_per_column = math.ceil(num_sym_groups / sym_groups_per_row)
    return((sym_groups_per_column, sym_groups_per_row))


def computeSymmetrySquarePlotParams(symmetry_lol):
    tilings_per_sym_group = max(map(lambda l: len(l), symmetry_lol))
    num_sym_groups = len(symmetry_lol)
    
    sym_group_width = tilings_per_sym_group * WIDTH 

    (sym_groups_per_column, sym_groups_per_row) = get_sym_group_dimensions(symmetry_lol)

    PLOT_CELLS_WIDTH, PLOT_CELLS_HEIGHT = getPlotWidthHeight(symmetry_lol, True)
    colors = np.ones((PLOT_CELLS_HEIGHT, PLOT_CELLS_WIDTH, 3), dtype=int) * 255
    minor_x_ticks = []
    for sym_group_index, sym_group in enumerate(symmetry_lol):
        sym_groups_done_this_column = (sym_group_index % sym_groups_per_column)
        sym_group_upper_left_x = (sym_group_index // sym_groups_per_column) * (sym_group_width + GAP_BETWEEN_SYM_GROUPS)
        sym_group_upper_left_y = sym_groups_done_this_column * HEIGHT

        for x in range(sym_group_width):
            minor_x_ticks.append(x + sym_group_upper_left_x)
        for tiling_index, tiling in enumerate(sym_group):
            tiling_upper_left_x = tiling_index * WIDTH + sym_group_upper_left_x
            tiling_upper_left_y = sym_group_upper_left_y
            insertRectangleInColors((tiling_upper_left_y, tiling_upper_left_x), tiling, colors, HEIGHT, WIDTH)
    minor_x_ticks = np.array(minor_x_ticks) - .5
    if(PLOT_CELLS_HEIGHT <= 285):
        PLT_SIZE = 10
        lw_ratio = .25
    else:
        PLT_SIZE = 20
        lw_ratio = .5

    last_x_tick = -1 * WIDTH
    xticks = []
    for sg in range(sym_groups_per_row + 1):
        for t in range(tilings_per_sym_group + 1):
            xticks.append(last_x_tick + WIDTH)
            last_x_tick += WIDTH
        last_x_tick += (GAP_BETWEEN_SYM_GROUPS - WIDTH)
    yticks = np.linspace(0, PLOT_CELLS_HEIGHT, sym_groups_per_column + 1) - .5
    xticks = np.array(xticks) - .5
    mticker.Locator.MAXTICKS = PLOT_CELLS_WIDTH * PLOT_CELLS_HEIGHT * 2
    major_linewidth = (4 if (PLOT_CELLS_HEIGHT <= 92) else (1 if PLOT_CELLS_HEIGHT <= 285 else 1/6))
    minor_y_ticks = np.linspace(0, PLOT_CELLS_HEIGHT, PLOT_CELLS_HEIGHT + 1) - .5
    return((colors, PLT_SIZE, lw_ratio, xticks, yticks, major_linewidth, minor_x_ticks, minor_y_ticks))         

def computeSymmetryPlotParams(symmetry_lol):
    if(not(SYM_GROUPS_SINGLE_COLUMN)):
        #sym groups are in a square
        return(computeSymmetrySquarePlotParams(symmetry_lol))

    tilings_in_row = max(map(lambda l: len(l), symmetry_lol))
    tilings_in_column = len(symmetry_lol)

    # if(tilings_in) #start of sym_group_rect
    PLOT_CELLS_WIDTH, PLOT_CELLS_HEIGHT = getPlotWidthHeight(symmetry_lol, True)
    colors = np.ones((PLOT_CELLS_HEIGHT, PLOT_CELLS_WIDTH, 3), dtype=int) * 255
    for sym_index, sym_group in enumerate(symmetry_lol):
        for tiling_index, tiling in enumerate(sym_group):
            upper_left_x = tiling_index * WIDTH
            upper_left_y = sym_index * HEIGHT
            insertRectangleInColors([upper_left_y, upper_left_x], tiling, colors, HEIGHT, WIDTH)
    if(PLOT_CELLS_HEIGHT <= 285):
        PLT_SIZE = 10
        lw_ratio = .25
    else:
        PLT_SIZE = 20
        lw_ratio = .5
    yticks = np.linspace(0, PLOT_CELLS_HEIGHT, tilings_in_column + 1) - .5
    xticks = np.linspace(0, PLOT_CELLS_WIDTH, tilings_in_row + 1) - .5
    mticker.Locator.MAXTICKS = PLOT_CELLS_WIDTH * PLOT_CELLS_HEIGHT * 2
    major_linewidth = (4 if (PLOT_CELLS_HEIGHT <= 92) else (1 if PLOT_CELLS_HEIGHT <= 285 else 1/6))
    minor_x_ticks = np.linspace(0, PLOT_CELLS_WIDTH, PLOT_CELLS_WIDTH + 1) - .5
    minor_y_ticks = np.linspace(0, PLOT_CELLS_HEIGHT, PLOT_CELLS_HEIGHT + 1) - .5
    return((colors, PLT_SIZE, lw_ratio, xticks, yticks, major_linewidth, minor_x_ticks, minor_y_ticks))  

def computePlotParams(tilings):
    PLOT_CELLS_WIDTH, PLOT_CELLS_HEIGHT = getPlotWidthHeight(tilings, False)
    colors = np.ones((PLOT_CELLS_HEIGHT, PLOT_CELLS_WIDTH, 3), dtype=int) * 255
    tilings_in_column = len(colors) // (HEIGHT) 
    tilings_in_row = len(colors[0]) // (WIDTH)
    for index, tiling in enumerate(tilings):
        upper_left_x = (index % tilings_in_row) * (WIDTH) 
        upper_left_y = (index // tilings_in_row) * (HEIGHT)
        insertRectangleInColors([upper_left_y, upper_left_x], tiling, colors, HEIGHT, WIDTH)
    if(len(tilings) <= 5000):
        PLT_SIZE = 10
        lw_ratio = .25
    else:
        PLT_SIZE = 20
        lw_ratio = .5
    yticks = np.linspace(0, PLOT_CELLS_HEIGHT, tilings_in_column + 1) - .5
    xticks = np.linspace(0, PLOT_CELLS_WIDTH, tilings_in_row + 1) - .5
    mticker.Locator.MAXTICKS = PLOT_CELLS_WIDTH * PLOT_CELLS_HEIGHT * 2
    major_linewidth = (4 if (len(tilings) <= 500) else (1 if len(tilings) <= 5000 else 1/6))
    minor_x_ticks = np.linspace(0, PLOT_CELLS_WIDTH, PLOT_CELLS_WIDTH + 1) - .5
    minor_y_ticks = np.linspace(0, PLOT_CELLS_HEIGHT, PLOT_CELLS_HEIGHT + 1) - .5
    return((colors, PLT_SIZE, lw_ratio, xticks, yticks, major_linewidth, minor_x_ticks, minor_y_ticks))

def getPlotWidthHeight(tilings, plotting_sym_groups):
    if(plotting_sym_groups):
        if(SYM_GROUPS_SINGLE_COLUMN):
            tilings_in_row = max(map(lambda l: len(l), tilings))
            tilings_in_column = len(tilings)
            # if(tilings_in) #start of sym_group_rect
            PLOT_CELLS_WIDTH = WIDTH * tilings_in_row
            PLOT_CELLS_HEIGHT = tilings_in_column * HEIGHT
        else: 
            tilings_per_sym_group = max(map(lambda l: len(l), tilings))
            num_sym_groups = len(tilings)
            
            sym_group_width = tilings_per_sym_group * WIDTH 

            (sym_groups_per_column, sym_groups_per_row) = get_sym_group_dimensions(tilings)

            PLOT_CELLS_WIDTH =  (sym_groups_per_row * tilings_per_sym_group * WIDTH) + ((sym_groups_per_row - 1) * GAP_BETWEEN_SYM_GROUPS)
            PLOT_CELLS_HEIGHT = sym_groups_per_column * HEIGHT
    else:
        PLOT_CELLS_WIDTH = math.ceil(len(tilings) ** .5) * (WIDTH)
        PLOT_CELLS_HEIGHT = math.ceil(len(tilings) / math.ceil(len(tilings) ** .5)) * (HEIGHT) 
    return((PLOT_CELLS_WIDTH, PLOT_CELLS_HEIGHT))


def getMaxTilingsOrSymRowsPerPage(max_cell_length, plotting_sym_group, tilings):
    if(plotting_sym_group):
        if(SYM_GROUPS_SINGLE_COLUMN):
            return(math.floor(max_cell_length / HEIGHT))
        else:
            x = 8 * WIDTH + GAP_BETWEEN_SYM_GROUPS
            guess = (round((max_cell_length** 2) / (x * HEIGHT) ))
    else:
        guess = (min(math.floor(max_cell_length ** 2 / HEIGHT) , math.floor(max_cell_length ** 2 / WIDTH)))
    if(max(getPlotWidthHeight(tilings[:guess], plotting_sym_group)) > max_cell_length):
        while( (max(getPlotWidthHeight(tilings[:guess], plotting_sym_group)) > max_cell_length) and (guess > 1)):
            guess -= 1
        return(guess)
    else:
        while( (max(getPlotWidthHeight(tilings[:guess + 1], plotting_sym_group)) < max_cell_length) and (guess < len(tilings))):
            guess += 1
    return(guess)

def plotTilings(tilings, plot_name, plotting_sym_groups):
    max_tilings_or_sym_rows = getMaxTilingsOrSymRowsPerPage(MAX_CELL_LENGTH_PER_PAGE, plotting_sym_groups, tilings)
    if(max_tilings_or_sym_rows < len(tilings)):
        num_pages_needed = math.ceil(len(tilings) / max_tilings_or_sym_rows)
        for page in range(num_pages_needed):
            start_index = page * max_tilings_or_sym_rows
            end_index = (page + 1) *  max_tilings_or_sym_rows #non inclusive for range
            tilings_this_page = tilings[start_index: end_index]
            filename = f"{plot_name[0:-4]}_page_{page+1}_{start_index+ 1}_{start_index + len(tilings_this_page)}{plot_name[-4:]}"
            plotTilings(tilings_this_page, filename, plotting_sym_groups)
        return
    print(f"Creating '{plot_name}'. . .")
    (colors, PLT_SIZE, lw_ratio, xticks, yticks, major_linewidth, minor_x_ticks, minor_y_ticks) = computeSymmetryPlotParams(tilings) if (plotting_sym_groups) else computePlotParams(tilings)
    fig = plt.figure()
    fig.set_figwidth(PLT_SIZE)
    fig.set_figheight(PLT_SIZE)
    ax = fig.gca()
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.set_yticks(minor_y_ticks, minor=True)
    ax.set_xticks(minor_x_ticks, minor=True)
    ax.grid(which='minor', color=(0,0,0,.2), linewidth= major_linewidth * lw_ratio)

    ax.tick_params(which='both', width=0,length=0)
    ax.grid(which='major', color=(0,0,0,1), linewidth= major_linewidth) #Make the grid lines thinner if there are fewer tilings
    ax.axes.xaxis.set_ticklabels([])
    ax.axes.yaxis.set_ticklabels([])
    for _, spine in ax.spines.items():
        spine.set_visible(False)

    plt.imshow(colors, interpolation='nearest')
    plt.tight_layout()
    plt.savefig(plot_name, format = "png", dpi=800)
    print(f"Created '{plot_name}'.\n")

def plotAllTilings(tilings, tilings_ordered_by_symmetry_lol):
    plotTilings(tilings, os.path.join(FILE_PREFIX, f"tilings_{WIDTH}x{HEIGHT}_{len(tilings)}.png"), False)
    plotTilings(list(map(lambda l: l[0], tilings_ordered_by_symmetry_lol)), os.path.join(FILE_PREFIX, f"sym_unique_{WIDTH}x{HEIGHT}_{len(tilings_ordered_by_symmetry_lol)}.png"), False)

    plotTilings(tilings_ordered_by_symmetry_lol, os.path.join(FILE_PREFIX, f"sym_order_{WIDTH}x{HEIGHT}_{len(tilings_ordered_by_symmetry_lol)}.png"), True)

def pad_num_str(num, length):
    return(str(num).rjust(length, ' '))

def run_everything(WIDTH, HEIGHT, PRINT_INDIVIDUAL_TILINGS, PRINT_FILTER_TEST, PRINT_PROGRESS, SHOW_IMAGE):
    setupCalculationGlobals(givenWidth = WIDTH, givenHeight = HEIGHT)
    setupOutputGlobals(printIndividualTilings = PRINT_INDIVIDUAL_TILINGS, printFilterTest = PRINT_FILTER_TEST, printProgress = PRINT_PROGRESS)
    TILINGS_DIRECTORY = f"Tilings_{HEIGHT}_{WIDTH}"
    global FILE_PREFIX
    FILE_PREFIX = os.path.join(OUTPUT_DIRECTORY, TILINGS_DIRECTORY)

    if(PRINT_INDIVIDUAL_TILINGS or PRINT_FILTER_TEST or SHOW_IMAGE):
        if(not(os.path.exists(FILE_PREFIX))):
            os.makedirs(FILE_PREFIX)
    filter_file = open(os.path.join(FILE_PREFIX, f"filter_test_{WIDTH}x{HEIGHT}.txt"), 'w') if (PRINT_FILTER_TEST) else None
    tilings_container = getAllTilings(filter_file)
    (tilings_ordered_by_symmetry_lol, original_tiling_sym_indexes) = getTilingsFilteredForSymmetry(tilings_container)
    tilings_original_order, symmetry_representations = tilings_container

    printOutput(tilings_original_order, symmetry_representations, tilings_ordered_by_symmetry_lol, original_tiling_sym_indexes) 
    if(filter_file):
        filter_file.close()
    print(f"Completed calculations for {WIDTH} x {HEIGHT} grid.")
    total = len(tilings_original_order)
    sym_unique = len(tilings_ordered_by_symmetry_lol)
    pad_to = max(len(str(total)), len(str(sym_unique)))
    print(f"There are: {pad_num_str(total, pad_to)} tilings.")
    print(f"There are: {pad_num_str(sym_unique, pad_to)} symmetrically unique tilings.")
    if(SHOW_IMAGE):
        print("Creating images . . .\n")
        plotAllTilings(tilings_original_order, tilings_ordered_by_symmetry_lol)
        print("Finished creating images.")
    return((tilings_original_order, symmetry_representations)) #only used for pytest functions

def plotTest(num, testing_sym_column):
    #if(testing_sym_column), interpret num as num_sym_groups, otherwise, num_tilings
    tilings = np.random.random_integers(0, len(COLORS) - 1, size= (num, 8, HEIGHT, WIDTH) if(testing_sym_column) else (num, HEIGHT, WIDTH))
    insert = str(num) + "_column" if(testing_sym_column) else ""
    plotTilings(tilings, f"Random_{insert}.png", testing_sym_column)

if(__name__ == "__main__"):
    ###########################   CONFIGURATION    ############################
    WIDTH = 4
    HEIGHT = 4
    PRINT_INDIVIDUAL_TILINGS = True
    PRINT_FILTER_TEST = False          # Not recommended for large grids (> 5x5)
    PRINT_PROGRESS = True             # Recommended for large grids
    SHOW_IMAGE = True
    SYM_GROUPS_SINGLE_COLUMN = False 
    GAP_BETWEEN_SYM_GROUPS = 2
    MAX_CELL_LENGTH_PER_PAGE = 2600  # 2500 works (~250K 5x5 tilings in a square)
    OUTPUT_DIRECTORY = "Outputs"
    ###########################################################################
    run_everything(WIDTH, HEIGHT, PRINT_INDIVIDUAL_TILINGS, PRINT_FILTER_TEST, PRINT_PROGRESS, SHOW_IMAGE)
