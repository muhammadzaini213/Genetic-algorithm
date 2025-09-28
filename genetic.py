import random

# =========================
# Data Structures
# =========================
class Course:
    def __init__(self, name, teacher, num_classes=1):
        self.name = name
        self.teacher = teacher
        self.num_classes = num_classes

class CourseClass:
    def __init__(self, course, section):
        self.course = course
        self.section = section  # "A", "B", "C"
        self.students = []

    def __repr__(self):
        return f"{self.course.name}-{self.section}"

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

class Student:
    def __init__(self, name, courses):
        self.name = name
        self.courses = courses

    def __repr__(self):
        return f"Student({self.name})"

# =========================
# Schedule Representation
# =========================
class Schedule:
    def __init__(self, course_classes, rooms, timeslots):
        self.course_classes = course_classes
        self.rooms = rooms
        self.timeslots = timeslots
        # assignments: CourseClass -> (Room, Timeslot)
        self.assignments = {}

    def randomize(self):
        for cclass in self.course_classes:
            valid_pairs = [(room, ts) for room in self.rooms for ts in self.timeslots if ts.id in room.available_times]
            self.assignments[cclass] = random.choice(valid_pairs)

    def fitness(self, students):
        penalty = 0

        # Maps for checking conflicts
        room_usage = {}
        teacher_usage = {}
        student_usage = {}

        for cclass, (room, ts) in self.assignments.items():
            # Room availability
            if ts.id not in room.available_times:
                penalty += 1000

            # Room conflict
            key_room = (room, ts)
            if key_room in room_usage:
                penalty += 1000
            else:
                room_usage[key_room] = cclass

            # Teacher conflict
            key_teacher = (cclass.course.teacher, ts)
            if key_teacher in teacher_usage:
                penalty += 1000
            else:
                teacher_usage[key_teacher] = cclass

            # Capacity violation
            if len(cclass.students) > room.capacity:
                penalty += 10 * (len(cclass.students) - room.capacity)

        # Student conflicts
        for student in students:
            taken = {}
            for cclass in self.course_classes:
                if cclass.course.name in student.courses and student in cclass.students:
                    room, ts = self.assignments[cclass]
                    if ts in taken:
                        penalty += 1000
                    else:
                        taken[ts] = cclass

        return penalty

# =========================
# Genetic Algorithm
# =========================
def crossover(p1, p2):
    child = Schedule(p1.course_classes, p1.rooms, p1.timeslots)
    child.assignments = {}
    for cclass in p1.course_classes:
        if random.random() < 0.5:
            child.assignments[cclass] = p1.assignments[cclass]
        else:
            child.assignments[cclass] = p2.assignments[cclass]
    return child

def mutate(schedule):
    cclass = random.choice(schedule.course_classes)
    valid_pairs = [(room, ts) for room in schedule.rooms for ts in schedule.timeslots if ts.id in room.available_times]
    schedule.assignments[cclass] = random.choice(valid_pairs)

def genetic_algorithm(courses, rooms, timeslots, students, population_size=50, generations=100):
    # expand courses into CourseClass (A, B, C)
    course_classes = []
    for course in courses:
        for i in range(course.num_classes):
            course_classes.append(CourseClass(course, chr(65+i)))

    # assign students into classes (round-robin for simplicity)
    for student in students:
        for cname in student.courses:
            selected_classes = [c for c in course_classes if c.course.name == cname]
            target = min(selected_classes, key=lambda x: len(x.students))
            target.students.append(student)

    # init population
    population = []
    for _ in range(population_size):
        s = Schedule(course_classes, rooms, timeslots)
        s.randomize()
        population.append(s)

    # evolution loop
    for gen in range(generations):
        scored = [(s.fitness(students), s) for s in population]
        scored.sort(key=lambda x: x[0])
        best_score, best_schedule = scored[0]
        print(f"Gen {gen} best fitness = {best_score}")

        if best_score == 0:
            return best_schedule

        survivors = [s for _, s in scored[:population_size//2]]
        children = []
        while len(children) < population_size//2:
            p1, p2 = random.sample(survivors, 2)
            child = crossover(p1, p2)
            if random.random() < 0.2:  # mutation rate
                mutate(child)
            children.append(child)

        population = survivors + children

    return scored[0][1]

# =========================
# Example Usage
# =========================
if __name__ == "__main__":
    courses = [
        Course("Math", "Dr. A", num_classes=2),
        Course("Physics", "Dr. B", num_classes=1),
        Course("CS", "Dr. C", num_classes=2)
    ]

    rooms = [
        Room("R1", 30, {1,2,3,4}),
        Room("R2", 20, {2,3,5}),
        Room("Lab", 25, {1,3,4,5})
    ]

    timeslots = [
        Timeslot(1, "Mon", "08:00"),
        Timeslot(2, "Mon", "10:00"),
        Timeslot(3, "Tue", "08:00"),
        Timeslot(4, "Tue", "10:00"),
        Timeslot(5, "Wed", "08:00")
    ]

    students = [
        Student("S1", ["Math", "Physics"]),
        Student("S2", ["Math", "CS"]),
        Student("S3", ["Physics", "CS"]),
        Student("S4", ["Math", "CS"]),
        Student("S5", ["CS"]),
    ]

    best = genetic_algorithm(courses, rooms, timeslots, students, generations=50)

    print("\n=== BEST SCHEDULE ===")
    for cclass, (room, ts) in best.assignments.items():
        print(f"{cclass} -> {room.name} at {ts}")
