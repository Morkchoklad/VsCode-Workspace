# If a digit only appears on certain rows/cols of a box,
# eliminate from other rows/cols
def locked_candidates_1(values):
    # eventually we need to look at all units_list, for now we check boxes
    boxes = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')][0:3]
    chosen_box = None
    for i,box in enumerate(boxes):
        # if s in box:
        chosen_box = box
        temp_digits = '123456789'
        # presuppose correct boxes digits and no duplicates
        for squarex in chosen_box:
            if len(values[squarex]) == 1:
                temp_digits = remove_from_list(temp_digits,values[squarex])
        for digit in list(temp_digits):
            digit_present = list('000000000')
            for j,square in enumerate(chosen_box):
                if len(values[square]) > 1 and digit in values[square]:
                    digit_present[j] = '1'
            # locked_col = sum_col(digit_present)
            locked_row = sum_row(digit_present)
            # if locked_col is not None:
            #     # remove that digit row/col in other boxes
            #     for index in locked_col:
            #         if index != chosen_box_i:
            #             box = boxes[index]
            #             for box_i in locked_col:
            #                 values[box[box_i]] = remove_from_list(values[box[box_i]], digit)
            if locked_row is not None:
                chosen_row = []
                real_row = []
                rest_row = []
                for index in locked_row:
                    chosen_row.append(chosen_box[index])
                for r in ROW:
                    if chosen_row[0] in r:
                        real_row = r
                rest_row = [x for x in real_row if x not in chosen_row]
                # print(rest_row)
                # print(locked_row, chosen_box_i, digit,square)
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
    return locked_candidates_1(temp_values)

print(test_locked_candidates_1())

t1 = [1,2,3]
t2 = [1,2,3,4,5,6]
# print(t1 == intersection(t1,t2))

# print([cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')][0:3])


# print([cross(rows, c) for c in cols]) # colonnes
            # [cross(r, cols) for r in rows])