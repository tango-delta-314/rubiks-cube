class Sticker():

    def __init__(self, current, target=None):
        self.current = current
        self.target = target or current

    def get_current_face(self):
        return Sticker._get_face(self.current)

    def get_target_face(self):
        return Sticker._get_face(self.target)

    @staticmethod
    def _get_face(vector):
        if vector.x == 3:
            return "R"
        elif vector.x == -3:
            return "L"
        elif vector.y == 3:
            return "U"
        elif vector.y == -3:
            return "D"
        elif vector.z == 3:
            return "F"
        elif vector.z == -3:
            return "B"

    def __eq__(self, obj):
        return (self.target == obj.target) and (self.current == obj.current)

    def __hash__(self):
        return hash((self.target, self.current))
