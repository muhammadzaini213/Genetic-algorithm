import random
from StaticData import courses_data, rooms_data, timeslots_data
from DataGenerator import angkatan25, angkatan24, angkatan23
from DataTypes import CourseClass

class Schedule:
    def __init__(self, course_classes, rooms, timeslots):
        self.course_classes = course_classes
        self.rooms = rooms
        self.timeslots = timeslots
        self.assignments = {}

    def randomize(self):
        for cclass in self.course_classes:
            valid_pairs = [(room, ts) for room in self.rooms for ts in self.timeslots if ts.id in room.available_times]
            self.assignments[cclass] = random.choice(valid_pairs)

    def fitness(self, students):
        penalty = 0

        room_usage = {}
        teacher_usage = {}
        student_usage = {}

        for cclass, (room, ts) in self.assignments.items():

            # Ketersediaan ruangan
            if ts.id not in room.available_times:
                penalty += 10_000_000

            # Konflik ruangan
            key_room = (room, ts)
            if key_room in room_usage:
                penalty += 100_000
            else:
                room_usage[key_room] = cclass

            # Konflik dosen
            key_teacher = (cclass.teacher, ts)
            if key_teacher in teacher_usage:
                penalty += 1000
            else:
                teacher_usage[key_teacher] = cclass

            # Kelebihan kapasitas, kecil aja
            over = len(cclass.students) - room.capacity
            if over > 30:  # abaikan sampai 20 siswa
                penalty += over-30  # hanya kelebihan > 20 dihitung

    # Konflik mahasiswa
        for student in students:
            taken = {}
            for cclass in self.course_classes:
                if cclass.course.name in student.courses and student in cclass.students:
                    room, ts = self.assignments[cclass]
                    if ts in taken:
                        penalty += 10
                    else:
                        taken[ts] = cclass

        return penalty


# Algoritma Genetika
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

def assign_teachers_to_sections(courses):
        """Assign teachers to course sections using round-robin or random assignment"""
        course_classes = []

        for course in courses:
            available_teachers = course.teachers.copy()

            for i in range(course.num_classes):
                section_letter = chr(65 + i)
                teacher = available_teachers[i % len(available_teachers)]
 
                course_class = CourseClass(course, section_letter, teacher)
                course_classes.append(course_class)

        return course_classes

def genetic_algorithm(courses, rooms, timeslots, students, population_size=50,
                      generations=100):
        course_classes = assign_teachers_to_sections(courses)

        for student in students:
            for cname in student.courses:
                selected_classes = [c for c in course_classes if c.course.name == cname]
                target = min(selected_classes, key=lambda x: len(x.students))
                target.students.append(student)

        population = []
        for _ in range(population_size):
            s = Schedule(course_classes, rooms, timeslots)
            s.randomize()
            population.append(s)

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
                if random.random() < 0.1:  # mutation rate
                    mutate(child)
                children.append(child)

            population = survivors + children

        return scored[0][1]


if __name__ == "__main__":
    
    students = angkatan25() + angkatan24() + angkatan23()

    best = genetic_algorithm(courses_data, rooms_data, timeslots_data, students,
                             population_size=1000,
                             generations=100)

    print("\n=== Jadwal Terbaik ===")
    for cclass, (room, ts) in best.assignments.items():
        student_count = len(cclass.students)
        print(f"{cclass} -> {room.name} di {ts} ({student_count} students)")

    print("\n=== Jadwal Dosen ===")
    teacher_schedule = {}
    for cclass, (room, ts) in best.assignments.items():
        if cclass.teacher not in teacher_schedule:
            teacher_schedule[cclass.teacher] = []
        teacher_schedule[cclass.teacher].append((cclass, room, ts))

    for teacher, assignments in teacher_schedule.items():
        print(f"\n{teacher}:")
        for cclass, room, ts in assignments:
            print(f"  {cclass.course.name}-{cclass.section} di {room.name} pada {ts}")


