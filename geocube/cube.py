from facetcube import FacetCube
from geomath import Vector
from manipulation import apply_geo_moves
from .sticker import Sticker


class Cube():

    def __init__(self, stickers=None):

        self.stickers = stickers or generate_solved_geo_cube()

    def to_facet_cube(self):
        str_cube = [' ']*54

        def fill_face(stickers, idx):
            stickers = sorted(stickers, key = lambda p: p.current.x)
            stickers = sorted(stickers, key = lambda p: p.current.z)

            for s in stickers:
                str_cube[idx] = s.get_target_face()
                idx += 1

        face_rotating_moves = ["", "y x", "x", "x2", "y' x", "y2 x"]

        for i, moves in enumerate(face_rotating_moves):
            tmp = apply_geo_moves(self.stickers, moves)
            t = [i for i in tmp if i.get_current_face() == "U"]
            fill_face(t, i * 9)

        return FacetCube(str_cube)


def generate_solved_geo_cube():
    stickers = []

    for face in [3, -3]:
        for c1 in [-2, 0, 2]:
            for c2 in [-2, 0, 2]:
                stickers.extend((
                    Sticker(Vector(face, c1, c2)),
                    Sticker(Vector(c1, face, c2)),
                    Sticker(Vector(c1, c2, face))
                ))

    return stickers
