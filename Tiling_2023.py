"""
    According to https://www.numbersaplenty.com/2023, there are exactly 2023 ways to tile a 4x4 grid using only L tiles and monominos. It does not clarify if rotations or reflections count as different ways, or prove the statement. This Python program will attempt to verify it.
"""
# Note: Profile by doing 'python -m cProfile -s tottime Tiling_2023.py'
import numpy as np, itertools as it, bisect as b, copy, math

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
    global PRINT_INDIVIDUAL_TILINGS, PRINT_FILTER_TEST, PRINT_PROGRESS
    PRINT_INDIVIDUAL_TILINGS = printIndividualTilings
    PRINT_FILTER_TEST = printFilterTest
    PRINT_PROGRESS = printProgress

def addAllTilingsForNumLTiles(tilings, num_L_tiles, filter_file):
    """
        Given tilings (a list of each possible tiling) and a number of L_tiles from 0 up to MAX_POSSIBLE_L_TILES, adds all possible tilings (considering rotations and reflections to be different) to tilings. Writes filter test output to filter file if it isn't None.
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
        loop_rec(0, getEmptyTiling(), filtered_L_tile_locations, 1, tilings)
        if(filter_file):
            print("Filtered Locations:", file = filter_file)
            printPotentialL_TileLocations(filtered_L_tile_locations, filter_file)
            print(file = filter_file)

def loop_rec(n, tiling, filtered_L_tile_locations, start_label, tilings):
    """
        Recursive helper function for above
    """
    for combo_type_n in filtered_L_tile_locations[n]:
        if(attemptToAddCombo(tiling, n, combo_type_n, start_label)):
            #adding combo succeeded
            if(n == (len(L_TILE_OFFSETS) - 1)): #on the last group of tiles
                tilings.append(copy.deepcopy(tiling))
            else:
                loop_rec(n + 1, tiling, filtered_L_tile_locations, start_label + len(combo_type_n), tilings)
            removeCombo(tiling, n, combo_type_n)
        
def findRightMost(l, item):
    """
        Given a sorted iterable l and an item, finds the index of the rightmost occurence of the item in l, or returns -1 if item is not in the list. Uses binary search. #TODO consider just counting the number of each L_tile if profiling shows this is taking too long.
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
        Given a tiling and a coord, returns True if the coord is both within bounds of the tiling and unoccupied. Otherwise returns False.
    """
    if((location[0] < 0) or (location[0] >= HEIGHT)):
        return(False)
    if((location[1] < 0) or (location[1] >= WIDTH)):
        return(False)
    return(not(tiling[tuple(location)]))

def attemptToAddL_Tile(tiling, L_tile_type, location, label):
    """
        Given a tiling (a 2d np array of shorts, where a 0 represents a monomino and higher integers represent L tiles, where all the squares in the same L tile have the same integer), attempts to add the given L_tile_type by placing its upper left square at the given location coord. Modifies tiling (by putting the integer label in all 3 tiles of the L_tile) and returns True if possible, and returns False if not possible. If not possible, leaves tiling unchanged. This function assumes location is within bounds of the grid.
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
        return(False)
    #did not fail
    return(True)

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
        Once globals have been setup, returns a list of all possible tilings, (considers rotations/reflections to be different)
    """
    tilings = []
    for num_L_tiles in range(0, MAX_POSSIBLE_L_TILES + 1):
        addAllTilingsForNumLTiles(tilings, num_L_tiles, filter_file)
    return(tilings)

def printOutput(tilings):
    """
        If PRINT_INDIVIDUAL_TILINGS is True, will print all tilings as well as how many there are, otherwise only prints number of tilings.
        Prints output to a file called tilings_{WIDTH}x{HEIGHT}.txt
    """
    tilings_filename = f"tilings_{WIDTH}x{HEIGHT}.txt"
    with open(tilings_filename, 'w') as f:
        if(PRINT_INDIVIDUAL_TILINGS): 
            for index, tiling in enumerate(tilings):
                print(f"{index + 1}:\n{tiling}\n", file = f)
        print(f"For {WIDTH} x {HEIGHT} rectangles:", file = f)
        print(f"The number of tilings is: {len(tilings)}", file = f) 

if(__name__ == "__main__"):
    ###########################   CONFIGURATION    ###########################
    WIDTH = 5
    HEIGHT = 4
    PRINT_INDIVIDUAL_TILINGS = True
    PRINT_FILTER_TEST = False          # Not recommended for large grids (> 5x5)
    PRINT_PROGRESS = False              # Recommended for large grids
    ###########################################################################
    setupCalculationGlobals(givenWidth = WIDTH, givenHeight = HEIGHT)
    setupOutputGlobals(printIndividualTilings = PRINT_INDIVIDUAL_TILINGS, printFilterTest = PRINT_FILTER_TEST, printProgress = PRINT_PROGRESS)
    if(PRINT_FILTER_TEST):
        filter_filename = f"filter_test_{WIDTH}x{HEIGHT}.txt"
        filter_file = open(filter_filename, 'w')
    else:
        filter_file = None
    tilings= getAllTilings(filter_file) #considering rotated/reflected tilings to be different
    printOutput(tilings)
    if(filter_file):
        filter_file.close()
    print(f"Completed calculations for {WIDTH} x {HEIGHT} grid.")

