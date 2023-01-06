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

    def test_2023_4x4(self):
        WIDTH = 4
        HEIGHT = 4
        PRINT_INDIVIDUAL_TILINGS = False
        PRINT_FILTER_TEST = False          # Not recommended for large grids (> 5x5)
        PRINT_PROGRESS = False              # Recommended for large grids
        SHOW_IMAGE = False                  # Not recommended for large grids (> 5x5)
        tilings, _ = run_everything(WIDTH, HEIGHT, PRINT_INDIVIDUAL_TILINGS, PRINT_FILTER_TEST, PRINT_PROGRESS, SHOW_IMAGE)
        assert(len(tilings) == 2023)

    def test_195_4x3(self):
        WIDTH = 4
        HEIGHT = 3
        PRINT_INDIVIDUAL_TILINGS = False
        PRINT_FILTER_TEST = False          # Not recommended for large grids (> 5x5)
        PRINT_PROGRESS = False              # Recommended for large grids
        SHOW_IMAGE = False                  # Not recommended for large grids (> 5x5)
        tilings, _ = run_everything(WIDTH, HEIGHT, PRINT_INDIVIDUAL_TILINGS, PRINT_FILTER_TEST, PRINT_PROGRESS, SHOW_IMAGE)
        assert(len(tilings) == 195)


    def test_transform_sym_rep(self):
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
        sym_rep_2017 = symmetry_representations[2017]

        sym_rep_2016 = symmetry_representations[2016]

        sym_rep_2015 = symmetry_representations[2015]

        sym_rep_2010 = symmetry_representations[2010]

        assert(transformSymRep(sym_rep_2017, 1, HEIGHT, WIDTH, False) == sym_rep_2016)

        assert(transformSymRep(sym_rep_2017, 2, HEIGHT, WIDTH, False) == sym_rep_2015)

        assert(transformSymRep(sym_rep_2017, 3, HEIGHT, WIDTH, False) == sym_rep_2010)

        direct_thrice = transformSymRep(sym_rep_2017, 3, HEIGHT, WIDTH, False)

        indirect_thrice = transformSymRep(transformSymRep(transformSymRep(sym_rep_2017, 1, HEIGHT, WIDTH, False), 1, HEIGHT, WIDTH, False), 1, HEIGHT, WIDTH, False)

        assert(indirect_thrice == direct_thrice)

        assert(transformSymRep(sym_rep_2017, None, HEIGHT, WIDTH, True) == sym_rep_2010) # vertical reflection

        assert(transformSymRep(transformSymRep(symmetry_representations[1296], None, HEIGHT, WIDTH, True), None, HEIGHT, WIDTH, True) == symmetry_representations[1296])

        """
        75:
       [[0 0 0 2]
        [1 1 2 2]
        [0 1 0 0]
        [0 0 0 0]]

        (((1, 0),), ((0, 3),), (), ())

        149:
       [[1 1 0 0]
        [0 1 0 0]
        [0 2 2 0]
        [0 2 0 0]]

        (((0, 0),), (), (), ((2, 1),))
        """
        assert(transformSymRep(symmetry_representations[74], 1, HEIGHT, WIDTH, False) == symmetry_representations[148])
    
    def testReflect3x3(self):
        WIDTH = 3
        HEIGHT = 3
        PRINT_INDIVIDUAL_TILINGS = False
        PRINT_FILTER_TEST = False          # Not recommended for large grids (> 5x5)
        PRINT_PROGRESS = False              # Recommended for large grids
        SHOW_IMAGE = False                  # Not recommended for large grids (> 5x5)
        _, symmetry_representations = run_everything(WIDTH, HEIGHT, PRINT_INDIVIDUAL_TILINGS, PRINT_FILTER_TEST, PRINT_PROGRESS, SHOW_IMAGE)

        sym_rep_a = symmetry_representations[21]
        sym_rep_b = symmetry_representations[30]
        """
       [[2 1 1]
        [2 2 1]
        [0 0 0]]

       [[2 2 1]
        [2 1 1]
        [0 0 0]]
        """
        assert(transformSymRep(sym_rep_a, None, HEIGHT, WIDTH, True) == sym_rep_b)

    def test_transformRectangle(self):
        raise(Exception("Unimplemented"))
        WIDTH = 5
        HEIGHT = 4
        PRINT_INDIVIDUAL_TILINGS = True
        PRINT_FILTER_TEST = False          # Not recommended for large grids (> 5x5)
        PRINT_PROGRESS = False              # Recommended for large grids
        SHOW_IMAGE = True                  # Not recommended for large grids (> 5x5)
        tilings, symmetry_representations = run_everything(WIDTH, HEIGHT, PRINT_INDIVIDUAL_TILINGS, PRINT_FILTER_TEST, PRINT_PROGRESS, SHOW_IMAGE)


    def testGetSymmetries(self):
        #TODO: test that the getSymmetries function returns 1 thing for empty tiling, 4 things for corner tiling, and expected 8 things as in above
        raise Exception("Test Unimplemented")

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
        """
        The two tilings above are these. They 
           [[2 1 1]
            [2 2 1]
            [0 0 0]]

           [[2 2 1]
            [2 1 1]
            [0 0 0]]
        """

        symmetric_tilings_container = [[tiling_a, tiling_b], [sym_rep_a, sym_rep_b]]
        two_empties = [tilings[0], copy.deepcopy(tilings[0])]
        sym_rep_empty = symmetry_representations[0]
        two_empties_tilings_container = [two_empties, [sym_rep_empty, sym_rep_empty]]

        filtered_empties = getTilingsFilteredForSymmetry(two_empties_tilings_container)
        filtered_symmetries = getTilingsFilteredForSymmetry(symmetric_tilings_container)

        assert(len(filtered_empties) == 1)
        assert(len(filtered_symmetries) == 1) #Expected to fail until real symmetry filtering implemented


