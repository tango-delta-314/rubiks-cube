import math
from .quaternion import Quaternion

class Vector():

    def __init__(self, x=0, y=0, z=0):

        self._x = x
        self._y = y
        self._z = z

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

    def round(self):

        self._x = round(self._x)
        self._y = round(self._y)
        self._z = round(self._z)

        return self

    def apply_axis_angle(self, axis, angle, degrees=False):

        a = angle
        if degrees:
            a = angle / 180 * math.pi

        q = Quaternion()
        q.set_from_axis_angle(axis, a)
        return self.apply_quaternion(q)

    def apply_quaternion(self, q):

        x = self._x
        y = self._y
        z = self._z

        qx = q.x
        qy = q.y
        qz = q.z
        qw = q.w

        ix = (qw * x) + (qy * z) - (qz * y)
        iy = (qw * y) + (qz * x) - (qx * z)
        iz = (qw * z) + (qx * y) - (qy * x)
        iw = - (qx * x) - (qy * y) - (qz * z)

        self._x = (ix * qw) + (iw * - qx) + (iy * - qz) - (iz * - qy)
        self._y = (iy * qw) + (iw * - qy) + (iz * - qx) - (ix * - qz)
        self._z = (iz * qw) + (iw * - qz) + (ix * - qy) - (iy * - qx)

        return self

    def __eq__(self, obj):
        return self._x == obj.x and self._y == obj.y and self._z == obj.z

    def __hash__(self):
        return hash((self._x, self._y, self._z))
