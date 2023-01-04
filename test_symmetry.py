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

def test_symmetry():
    #NOTE: setup globals in globals.py
    assert(WIDTH == 3)
    assert(HEIGHT == 3)
    tilings = run_everything()

    tiling_a = tilings[21]
    tiling_b = tilings[30]

    print("About to print tilings:")
    print(tiling_a, tiling_b, sep="\n\n", end="\n")

    symmetric_tilings = [tiling_a, tiling_b]
    two_empties = [getEmptyTiling(), getEmptyTiling()]

    filtered_empties = getTilingsFilteredForSymmetry(two_empties)
    filtered_symmetries = getTilingsFilteredForSymmetry(symmetric_tilings)

    assert(len(filtered_empties) == 1)
    assert(len(filtered_symmetries) == 1) #Expected to fail until real symmetry filtering implemented
