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
                penalty += 1 * (len(cclass.students) - room.capacity)

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

def genetic_algorithm(courses, rooms, timeslots, students, population_size=200,
                      generations=1000):
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
        Room("A-105", 80, {17}),
        Room("A-308", 80, {6, 12}),
        Room("B-102", 40, {14}),
        Room("B-103", 40, {1,6,9,11,14,15,19}),
        Room("B-106", 40, {10,18}),
        Room("E-101", 40, {11,12}),
        Room("E-102", 80, {15}),
        Room("E-103", 40, {3,6,7,19}),
        Room("E-104", 60, {7,19}),
        Room("E-105", 40, {6,16}),
        Room("E-201", 60, {13,19}),
        Room("E-202", 80, {2,13}),
        Room("E-204", 60, {13,19}),
        Room("E-205", 80, {2,15}),
        Room("E-206", 40, {10,14}),
        Room("E-301", 60, {2,3,19}),
        Room("E-302", 40, {14}),
        Room("E-303", 40, {13,19}),
        Room("E-304", 40, {7}),
        Room("E-305", 100, {3,4,7,9,11}),
        Room("E-306", 40, {6,11}),
        Room("E-307", 40, {1,7,11,16,18}),
        Room("F-103", 40, {1}),
    ]

    timeslots = [
        # Senin
        Timeslot(1, "Senin", "07:30 - 10:00"),
        Timeslot(2, "Senin", "10:20 - 12:00"),
        Timeslot(3, "Senin", "13:00 - 15:30"),
        Timeslot(4, "Senin", "16:00 - 17:30"),

        # Selasa
        Timeslot(5, "Selasa", "07:30 - 10:00"),
        Timeslot(6, "Selasa", "10:20 - 12:00"),
        Timeslot(7, "Selasa", "13:00 - 15:30"),
        Timeslot(8, "Selasa", "16:00 - 17:30"),

        # Rabu
        Timeslot(9, "Rabu", "07:30 - 10:00"),
        Timeslot(10, "Rabu", "10:20 - 12:00"),
        Timeslot(11, "Rabu", "13:00 - 15:30"),
        Timeslot(12, "Rabu", "16:00 - 17:30"),

        # Kamis
        Timeslot(13, "Kamis", "07:30 - 10:00"),
        Timeslot(14, "Kamis", "10:20 - 12:00"),
        Timeslot(15, "Kamis", "13:00 - 15:30"),
        Timeslot(16, "Kamis", "16:00 - 17:30"),

        # Jumat
        Timeslot(17, "Jumat", "07:30 - 9:00"),
        Timeslot(18, "Jumat", "9:20 - 11:00"),
        Timeslot(19, "Jumat", "13:00 - 15:30"),
        Timeslot(20, "Jumat", "16:00 - 17:30"),
    ]

    students = [
        Student("11251001", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251002", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251003", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251004", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251005", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251006", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251007", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251008", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251009", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251010", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251011", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251012", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251013", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251014", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251015", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251016", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251017", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251018", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251019", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251020", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251021", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251022", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251023", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251024", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251025", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251026", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251027", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251028", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251029", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251030", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251031", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251032", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251033", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251034", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251035", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251036", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251037", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251038", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251039", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251040", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251041", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251042", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251043", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251044", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251045", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251046", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251047", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251048", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251049", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251050", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251051", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251052", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251053", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251054", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251055", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251056", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251057", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251058", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251059", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251060", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251061", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251062", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251063", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251064", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251065", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251066", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251067", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251068", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251069", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251070", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251071", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251072", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251073", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251074", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251075", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251076", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251077", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251078", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251079", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251080", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251081", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251082", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251083", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251084", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251085", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251086", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251087", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251088", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251089", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251090", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251091", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251092", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251093", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251094", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251095", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251096", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251097", ["Matematika Diskrit", "Pengantar Informatika"]),
        Student("11251098", ["Matematika Diskrit", "Pengantar Informatika"]),


        Student("11241001", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241002", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241003", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241004", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241005", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241006", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241007", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241008", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241009", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241010", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241011", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241012", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241013", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241014", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241015", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241016", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241017", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241018", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241019", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241020", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241021", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241022", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241023", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241024", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241025", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241026", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241027", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241028", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241029", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241030", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241031", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241032", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241033", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241034", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241035", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241036", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241037", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241038", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241039", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241040", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241041", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241042", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241043", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241044", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241045", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241046", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241047", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241048", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241049", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241050", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241051", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241052", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241053", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241054", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241055", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241056", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241057", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241058", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241059", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241060", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241061", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241062", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241063", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241064", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241065", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241066", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241067", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241068", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241069", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241070", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241071", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241072", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241073", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241074", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241075", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241076", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241077", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241078", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241079", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241080", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241081", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241082", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241083", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241084", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241085", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241086", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241087", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241088", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241089", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241090", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241091", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial", "Sistem Operasi", "Struktur Data"]),
        Student("11241092", ["Aljabar Linier dan Geometri", "Arsitektur Komputer", "Desain Web", "Pengantar Kecerdasan Artifisial",
                             "Sistem Operasi", "Struktur Data"]),


        Student("11231001", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231002", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231003", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231004", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231005", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231006", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231007", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231008", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231009", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231010", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231011", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231012", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231013", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231014", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231015", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231016", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231017", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231018", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231019", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231020", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231021", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231022", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231023", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231024", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231025", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231026", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231027", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231028", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231029", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231030", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231031", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231032", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231033", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231034", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231035", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231036", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231037", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231038", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231039", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231040", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231041", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231042", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231043", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231044", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231045", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231046", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231047", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231048", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231049", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231050", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231051", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231052", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231053", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231054", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231055", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231056", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231057", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231058", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231059", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231060", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231061", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231062", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231063", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231064", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231065", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231066", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231067", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231068", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231069", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231070", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231071", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231072", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231073", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231074", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231075", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231076", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231077", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231078", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231079", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231080", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231081", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231082", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231083", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231084", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231085", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231086", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231087", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231088", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231089", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231090", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231091", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),
        Student("11231092", ["Implementasi dan Pengujian Perangkat Lunak",
                             "Interaksi Manusia dan Komputer", "Pengantar Kecerdasan Artifisial",
                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                             "Desain Web", "Pemrograman Fungsional",
                             "Pengembangan Aplikasi Perangkat Bergerak"]),

        
    ]

    best = genetic_algorithm(courses, rooms, timeslots, students, generations=1000)

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
