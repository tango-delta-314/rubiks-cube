from colors import facet_color


SOLVED_CUBE = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"


class FacetCube():
    '''
    Represents the cube as a string of facets.
    '''

    def __init__(self, cube=SOLVED_CUBE):
        self.cube = cube

    def print_cube(self):

        CANVAS_WIDTH = 12   # [L, F, R, B] * 3
        CANVAS_HEIGHT = 9   # [U, F, D] * 3

        # Initialize the character canvas
        canvas = []
        for i in range(0,9):
            row = []
            for j in range(0,12):
                row.append('  ')
            canvas.append(row)

        def draw(idx, r, c):
            for i in range(r, r+3):
                for j in range(c, c+3):
                    fill = self.cube[idx]
                    idx += 1
                    canvas[i][j] = f'{facet_color[fill]}{fill} '

        draw( 0, 0, 3)
        draw( 9, 3, 6)
        draw(18, 3, 3)
        draw(27, 6, 3)
        draw(36, 3, 0)
        draw(45, 3, 9)

        for i in canvas:
            print(''.join(i))
