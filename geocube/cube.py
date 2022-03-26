from geomath import Vector
from .sticker import Sticker


class Cube():

    def __init__(self, stickers=None):

        self.stickers = stickers or generate_solved_geo_cube()


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
