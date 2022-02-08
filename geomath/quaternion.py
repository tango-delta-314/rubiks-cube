import math

class Quaternion():

    def __init__(self, x=0, y=0, z=0, w=1):

        self._x = x
        self._y = y
        self._z = z
        self._w = w

    def set_from_axis_angle(self, axis, angle):

        a = angle / 2
        s = math.sin(a)

        self._x = axis.x * s
        self._y = axis.y * s
        self._z = axis.z * s
        self._w = math.cos(a)

        return self

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self, value):
        self._w = value
