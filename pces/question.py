from ces_object import CESObject


class Question(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)
