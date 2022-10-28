## Solve Every Sudoku Puzzle

## See http://norvig.com/sudoku.html

## Throughout this program we have:
##   r is a row,    e.g. 'A'
##   c is a column, e.g. '3'
##   s is a square, e.g. 'A3'
##   d is a digit,  e.g. '9'
##   u is a unit,   e.g. ['A1','B1','C1','D1','E1','F1','G1','H1','I1']
##   grid is a grid,e.g. 81 non-blank chars, e.g. starting with '.18...7...
##   values is a dict of possible values, e.g. {'A1':'12349', 'A2':'8', ...}
import random

def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return [a+b for a in A for b in B]

digits   = '123456789'
rows     = 'ABCDEFGHI'
cols     = digits
squares  = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))
             for s in squares)

################ Unit Tests ################

def test():
    """A set of tests that must pass."""
    assert len(squares) == 81
    assert len(unitlist) == 27
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 20 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
                           ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
                           ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
    assert peers['C2'] == set(['A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
                               'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                               'A1', 'A3', 'B1', 'B3'])
    print ('All tests pass.')

################ Parse a Grid ################

def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s,d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False ## (Fail if we can't assign d to square s.)
    return values

def grid_values(grid):
    """Convert grid into a dict of {square: char} with '0' or '.' for empties."""
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))

################ Constraint Propagation ################

def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False

def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if d not in values[s]:
        return values ## Already eliminated
    values[s] = values[s].replace(d,'')
    ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
        return False ## Contradiction: removed last value
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    ## (Added) Naked pairs
    elif len(values[s]) == 2:
        pair = values[s]
        pair_values = list(pair)
        if pair_values[0] != pair_values[1]:
            for u in units[s]:
                pair_peer = None
                for peer in u:
                    ## TODO SHOULD MAKE IT SO CONTENT OF VALUES SAME so '26' and '62' same
                    if s != peer and len(values[peer]) == 2 and values[peer] == pair:
                        pair_peer = peer
                        break
                if pair_peer is not None:
                    if not all(eliminate(values, s2, pair_values[0]) for s2 in u if s2 != s and s2 != pair_peer):
                        return False
                    if not all(eliminate(values, s2, pair_values[1]) for s2 in u if s2 != s and s2 != pair_peer):
                        return False
                    # for peer in u:
                    #     if s != peer and peer != pair_peer:
                    #         values[peer].replace(pair_values[0], '')
                    #         values[peer].replace(pair_values[1], '')
    ## TODO RUN LOCKED_CANDIDATES HERE???
    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values

################ Display as 2-D grid ################

def display(values):
    """Display these values as a 2-D grid."""
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print (''.join(values[r+c].center(width)+('|' if c in '36' else ''))
                      for c in cols)
        if r in 'CF': print (line)
    print

################ Search ################

def solve(grid): return search(parse_grid(grid))

def search(values):
    """Using depth-first search and propagation, try all possible values."""
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!
    ## Choose the unfilled square s with the fewest possibilities
    #n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    #return some(search(assign(values.copy(), s, d))
    #            for d in values[s])

    ## Choose random square and digit
    s = random.choice(squares)
    while not (len(values[s]) > 1):
        s = random.choice(squares)
    return some(search(assign(values.copy(), s, d))
                for d in shuffled(values[s]))

################ Naked Twins ######################



################ Locked Candidates ################

ROW = [cross(r, cols) for r in rows]
COL = [cross(rows, c) for c in cols]

def sum_col(list):
    col1,col2,col3 = sum_strings(list[0:9:3]), sum_strings(list[1:9:3]), sum_strings(list[2:9:3])
    columns = [col1,col2,col3]
    columns_dict = {col1:[0,3,6], col2:[1,4,7], col3: [2,5,8]}
    columns_non_null = [x for x in columns if x != 0]
    if len(columns_non_null) == 1 and columns_non_null[0] >= 2:
        return columns_dict[columns_non_null[0]]
    else:
        return None

def sum_row(list):
    row1,row2,row3 = sum_strings(list[0:3]), sum_strings(list[3:6]), sum_strings(list[6:9])
    rows = [row1,row2,row3]
    rows_dict = {row1:[0,1,2], row2:[3,4,5], row3: [6,7,8]}
    rows_non_null = [x for x in rows if x != 0]
    if len(rows_non_null) == 1 and rows_non_null[0] >= 2:
        return rows_dict[rows_non_null[0]]
    else:
        return None

def sum_strings(list):
    sum = 0
    for n in list:
        sum += int(n)
    return sum

def remove_from_list(string, d):
    new_list = list(string)
    if d in new_list:
        new_list.remove(d)
    return "".join(new_list)


# If a digit only appears on certain rows/cols of a box,
# eliminate from other rows/cols
def locked_candidates_1(values):
    # eventually we need to look at all units_list, for now we check boxes
    boxes = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
    chosen_box = None
    for box in boxes:
        chosen_box = box
        temp_digits = '123456789'
        # presuppose correct boxes digits and no duplicates
        for square in chosen_box:
            if len(values[square]) == 1:
                temp_digits = temp_digits.replace(values[square], '')
        for digit in list(temp_digits):
            digit_present = list('000000000')
            for i,square in enumerate(chosen_box):
                if len(values[square]) > 1 and digit in values[square]:
                    digit_present[i] = '1'
            locked_col = sum_col(digit_present)
            locked_row = sum_row(digit_present)
            if locked_col is not None:
                chosen_col = []
                real_col = []
                rest_col = []
                for index in locked_col:
                    chosen_col.append(chosen_box[index])
                for c in COL:
                    if chosen_col[0] in c:
                        real_col = c
                        break
                rest_col = [x for x in real_col if x not in chosen_col]
                for key in rest_col:
                    values[key] = remove_from_list(values[key], digit)
            if locked_row is not None:
                chosen_row = []
                real_row = []
                rest_row = []
                for index in locked_row:
                    chosen_row.append(chosen_box[index])
                for r in ROW:
                    if chosen_row[0] in r:
                        real_row = r
                        break
                rest_row = [x for x in real_row if x not in chosen_row]
                for key in rest_row:
                    values[key] = remove_from_list(values[key], digit)
    return values


def test_locked_candidates_1():
    """
    Let's suppose this configuration
    . . . |9 . . |4 3 . 
    . . 2 |6 . . |9 . . 
    . 9 . |. . 3 |. . 7
    ------+------+------
    Since candidate 2's right right box only appears in bottom row,
    we can discard cells in that row outside that box from having 2's.
    """
    temp_values = {
        'A1':'16','A2':'1578','A3':'157','A4':'9','A5':'12578','A6':'1258','A7':'4','A8':'3','A9':'1568',
        'B1':'134','B2':'134578','B3':'2','B4':'6','B5':'14578','B6':'158','B7':'9','B8':'58','B9':'158',
        'C1':'146','C2':'9','C3':'145','C4':'245','C5':'12458','C6':'3','C7':'268','C8':'2568','C9':'7'
    }

    end_values = {
        'A1':'16','A2':'1578','A3':'157','A4':'9','A5':'12578','A6':'1258','A7':'4','A8':'3','A9':'1568',
        'B1':'134','B2':'134578','B3':'2','B4':'6','B5':'14578','B6':'158','B7':'9','B8':'58','B9':'158',
        'C1':'146','C2':'9','C3':'145','C4':'45','C5':'1458','C6':'3','C7':'268','C8':'2568','C9':'7'
    }
    return locked_candidates_1(temp_values) == end_values

print(test_locked_candidates_1())

################ Utilities ################

def some(seq):
    """Return some element of seq that is true."""
    for e in seq:
        if e: return e
    return False

def from_file(filename, sep='\n'):
    """Parse a file into a list of strings, separated by sep."""
    return open(filename).read().strip().split(sep)

def shuffled(seq):
    """Return a randomly shuffled copy of the input sequence."""
    seq = list(seq)
    random.shuffle(seq)
    return seq

################ System test ################

import time, random

def solve_all(grids, name='', showif=0.0):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""
    def time_solve(grid):
        start = time.time()
        values = solve(grid)
        t = time.time()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print ('(%.2f seconds)\n' % t)
        return (t, solved(values))
    times, results = zip(*[time_solve(grid) for grid in grids])
    N = len(grids)
    if N > 1:
        print ("Solved %d of %d %s puzzles (avg %.2f secs (%d Hz), max %.2f secs), total time : %.2f ." % (
            sum(results), N, name, sum(times)/N, N/sum(times), max(times), sum(times)))

def solved(values):
    """A puzzle is solved if each unit is a permutation of the digits 1 to 9."""
    def unitSolved(unit): return set(values[s] for s in unit) == set(digits)
    return values is not False and all(unitSolved(unit) for unit in unitlist)

def random_puzzle(N=6):
    """Make a random puzzle with N or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s])==1 else '.' for s in squares)
    return random_puzzle(N) ## Give up and make a new puzzle

grid1  = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
grid2  = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
hard1  = '.....6....59.....82....8....45........3........6..3.54...325..6..................'
    
if __name__ == '__main__':
    test()
##    solve_all(from_file("easy50.txt", '========'), "easy", None)
    solve_all(from_file("top95.txt"), "hard", None)
    solve_all(from_file("1000sudoku.txt"), "hardest", None)
    solve_all([random_puzzle() for _ in range(99)], "random", 100.0)

## References used:
## http://www.scanraid.com/BasicStrategies.htm
## http://www.sudokudragon.com/sudokustrategy.htm
## http://www.krazydad.com/blog/2005/09/29/an-index-of-sudoku-strategies/
## http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/