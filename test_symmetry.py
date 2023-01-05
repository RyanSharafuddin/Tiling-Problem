"""
    NOTE: 
        When using pytest, test file names must be in form test_*.py or *_test.py, and unit test functions must start with test_. See https://docs.pytest.org/en/latest/getting-started.html#get-started
        Run by just doing pytest -rP in command line.
        The -rP flag tells it to pretty print captured stdout with each test case even in passing cases.
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

class TestSymmetry:

    def test_rotate_sym_rep(self):
        #TODO: fill in with expected values from a tiling that contains all 4 types of L tiles and at least 2 of 1 type and try all 8 symmetries on it. And see that the list remains sorted. Ditto for a rectangle with all 4 symmetries.
        WIDTH = 4
        HEIGHT = 4
        PRINT_INDIVIDUAL_TILINGS = False
        PRINT_FILTER_TEST = False          # Not recommended for large grids (> 5x5)
        PRINT_PROGRESS = False              # Recommended for large grids
        SHOW_IMAGE = False                  # Not recommended for large grids (> 5x5)
        tilings, symmetry_representations = run_everything(WIDTH, HEIGHT, PRINT_INDIVIDUAL_TILINGS, PRINT_FILTER_TEST, PRINT_PROGRESS, SHOW_IMAGE)
        """
            2018: (2017 0 indexed). Has all 4 tilings and 2 of type 3
           [[4 4 1 1]
            [4 5 5 1]
            [3 5 0 2]
            [3 3 2 2]]

            (((0, 2),), ((2, 3),), ((2, 0),), ((0, 0), (1, 1)))

            Visual inspection of image file shows that when rotated once, it turns into:

            2017: (2016 0 indexed)
           [[5 5 1 1]
            [5 3 0 1]
            [4 3 3 2]
            [4 4 2 2]]

            (((0, 2),), ((2, 3),), ((1, 1), (2, 0)), ((0, 0),))

            Rotated twice:

            2016: (2015 0 indexed)
           [[5 5 1 1]
            [5 0 2 1]
            [4 2 2 3]
            [4 4 3 3]]

            (((0, 2),), ((1, 2), (2, 3)), ((2, 0),), ((0, 0),))

            thrice

            2011: (2010 0 indexed)
            [[5 5 1 1]
            [5 2 2 1]
            [4 0 2 3]
            [4 4 3 3]]

            (((0, 2), (1, 1)), ((2, 3),), ((2, 0),), ((0, 0),))

            this takes care of testing list sorting.
        """
        tiling_2017, sym_rep_2017 = tilings[2017], symmetry_representations[2017]

        tiling_2016, sym_rep_2016 = tilings[2016], symmetry_representations[2016]

        tiling_2015, sym_rep_2015 = tilings[2015], symmetry_representations[2015]

        tiling_2010, sym_rep_2010 = tilings[2010], symmetry_representations[2010]

        assert(rotSymRepCounterclockwise(sym_rep_2017, 1, HEIGHT, WIDTH) == sym_rep_2016)

        twice_rotated = rotSymRepCounterclockwise(sym_rep_2017, 2, HEIGHT, WIDTH)
        assert(twice_rotated == sym_rep_2015)

        assert(rotSymRepCounterclockwise(sym_rep_2017, 3, HEIGHT, WIDTH) == sym_rep_2010)

        direct_thrice = rotSymRepCounterclockwise(sym_rep_2017, 3, HEIGHT, WIDTH)

        indirect_thrice = rotSymRepCounterclockwise(rotSymRepCounterclockwise(rotSymRepCounterclockwise(sym_rep_2017, 1, HEIGHT, WIDTH), 1, HEIGHT, WIDTH), 1, HEIGHT, WIDTH)

        assert(indirect_thrice == direct_thrice)


        #TODO: also test a rotation with 2 L tiles, one CCW equivalence between the sym reps, then test that calling rotSymRepCounterclockwise with num_times = 1 3 times is same as calling it once with num_times = 3. 
    
    def test_reflect_sym_rep(self):
        raise Exception("Unimplemented")

    def testGetSymmetries(self):
        #TODO: test that the getSymmetries function returns 1 thing for empty tiling, 4 things for corner tiling, and expected 8 things as in above
        raise Exception("Unimplemented")

    #Fails because not all symmetries are implemented yet
    def test_symmetry(self):
        WIDTH = 3
        HEIGHT = 3
        PRINT_INDIVIDUAL_TILINGS = False
        PRINT_FILTER_TEST = False          # Not recommended for large grids (> 5x5)
        PRINT_PROGRESS = False              # Recommended for large grids
        SHOW_IMAGE = False                  # Not recommended for large grids (> 5x5)
        tilings, symmetry_representations = run_everything(WIDTH, HEIGHT, PRINT_INDIVIDUAL_TILINGS, PRINT_FILTER_TEST, PRINT_PROGRESS, SHOW_IMAGE)

        tiling_a = tilings[21]
        tiling_b = tilings[30]

        sym_rep_a = symmetry_representations[21]
        sym_rep_b = symmetry_representations[30]

        print("About to print 2 different but tilings:")
        print(tiling_a, tiling_b, sep="\n\n", end="\n")

        symmetric_tilings_container = [[tiling_a, tiling_b], [sym_rep_a, sym_rep_b]]
        two_empties = [tilings[0], copy.deepcopy(tilings[0])]
        sym_rep_empty = symmetry_representations[0]
        two_empties_tilings_container = [two_empties, [sym_rep_empty, copy.deepcopy(sym_rep_empty)]]

        filtered_empties = getTilingsFilteredForSymmetry(two_empties_tilings_container)
        filtered_symmetries = getTilingsFilteredForSymmetry(symmetric_tilings_container)

        assert(len(filtered_empties) == 1)
        assert(len(filtered_symmetries) == 1) #Expected to fail until real symmetry filtering implemented


