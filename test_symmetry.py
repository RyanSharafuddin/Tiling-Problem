"""
    NOTE: 
        When using pytest, test file names must be in form test_*.py or *_test.py, and unit test functions must start with test_. See https://docs.pytest.org/en/latest/getting-started.html#get-started
        Run by just doing pytest -s in command line.
        The -s flag tells it not to capture stdout
    NOTE:
    22 (1 indexed, so tilings[21]) on the 3x3 is this:
    22:
       [[2 1 1]
        [2 2 1]
        [0 0 0]]
    31 (1 indexed, so tilings[30]) is this:
    31:
       [[2 2 1]
        [2 1 1]
        [0 0 0]]
    31 therefore is 22 reflected across vertical line (equivalent to rotate180 and reflect horizontal). Because 2s and 1s though, naiive symmetry check would not catch this. Therefore, use it for your test case.
"""
from Tiling_2023 import *
from globals import *

#Fails because rotate function not implemented yet
# def test_symmetry():
#     #NOTE: setup globals in globals.py
#     assert(WIDTH == 3)
#     assert(HEIGHT == 3)
#     tilings, symmetry_representations = run_everything()

#     tiling_a = tilings[21]
#     tiling_b = tilings[30]

#     sym_rep_a = symmetry_representations[21]
#     sym_rep_b = symmetry_representations[30]

#     print("About to print tilings:")
#     print(tiling_a, tiling_b, sep="\n\n", end="\n")

#     symmetric_tilings_container = [[tiling_a, tiling_b], [sym_rep_a, sym_rep_b]]
#     two_empties = [tilings[0], copy.deepcopy(tilings[0])]
#     sym_rep_empty = symmetry_representations[0]
#     two_empties_tilings_container = [two_empties, [sym_rep_empty, copy.deepcopy(sym_rep_empty)]]

#     # filtered_empties = getTilingsFilteredForSymmetry(two_empties_tilings_container)
#     filtered_symmetries = getTilingsFilteredForSymmetry(symmetric_tilings_container)

#     # assert(len(filtered_empties) == 1)
#     assert(len(filtered_symmetries) == 1) #Expected to fail until real symmetry filtering implemented

def test_rotate_sym_rep():
    tilings, symmetry_representations = run_everything()
    tiling, sym_rep = tilings[2], symmetry_representations[2]
    print(f"tiling:\n {tiling}\n")
    print(f"corresponding sym_rep:\n {sym_rep}")

    print(f"rotated 90 degrees ccw: \n{np.rot90(tiling, 1)}\n")
    print(f"rotate its sym_rep: \n{rotSymRepCounterclockwise(sym_rep, 1, 3, 3)}")
