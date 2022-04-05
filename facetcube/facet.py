from .colors import facet_color
from manipulation import apply_geo_moves

SOLVED_CUBE = ["U"]*9 + ["R"]*9 + ["F"]*9 + ["D"]*9 + ["L"]*9 + ["B"]*9


def get_facelet(face, i):
    return "URFDLB".index(face) * 9 + (i-1)


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

        print()
        for i in canvas:
            print(''.join(i))
        print(f'{facet_color["F"]} ') # Reset terminal


def geo_cube_to_facet_cube(cube_stickers):
    str_cube = [' ']*54

    def fill_face(stickers, idx):
        stickers = sorted(stickers, key = lambda p: p.current.x)
        stickers = sorted(stickers, key = lambda p: p.current.z)

        for s in stickers:
            str_cube[idx] = s.get_target_face()
            idx += 1

    face_rotating_moves = ["", "y x", "x", "x2", "y' x", "y2 x"]

    for i, moves in enumerate(face_rotating_moves):
        tmp = apply_geo_moves(cube_stickers, moves)
        t = [i for i in tmp if i.get_current_face() == "U"]
        fill_face(t, i * 9)

    return FacetCube(str_cube)
