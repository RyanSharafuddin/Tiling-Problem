"""
    According to https://www.numbersaplenty.com/2023, there are exactly 2023 ways to tile a 4x4 grid using only L tiles and monominos. It does not clarify if rotations or reflections count as different ways, or prove the statement. This Python program will attempt to verify it.
"""
import numpy as np
import itertools as it
import bisect as b

def setupGlobals(givenWidth, givenHeight):
    global WIDTH
    global HEIGHT
    global TOTAL
    global MAX_POSSIBLE_L_TILES
    global L_TILES
    global LOCATIONS
    global L_TILE_OFFSETS

    WIDTH = givenWidth
    HEIGHT = givenHeight
    TOTAL = WIDTH * HEIGHT
    MAX_POSSIBLE_L_TILES = TOTAL // 3 # Note integer division here
    L_TILES = np.array([0, 1, 2, 3]) #In order: TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT, TOP_LEFT
    #Locations is an ndarry of all the coordinates, where each coordinate is a 1d array in the form [y x], where [0 0] is top left
    LOCATIONS = []
    for h in range(HEIGHT):
        for w in range(WIDTH):
            LOCATIONS.append(np.array([h, w]))
    LOCATIONS = np.array(LOCATIONS)
    #offsets[i] are used calculate the other 2 tiles of an L tile of type i given the coord of its top left tile 
    L_TILE_OFFSETS = np.array(
            [
                [[0,1], [1,1]],
                [[1, -1], [1,0]], 
                [[1,0], [1,1]], 
                [[1,0], [0, 1]]
            ]
        )

def addAllTilings(tilings_set, num_L_tiles):
    #A combo is a sorted list of which L_tiles present
    #L_tile_combos is all such combos for the given total number of L_tiles
    L_tile_combos = it.combinations_with_replacement(L_TILES, num_L_tiles) 
    for L_tile_combo in L_tile_combos:
        #TODO: 1st approach: choose locations for each group of L tiles and see if it works
        #TODO: 2nd approach: choose locations for each group intelligently so as not to overlap
        potential_L_tile_locations = getPotentialL_tileLocations(L_tile_combo)
        
def findRightMost(l, item):
    """
        Given a sorted iterable l and an item, finds the index of the rightmost occurence of the item in l, or returns -1 if item is not in the list. Uses binary search. #TODO consider just counting the number of each L_tile if profiling shows this is taking too long.
    """
    index = b.bisect_right(l, item)
    return((index - 1) if ((index != 0) and l[index - 1] == item) else -1)

def getNumsOfEachL_tile(L_tile_combo):
    """
        Given a sorted L_tile combo (for example, [0, 0, 0, 2, 3, 3, 3]), return a length 4 array that says how many of each type of L_tile is in the combo. In this case, answer would be [3, 0, 1, 3]
    """
    nums_of_each_L_tile = np.zeros(4, dtype=np.short)
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

def getPotentialL_tileLocations(L_tile_combo):
    """
        Given a combo of which L tiles are present, returns a list with 4 elements, where element i is a list corresponding to L_tile type i.
        The list contains tuples of coordinates, where each tuple is 1 possible combination of locations for element i. The empty tuple corresponds to no usage of L_tile i.
        A coordinate is a 1d array of [y x], where [0 0]  is top left.
        See potentialL_tileLocations.txt for example for a width 4 height 2 grid.
        potential_L_tile_locations - list of 4 lists, each corresponding to a L_tile type
        potential_L_tile_locations[i] - list of tuples for L_tile type i, where each tuple is a combination of coords for that L_tile type
        potential_L_tile_locations[i][j] - a tuple of coords, corresponding to a combo of locations for L_tile type i.
        potential_L_tile_locations[i][j][k] - a coord in combo j for tile i (can be empty if that tile is not used)
    """
    print(f"L_tile_combo: {L_tile_combo}")
    nums_of_each_L_tile = getNumsOfEachL_tile(L_tile_combo)
    print(f"nums_of_each_L_tile: {nums_of_each_L_tile}")
    potential_L_tile_locations = []
    for L_tile_type in L_TILES:
        potential_L_tile_locations.append( 
            #NOTE: can wrap entire line below in np.array to change list into np.array to speed up; makes debugging printing uglier, but may speed up code
            list(it.combinations(LOCATIONS, nums_of_each_L_tile[L_tile_type]) 
            ))
    print(f"potential_L_tile_locations:")
    printPotentialL_TileLocations(potential_L_tile_locations)
    print()
    return(potential_L_tile_locations)

def printPotentialL_TileLocations(potential_L_tile_locations):
    """
        Pretty prints the potential_L_tile_locations
    """
    print("[")
    for L_tile_type in L_TILES:
        #print the tuple of combos
        if(len(potential_L_tile_locations[L_tile_type]) == 1): #There's only the empty tuple; can print all on one line
            print(f"    {potential_L_tile_locations[L_tile_type]}")
        else:
            print(f"    [", end="")
            for combo in potential_L_tile_locations[L_tile_type]:
                print(f"(", end="")
                for coord in combo:
                    print(f"{coord},", end="")
                print(f"), ", end="")
                # print(f"    {combo}")
            print(f"]")
    print("]\n")

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
        Given a tiling (a 2d np array of shorts, where a 0 represents a monomino and higher integers represent L tiles, where all the squares in the same L tile have the same integer), attempts to add the given L_tile_type by placing its upper left square at the given location coord. Modifies tiling (by putting the integer label in all 3 tiles of the L_tile) and returns True if possible, and returns False if not possible. This function assumes location is within bounds of the grid.
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

def testAttemptToAddL_Tile(tiling, L_tile_type, location, label):
    result = attemptToAddL_Tile(tiling, L_tile_type, location, label)
    print(f"Result: {result}")
    print(tiling)

def getEmptyTiling():
    return(np.zeros([HEIGHT, WIDTH], dtype=np.short))

if(__name__ == "__main__"):
    setupGlobals(givenWidth = 4, givenHeight = 2)
    tilings_set = set() #considering rotated/reflected tilings to be different

    for num_L_tiles in range(0, MAX_POSSIBLE_L_TILES + 1):
        addAllTilings(tilings_set, num_L_tiles)

