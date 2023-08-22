from pces.ces_object import CESObject


class NodeMapper(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)
