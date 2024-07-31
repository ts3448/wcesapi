from ces_object import CESObject


class ResponseRate(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)
