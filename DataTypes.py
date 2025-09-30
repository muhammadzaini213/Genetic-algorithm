class Student:
    def __init__(self, name, courses):
        self.name = name
        self.courses = courses

    def __repr__(self):
        return f"Student({self.name})"

class Course:
    def __init__(self, name, teachers, num_classes=1):
        self.name = name
        self.teachers = teachers if isinstance(teachers, list) else [teachers]  # Support both single teacher and list
        self.num_classes = num_classes

class CourseClass:
    def __init__(self, course, section, teacher=None):
        self.course = course
        self.section = section  # "A", "B", "C"
        self.teacher = teacher  # Specific teacher assigned to this section
        self.students = []

    def __repr__(self):
        return f"{self.course.name}-{self.section} ({self.teacher})"

class Room:
    def __init__(self, name, capacity, available_times):
        self.name = name
        self.capacity = capacity
        self.available_times = set(available_times)

    def __repr__(self):
        return f"Room({self.name}, cap={self.capacity})"

class Timeslot:
    def __init__(self, slot_id, day, time):
        self.id = slot_id
        self.day = day
        self.time = time

    def __repr__(self):
        return f"{self.day} {self.time}"


