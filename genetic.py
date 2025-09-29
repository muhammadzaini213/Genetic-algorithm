import random

# =========================
# Data Structures
# =========================
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

            # Teacher conflict - now using the specific teacher assigned to this section
            key_teacher = (cclass.teacher, ts)
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

def assign_teachers_to_sections(courses):
    """Assign teachers to course sections using round-robin or random assignment"""
    course_classes = []
    
    for course in courses:
        available_teachers = course.teachers.copy()
        
        for i in range(course.num_classes):
            section_letter = chr(65 + i)  # A, B, C, etc.
            
            # Strategy 1: Round-robin assignment
            teacher = available_teachers[i % len(available_teachers)]
            
            # Strategy 2: Random assignment (uncomment to use)
            # teacher = random.choice(available_teachers)
            
            # Strategy 3: Prefer one teacher per section if possible (uncomment to use)
            # if i < len(available_teachers):
            #     teacher = available_teachers[i]
            # else:
            #     teacher = random.choice(available_teachers)
            
            course_class = CourseClass(course, section_letter, teacher)
            course_classes.append(course_class)
    
    return course_classes

def genetic_algorithm(courses, rooms, timeslots, students, population_size=50, generations=100):
    # Expand courses into CourseClass with assigned teachers
    course_classes = assign_teachers_to_sections(courses)

    # Assign students to classes (round-robin for simplicity)
    for student in students:
        for cname in student.courses:
            selected_classes = [c for c in course_classes if c.course.name == cname]
            target = min(selected_classes, key=lambda x: len(x.students))
            target.students.append(student)

    # Initialize population
    population = []
    for _ in range(population_size):
        s = Schedule(course_classes, rooms, timeslots)
        s.randomize()
        population.append(s)

    # Evolution loop
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
    # Now courses can have multiple teachers
    courses = [
        Course("Aljabar Linier dan Geometri", ["Ramadhan Paninggalih"], num_classes=3),
        Course("Arsitektur Komputer", ["Aninditya Anggari Nuryono", "Aninditya Anggari Nuryono", "Riska Kurniyanto Abdullah"], num_classes=3),
        Course("Capstone Project", ["Ramadhan Paninggalih"], num_classes=1),
        Course("Deep Learning", ["Boby Mugi Pratama"], num_classes=1),
        Course("Desain Web", ["Rizal Kusuma Putra"], num_classes=2),
        Course("Implementasi dan Pengujian Perangkat Lunak", ["Nur Fajri Azhar"],
                num_classes=3),
        Course("Interaksi Manusia dan Komputer", ["Nisa Rizqiya Fadhliana"], 
                num_classes=3),
        Course("Kapita Selekta", ["Nisa Rizqiya Fadhliana"], num_classes=1),
        Course("Keamanan Siber (Pengayaan)", ["Darmansyah"], num_classes=1),
        Course("Kecerdasan Web", ["Gusti Ahmad Fanshuri Alfarisy"],
                num_classes=1),
        Course("Keprofesian Informatika", ["Nur Fajri Azhar", "Darmansyah"], num_classes=2),
        Course("Kerja Praktek", ["Nisa Rizqiya Fadhliana"], num_classes=1),
        Course("Komputasi Evolusioner", ["Muchammad Chandra Cahyo Utomo"], num_classes=1), 
        Course("Manajemen Basis Data", ["Bowo Nugroho"], num_classes=3),
        Course("Manajemen Proyek TIK", ["Riska Kurniyanto Abdullah"],
                num_classes=1),
        Course("Matematika Diskrit", ["Ramadhan Paninggalih"], num_classes=2),
        Course("Pemrograman Fungsional", ["Gusti Ahmad Fanshuri Alfarisy"], num_classes=2),
        Course("Pemrosesan Bahasa Alami", ["Bima Prihasto"], num_classes=1),
        Course("Pengantar Informatika", ["Muchammad Chandra Cahyo Utomo"],
                num_classes=2),
        Course("Pengantar Kecerdasan Artifisial", ["Bima Prihasto", "Bima Prihasto", "Gusti Ahmad Fanshuri Alfarisy"], num_classes=3),
        Course("Pengembangan Aplikasi Perangkat Bergerak", ["Rizal Kusuma Putra"], num_classes=2),
        Course("Pengolahan Citra Digital", ["Rizky Amelia"], num_classes=2),
        Course("Proposal Tugas Akhir", ["Nisa Rizqiya Fadhliana"], num_classes=1),
        Course("Sains Data (Pengayaan)", ["Ramadhan Paninggalih"], num_classes=1),
        Course("Sistem Digital", ["Boby Mugi Pratama"], num_classes=3),
        Course("Sistem Operasi", ["Darmansyah"], num_classes=3),
        Course("Sistem Paralel dan Terdistribusi", ["Riska Kurniyanto Abdullah"], num_classes=2),
        Course("Struktur Data", ["Muchammad Chandra Cahyo Utomo", "Muchammad Chandra Cahyo Utomo", "Bowo Nugroho"], num_classes=3),
        Course("Tugas Akhir", ["Nisa Rizqiya Fadhliana"], num_classes=1),
        Course("Visi Komputer", ["Rizky Amelia"], num_classes=1),

    ]

    rooms = [
        Room("R1", 30, {1,2,3,4}),
        Room("R2", 20, {2,3,5}),
        Room("R3", 25, {1,2,4,5}),
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
        Student("S5", ["CS", "Physics"]),
        Student("S6", ["Math"]),
        Student("S7", ["Physics"]),
        Student("S8", ["Math", "CS"]),
    ]

    best = genetic_algorithm(courses, rooms, timeslots, students, generations=50)

    print("\n=== BEST SCHEDULE ===")
    for cclass, (room, ts) in best.assignments.items():
        student_count = len(cclass.students)
        print(f"{cclass} -> {room.name} at {ts} ({student_count} students)")
    
    print("\n=== TEACHER ASSIGNMENTS ===")
    teacher_schedule = {}
    for cclass, (room, ts) in best.assignments.items():
        if cclass.teacher not in teacher_schedule:
            teacher_schedule[cclass.teacher] = []
        teacher_schedule[cclass.teacher].append((cclass, room, ts))
    
    for teacher, assignments in teacher_schedule.items():
        print(f"\n{teacher}:")
        for cclass, room, ts in assignments:
            print(f"  {cclass.course.name}-{cclass.section} in {room.name} at {ts}")
