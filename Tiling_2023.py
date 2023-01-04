"""
    According to https://www.numbersaplenty.com/2023, there are exactly 2023 ways to tile a 4x4 grid using only L tiles and monominos. It does not clarify if rotations or reflections count as different ways, or prove the statement. This Python program will attempt to verify it.
"""
# Note: Profile by doing 'python -m cProfile -s tottime Tiling_2023.py'
import numpy as np, itertools as it, bisect as b, copy, math, matplotlib.pyplot as plt, matplotlib.ticker as mticker
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

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
        loop_rec(0, getEmptyTiling(), filtered_L_tile_locations, 1, tilings, [])
        if(filter_file):
            print("Filtered Locations:", file = filter_file)
            printPotentialL_TileLocations(filtered_L_tile_locations, filter_file)
            print(file = filter_file)

def loop_rec(n, tiling, filtered_L_tile_locations, start_label, tilings, combo_accumulator):
    """
        Recursive helper function for above
    """
    for combo_type_n in filtered_L_tile_locations[n]:
        if(attemptToAddCombo(tiling, n, combo_type_n, start_label)):
            #adding combo succeeded
            combo_accumulator.append(tuple(tuple(i) for i in combo_type_n))
            if(n == (len(L_TILE_OFFSETS) - 1)): #on the last group of tiles
                tilings[0].append(copy.deepcopy(tiling))
                tilings[1].append(tuple(combo_accumulator))
            else:
                loop_rec(n + 1, tiling, filtered_L_tile_locations, start_label + len(combo_type_n), tilings, combo_accumulator)
            removeCombo(tiling, n, combo_type_n)
            combo_accumulator.pop()
        
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
    tilings = [[], []]
    for num_L_tiles in range(0, MAX_POSSIBLE_L_TILES + 1):
        addAllTilingsForNumLTiles(tilings, num_L_tiles, filter_file)
    return(tilings)

def printOutput(tilings):
    #TODO: print the symmetry representations, and then stop printing them.
    (tilings, symmetry_representation) = tilings
    """
        If PRINT_INDIVIDUAL_TILINGS is True, will print all tilings as well as how many there are, otherwise only prints number of tilings.
        Prints output to a file called tilings_{WIDTH}x{HEIGHT}.txt
    """
    tilings_filename = f"tilings_{WIDTH}x{HEIGHT}_{len(tilings)}.txt"
    with open(tilings_filename, 'w') as f:
        if(PRINT_INDIVIDUAL_TILINGS): 
            for index, tiling in enumerate(tilings):
                print(f"{index + 1}:\n{tiling}\n", file = f)
                print(f"{symmetry_representation[index]}\n", file = f)
        print(f"For {WIDTH} x {HEIGHT} rectangles:", file = f)
        print(f"The number of tilings is: {len(tilings)}", file = f)

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

        2) Make a function that rotates this representation 90 degrees counterclockwise.
            CURRENT PROGRESS: on the rotates function, only handles some cases so far: Test it on tilings with multiple tiles of different types.
        3) Make a function that reflects this representation horizontally.
        4) Modify below 2 symmetry functions to use this representation.
        5) Print out the filtered tilings (perhaps with a note about which of the original tilings were eliminated and which they were symmetric to)
"""

def rotateComputerCoordsCCW(num_times, coord, height, width):
    """
        given a coords array in form [y,x], returns new coords which are these rotated 90 degrees counterclockwise num_times. In form [y,x]
    """
    #given y,x of upper left square of an L tile of L_tile_type, calculate where the upper left square of the rotated result would be, given height and width
    #   With real coords, a 90 degree counter clockwise rotation centered at origin does this:
    # (x, y) -> (-y, x) -> (-x, -y) -> (y, -x) -> (x, y)

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
    if(num_times != 1):
        raise Exception("Unimplemented") #TODO
    computerY, computerX = coord
    transformed_computerX = int(computerY - (height - 1)/2 + (width -1)/2)
    transformed_computerY = int(-1*computerX + (width - 1)/2 + (height - 1)/2)
    return((transformed_computerY, transformed_computerX)) 

def insertComboIntoNewSymmetryRepFor90DegRot(L_tile_type, L_tile_location_combo, num_times, new_symmetry_representation, height, width):
    #WARN: this function only handles 90 degree ccw rotations as of now. Change and then change name
    # TODO: test that this works on tilings with multiple different kinds of tiles and at least 2 of the same kind
    if(num_times != 1):
        raise Exception("Unimplemented")
    new_top_left_locs = []
    offset_indexes = (0, None, 1, 1) #WARN be careful when rotating multiple times
    for L_tile_location in L_tile_location_combo:
        offset_index = offset_indexes[L_tile_type] #WARN be careful when rotating multiple times
        future_identifier_loc = L_tile_location if(offset_index is None) else (np.add(L_tile_location, L_TILE_OFFSETS[L_tile_type][offset_index]))
        # if(L_tile_type == 0): #top right corner
        #     future_identifer_loc = np.add(L_tile_location, L_TILE_OFFSETS[0][0]) # the current location of the square in the corner, the top right, which for type 0 L tiles, will be top left corner after 90 degree counter clockwise rotation
        # elif(L_tile_type == 1): #bottom right
        #     future_identifer_loc = L_tile_location # bottom rights become top left. Top left square becomes new top left square
        # else:
        new_top_left_loc = rotateComputerCoordsCCW(1, future_identifier_loc, height, width)
        new_top_left_locs.append(new_top_left_loc)

    new_top_left_locs.sort() #TODO test that this sort actually works
    for i in range(0, 4): #TODO change once implement rotating multiple times, since this is only valid for rotating once
        if(L_tile_type == i):
            new_symmetry_representation[(i - 1) % 4] = tuple(new_top_left_locs) #since L_TILE_OFFSETS are listed in rotating clockwise order
    # if(L_tile_type == 0): #top right corner
    #     new_symmetry_representation[3] = tuple(new_top_left_locs) #top right becomes bottom left with one rotation ccw
    # elif(L_tile_type == 1):
    #     new_symmetry_representation[0] = tuple(new_top_left_locs)


def rotSymRepCounterclockwise(symmetry_representation, num_times, height, width):
    #NOTE: returns a new sym rep; does not mutate old one
    #num_times corresponds to how many 90 degree counterclockwise turns
    new_symmetry_representation = [(), (), (), ()]
    #NOTE: L_tile_location_combo is a tuple
    for (L_tile_type, L_tile_location_combo) in enumerate(symmetry_representation):
        insertComboIntoNewSymmetryRepFor90DegRot(L_tile_type, L_tile_location_combo, num_times, new_symmetry_representation, height, width)
    return(tuple(new_symmetry_representation))
        # An L tile of type 0 (top right corner) becomes a type 3 L tile (top left). 
        # The square at its first offset (the corner square, offset [0,1] from top left), becomes its new top left.

def getTilingsFilteredForSymmetry(tilings_container):
    # print(f"tilings_container: \n{tilings_container}")
    filtered_tilings = []
    filtered_tiling_symmetry_representations = set()
    for index, symmetry_representation in enumerate(tilings_container[1]):
        # print(f"IN GET TILINGS FILTERED\nTiling:\n{tilings_container[0][index]}\nsym_rep\n{symmetry_representation}")
        # symmetry_representation = tuple(symmetry_representation)
        duplicate = False
        symmetry_reps_this_tiling = getSymmetries(symmetry_representation)
        for symmetry in symmetry_reps_this_tiling:
            if(symmetry in filtered_tiling_symmetry_representations):
                duplicate = True #TODO: print that this tiling is a duplicate, and maybe add some info to set to display which previous tiling it's a duplicate of
                break
        if(not(duplicate)):
            filtered_tiling_symmetry_representations.add(symmetry_representation)
            filtered_tilings.append(tilings_container[0][index])
    return(filtered_tilings)

# def tuplify(sym_rep):
#     new_sym_rep = ((tuple), (), (), ())

def getSymmetries(symmetry_representation):
    #NOTE: need to change to work with other representation in plan
    symmetriesSet = set()
    if(HEIGHT == WIDTH):
        #square, 8 symmetries
        rot0 = symmetry_representation
    #     #np.rot90 rotates counterclockwise
        # rot90 = np.rot90(tiling, 1)
        rot90 = rotSymRepCounterclockwise(symmetry_representation, 1, HEIGHT, WIDTH)
    #     rot180 = np.rot90(tiling, 2)
    #     rot270 = np.rot90(tiling, 3)

    #     #reflect horizontal means across horizontal axis
    #     rot0_reflect_horizontal = np.flip(rot0, 0)
    #     rot90_reflect_horizontal = np.flip(rot90, 0)
    #     rot180_reflect_horizontal = np.flip(rot180, 0)
    #     rot270_reflect_horizontal = np.flip(rot270, 0)
        
    #     symmetries_list = [rot0, rot90, rot180, rot270, rot0_reflect_horizontal, rot90_reflect_horizontal, rot180_reflect_horizontal, rot270_reflect_horizontal]
    symmetriesSet.update([rot0, rot90])

    # else:
    #     #rectangle, 4 symmetries
    #     rot0 = tiling
    #     rot180 = np.rot90(tiling, 2)

    #     reflect_horizontal = np.flip(rot0, 0)
    #     reflect_vertical = np.flip(rot0, 1)
        
    #     symmetries_list = [rot0, rot180, reflect_horizontal, reflect_vertical]

    # # print("Printing symmetries in symmetries list: ")
    # # for symmetry in symmetries_list:
    # #     print(symmetry, end="\n\n")
    
    # symmetries_tuple_list = map(tilingToTup, symmetries_list)
    # for symmetry_tuple in symmetries_tuple_list:
    #     symmetriesSet.add(symmetry_tuple)

    # # print("Printing symmetries in symmetries set: ")
    # # for symmetry in symmetriesSet:
    # #     print(np.array(symmetry), end="\n\n")

    return(symmetriesSet)

def tilingToTup(tiling):
    return(tuple(map(tuple, tiling)))
    
def plotTiling(coord, tiling, colors):
    for y in range(coord[0], coord[0] + HEIGHT):
        for x in range(coord[1], coord[1] + WIDTH):
            colors[y, x] = COLORS[ tiling[(y-coord[0], x-coord[1])] ]

def plotAllTilings(tilings):
    global COLORS

    COLORS = np.array([
        [125, 125, 125], #7d7d7d  # Color for the monominos
        [224, 130, 7],   #e08207
        [48, 173, 10],   #30ad0a   
        [9, 17, 173],    #0911ad
        [173, 9, 159],   #ad099f
        [217, 11, 11],   #d90b0b
        [21, 176, 155],  #15b09b
        [28, 74, 33],    #1c4a21
        [172, 136, 191], #ac88bf
        [69, 5, 23],     #450517
        [255, 244, 28],  #fff41c
        [7, 227, 209],   #07e3d1
        [13, 54, 4]      #0d3604
        #NOTE: will need to add more colors if want to graph tilings with more than 12 L tiles. Consider picking new colors randomly.
        ], dtype=int)

    PLOT_CELLS_WIDTH = math.ceil(len(tilings) ** .5) * (WIDTH)
    PLOT_CELLS_HEIGHT = math.ceil(len(tilings) / math.ceil(len(tilings) ** .5)) * (HEIGHT) 
    colors = np.ones((PLOT_CELLS_HEIGHT, PLOT_CELLS_WIDTH, 3), dtype=int) * 255

    tilings_in_column = len(colors) // (HEIGHT) 
    tilings_in_row = len(colors[0]) // (WIDTH)

    for index, tiling in enumerate(tilings):
        upper_left_x = (index % tilings_in_row) * (WIDTH) 
        upper_left_y = (index // tilings_in_row) * (HEIGHT)
        plotTiling([upper_left_y, upper_left_x], tiling, colors)
    
    if(len(tilings) <= 5000):
        PLT_SIZE = 10
        lw_ratio = .25
    else:
        PLT_SIZE = 20
        lw_ratio = .5

    fig = plt.figure()
    fig.set_figwidth(PLT_SIZE)
    fig.set_figheight(PLT_SIZE)

    ax = fig.gca()
    yticks = np.linspace(0, PLOT_CELLS_HEIGHT, tilings_in_column + 1) - .5
    xticks = np.linspace(0, PLOT_CELLS_WIDTH, tilings_in_row + 1) - .5
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)

    mticker.Locator.MAXTICKS = PLOT_CELLS_WIDTH * PLOT_CELLS_HEIGHT * 2
    major_linewidth = (4 if (len(tilings) <= 500) else (1 if len(tilings) <= 5000 else 1/6))

    ax.xaxis.set_minor_locator(AutoMinorLocator(WIDTH))
    ax.yaxis.set_minor_locator(AutoMinorLocator(HEIGHT))
    ax.grid(which='minor', color=(0,0,0,.2), linewidth= major_linewidth * lw_ratio)

    ax.tick_params(which='both', width=0,length=0)
    ax.grid(which='major', color=(0,0,0,1), linewidth= major_linewidth) #Make the grid lines thinner if there are fewer tilings
    ax.axes.xaxis.set_ticklabels([])
    ax.axes.yaxis.set_ticklabels([])
    for _, spine in ax.spines.items():
        spine.set_visible(False)

    plt.imshow(colors, interpolation='nearest')
    plt.tight_layout()
    # plt.title(f"{len(tilings)} Tilings of a {WIDTH} x {HEIGHT} Grid" ) #cut off
    plt.savefig(f"tilings_{WIDTH}x{HEIGHT}_{len(tilings)}.png", format = "png", dpi=800)

def run_everything():
    setupCalculationGlobals(givenWidth = WIDTH, givenHeight = HEIGHT)
    setupOutputGlobals(printIndividualTilings = PRINT_INDIVIDUAL_TILINGS, printFilterTest = PRINT_FILTER_TEST, printProgress = PRINT_PROGRESS)
    if(PRINT_FILTER_TEST):
        filter_filename = f"filter_test_{WIDTH}x{HEIGHT}.txt"
        filter_file = open(filter_filename, 'w')
    else:
        filter_file = None
    tilings, symmetry_representations = getAllTilings(filter_file) #considering rotated/reflected tilings to be different
    printOutput((tilings, symmetry_representations)) #TODO: once no longer need to print symmetry representation, only pass in tilings to this function.
    if(filter_file):
        filter_file.close()
    print(f"Completed calculations for {WIDTH} x {HEIGHT} grid.")
    print(f"There are: {len(tilings)} tilings.")
    if(SHOW_IMAGE):
        print("Creating image . . .")
        plotAllTilings(tilings)
        print("Finished creating image.")
    return((tilings, symmetry_representations)) #only used for pytest functions

def plotTest(num_tilings):
    tilings = np.random.random_integers(0, 7, size=(num_tilings, HEIGHT, WIDTH))
    plotAllTilings(tilings)

if(__name__ == "__main__"):
    ###########################   CONFIGURATION    ############################
    WIDTH = 4
    HEIGHT = 4
    PRINT_INDIVIDUAL_TILINGS = True
    PRINT_FILTER_TEST = False          # Not recommended for large grids (> 5x5)
    PRINT_PROGRESS = False              # Recommended for large grids
    SHOW_IMAGE = True                  # Not recommended for large grids (> 5x5)
    ###########################################################################
    run_everything()
else:
    # This is being imported into the test file
    from globals import *