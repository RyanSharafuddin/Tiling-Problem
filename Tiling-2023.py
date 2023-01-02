"""
    According to https://www.numbersaplenty.com/2023, there are exactly 2023 ways to tile a 4x4 grid using only L tiles and monominos. It does not clarify if rotations or reflections count as different ways, or prove the statement. This Python program will attempt to verify it.
"""
import numpy as np
import itertools as it
import bisect as b

WIDTH = 4
HEIGHT = 2
TOTAL = WIDTH * HEIGHT
MAX_POSSIBLE_L_TILES = TOTAL // 3 # Note integer division here
L_TILES = np.array([0, 1, 2, 3]) #In order: TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT, TOP_LEFT

def addAllTilings(tilings_set, num_L_tiles):
    #A combo is a sorted list of which L_tiles present
    #L_tile_combos is all such combos for the given total number of L_tiles
    L_tile_combos = it.combinations_with_replacement(L_TILES, num_L_tiles) 
    for L_tile_combo in L_tile_combos:
        #TODO: 1st approach: choose locations for each group of L tiles and see if it works
        #TODO: 2nd approach: choose locations for each group intelligently so as not to overlap
        print(f"L_tile_combo: {L_tile_combo}")
        nums_of_each_L_tile = getNumsOfEachL_tile(L_tile_combo)
        print(f"nums_of_each_L_tile: {nums_of_each_L_tile}")
        potential_L_tile_locations = [] #a list of 4 lists, where each list contains the combo of locations for that L_tile type. A location is a number from 0 to TOTAL
        for L_tile_type in L_TILES:
            potential_L_tile_locations.append( list(it.combinations(range(TOTAL), nums_of_each_L_tile[L_tile_type])) )
        print(f"potential_L_tile_locations: {potential_L_tile_locations}")
        print()
        

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

if(__name__ == "__main__"):
    tilings_set = set() #considering rotated/reflected tilings to be different

    for num_L_tiles in range(0, MAX_POSSIBLE_L_TILES + 1):
        addAllTilings(tilings_set, num_L_tiles)

