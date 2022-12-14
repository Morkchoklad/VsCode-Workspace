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

def parse_grid(grid, solveType):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s,d in grid_values(grid).items():
        if d in digits and not assign(values, s, d, solveType):
            return False ## (Fail if we can't assign d to square s.)
    return values

def grid_values(grid):
    """Convert grid into a dict of {square: char} with '0' or '.' for empties."""
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))

################ Constraint Propagation ################

def assign(values, s, d, solveType):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2, solveType) for d2 in other_values):
        return values
    else:
        return False

def eliminate(values, s, d, solveType):
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
        if not all(eliminate(values, s2, d2, solveType) for s2 in peers[s]):
            return False
    ## (Added) Naked pairs
    if solveType == 'n':
        if len(values[s]) == 2:
            pair = values[s]
            pair_values = list(pair)
            if pair_values[0] != pair_values[1]:
                for u in units[s]:
                    pair_peer = None
                    for peer in u:
                        if s != peer and len(values[peer]) == 2 and set(values[peer]) == set(pair):
                            pair_peer = peer
                            break
                    if pair_peer is not None:
                        if not all(eliminate(values, s2, pair_values[0], solveType) for s2 in u if s2 != s and s2 != pair_peer):
                            return False
                        if not all(eliminate(values, s2, pair_values[1], solveType) for s2 in u if s2 != s and s2 != pair_peer):
                            return False
    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d, solveType):
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

def solve(grid, solveType): return search(parse_grid(grid, solveType), solveType)

def search(values, solveType):
    """Using depth-first search and propagation, try all possible values."""
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!

    if solveType == 'r' :
        ## Choose random square and digit
        s = random.choice(squares)
        while not (len(values[s]) > 1):
            s = random.choice(squares)
        return some(search(assign(values.copy(), s, d, solveType), solveType)
                for d in shuffled(values[s]))

    ## Choose the unfilled square s with the fewest possibilities
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d, solveType), solveType)
                for d in values[s])


################ Hill Climbing ################
def fill(grid):
    """Fills the grid with values regardless of rows and column rules"""
    for i in range(18,27) :
        values = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
        for s in unitlist[i] :
            values.discard(grid[s])
        for s in unitlist[i] :
            if (grid[s] == '0') or (grid[s] == '.'):
                grid[s] = values.pop()
    return grid

def score(values):
    """Counts the number of cells in both rows and columns are in conflict"""
    score = 0
    for i in range(0,18) :
        digitsSeen = set()
        for s in unitlist[i]:
            digitsSeen.add(values[s])
        score += (9 - len(digitsSeen))
    return score

def hillClimbingSearch(initial):
    """Attempts to solve a sudoku puzzle using a hill-climbing algorithm"""
    maybeSol = fill(initial.copy())
    hasSwapped = True
    while hasSwapped :
        currentScore = score(maybeSol)
        hasSwapped = False
        for s1 in squares :
            if initial[s1] != '0' and (initial[s1] != '.'):
                for s2 in units[s1][2] :
                    if (initial[s2] != '0') and (initial[s2] != '.') and (s1 != s2):
                        trySwap = maybeSol.copy()
                        trySwap[s1] = maybeSol[s2]
                        trySwap[s2] = maybeSol[s1]
                        if score(trySwap) < currentScore:
                            maybeSol = trySwap.copy()
                            hasSwapped = True
    return maybeSol

def solveHC(grid):
    return hillClimbingSearch(grid_values(grid))


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
def solve_all(grids, solveType, name='', showif=0.0):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles.
    solveType determines the algorithm used to solve the puzzle :
    'r' means random (number 2 of the assignment)
    'h' means hill climbing (number 3)
    'n' means naked pair (number 4)
    any other entry calls for the default algorithm using the cell with the fewest options"""
    def time_solve(grid):
        start = time.time()
        if solveType == 'h' : values = solveHC(grid)
        else : values = solve(grid, solveType)
        t = time.time()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print ('(%.2f seconds)\n' % t)
        return (t, solved(values, solveType))
    times, results = zip(*[time_solve(grid) for grid in grids])
    N = len(grids)
    if N > 1:
        print ("Solved %d of %d %s puzzles (avg %.2f secs (%d Hz), max %.2f secs), total time : %.2f ." % (
            sum(results), N, name, sum(times)/N, N/sum(times), max(times), sum(times)))

def solved(values, solveType):
    """A puzzle is solved if each unit is a permutation of the digits 1 to 9 for the usual algorithm. For Hill climbing
    it is only solved when the score of the grid is equal to 0."""
    if solveType == 'h': return score(values) == 0
    def unitSolved(unit): return set(values[s] for s in unit) == set(digits)
    return values is not False and all(unitSolved(unit) for unit in unitlist)

def random_puzzle(N=60):
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
##    The second argument determines the heuristics/algorithm used :
##    'r' means random (number 2 of the assignment)
##    'h' means hill climbing (number 3)
##    'n' means naked pair (number 4)
##    any other entry calls for the default algorithm using the cell with the fewest options
    solve_all(from_file("100sudoku.txt"), 'r', None, None)
    solve_all(from_file("100sudoku.txt"), 'h', None, None)
    solve_all(from_file("100sudoku.txt"), 'n', None, None)
    solve_all(from_file("100sudoku.txt"), None, None, None)

## References used:
## http://www.scanraid.com/BasicStrategies.htm
## http://www.sudokudragon.com/sudokustrategy.htm
## http://www.krazydad.com/blog/2005/09/29/an-index-of-sudoku-strategies/
## http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/
