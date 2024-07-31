from ces_object import CESObject


class OverallResponseRate(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)

    _shared_columns = {
        "Project": {"id": "projectId"},
        }
