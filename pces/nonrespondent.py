from ces_object import CESObject


class NonRespondent(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)
