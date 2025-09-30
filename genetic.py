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

    def copy(self):
        """Create a deep copy of the schedule"""
        new_schedule = Schedule(self.course_classes, self.rooms, self.timeslots)
        new_schedule.assignments = self.assignments.copy()
        return new_schedule

    def fitness(self, students):
        penalty = 0

        room_usage = {}
        teacher_usage = {}

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

            # Kelebihan kapasitas
            over = len(cclass.students) - room.capacity
            if over > 30:
                penalty += over - 30

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


def crossover(p1, p2):
    """Uniform crossover between two parent schedules"""
    child = Schedule(p1.course_classes, p1.rooms, p1.timeslots)
    child.assignments = {}
    for cclass in p1.course_classes:
        if random.random() < 0.5:
            child.assignments[cclass] = p1.assignments[cclass]
        else:
            child.assignments[cclass] = p2.assignments[cclass]
    return child


def mutate(schedule, mutation_rate=0.2):
    """Mutate schedule by reassigning classes based on mutation rate"""
    for cclass in schedule.course_classes:
        if random.random() < mutation_rate:
            valid_pairs = [(room, ts) for room in schedule.rooms 
                          for ts in schedule.timeslots 
                          if ts.id in room.available_times]
            if valid_pairs:
                schedule.assignments[cclass] = random.choice(valid_pairs)


def local_search(schedule, students, iterations=10):
    """Apply hill climbing to improve the schedule"""
    current_fitness = schedule.fitness(students)
    
    for _ in range(iterations):
        if len(schedule.course_classes) < 2:
            break
            
        # Try swapping two random assignments
        cclass1, cclass2 = random.sample(schedule.course_classes, 2)
        
        # Swap
        schedule.assignments[cclass1], schedule.assignments[cclass2] = \
            schedule.assignments[cclass2], schedule.assignments[cclass1]
        
        new_fitness = schedule.fitness(students)
        
        if new_fitness < current_fitness:
            current_fitness = new_fitness
        else:
            # Revert swap if not better
            schedule.assignments[cclass1], schedule.assignments[cclass2] = \
                schedule.assignments[cclass2], schedule.assignments[cclass1]
    
    return schedule


def tournament_selection(scored_population, tournament_size=3):
    """Select an individual using tournament selection"""
    tournament = random.sample(scored_population, min(tournament_size, len(scored_population)))
    return min(tournament, key=lambda x: x[0])[1]


def assign_teachers_to_sections(courses):
    """Assign teachers to course sections using round-robin"""
    course_classes = []

    for course in courses:
        available_teachers = course.teachers.copy()

        for i in range(course.num_classes):
            section_letter = chr(65 + i)
            teacher = available_teachers[i % len(available_teachers)]

            course_class = CourseClass(course, section_letter, teacher)
            course_classes.append(course_class)

    return course_classes


def genetic_algorithm(courses, rooms, timeslots, students, 
                      population_size=100,
                      generations=500,
                      elite_size=10,
                      tournament_size=5,
                      base_mutation_rate=0.15,
                      local_search_frequency=10):
    """
    Improved genetic algorithm with:
    - Elitism
    - Tournament selection
    - Adaptive mutation
    - Local search
    - Diversity preservation
    - Stagnation detection and recovery
    """
    
    # Assign teachers and students to classes
    course_classes = assign_teachers_to_sections(courses)

    for student in students:
        for cname in student.courses:
            selected_classes = [c for c in course_classes if c.course.name == cname]
            if selected_classes:
                target = min(selected_classes, key=lambda x: len(x.students))
                target.students.append(student)

    # Initialize population
    print("Initializing population...")
    population = []
    for _ in range(population_size):
        s = Schedule(course_classes, rooms, timeslots)
        s.randomize()
        population.append(s)

    # Tracking variables
    best_ever_score = float('inf')
    best_ever_schedule = None
    stagnant_count = 0
    
    print(f"Starting genetic algorithm with {len(course_classes)} classes, "
          f"{len(rooms)} rooms, {len(timeslots)} timeslots, {len(students)} students")
    
    for gen in range(generations):
        # Evaluate fitness
        scored = [(s.fitness(students), s) for s in population]
        scored.sort(key=lambda x: x[0])
        best_score, best_schedule = scored[0]
        avg_score = sum(score for score, _ in scored) / len(scored)
        
        print(f"Gen {gen:3d} | Best: {best_score:8.0f} | Avg: {avg_score:10.0f} | Stagnant: {stagnant_count}")

        # Check if we found perfect solution
        if best_score == 0:
            print("\n✓ Perfect schedule found!")
            return best_schedule

        # Track best ever
        if best_score < best_ever_score:
            best_ever_score = best_score
            best_ever_schedule = best_schedule.copy()
            stagnant_count = 0
        else:
            stagnant_count += 1

        # Apply local search to best individuals periodically
        if gen % local_search_frequency == 0 and gen > 0:
            print(f"  Applying local search to top {elite_size} individuals...")
            for i in range(min(elite_size, len(scored))):
                scored[i] = (scored[i][1].fitness(students), 
                            local_search(scored[i][1].copy(), students, iterations=20))
            scored.sort(key=lambda x: x[0])

        # Diversity injection if stagnant
        if stagnant_count > 30:
            print(f"  Population stagnant! Injecting diversity...")
            # Keep only the best individuals
            population = [s for _, s in scored[:elite_size]]
            # Generate new random individuals
            for _ in range(population_size - elite_size):
                s = Schedule(course_classes, rooms, timeslots)
                s.randomize()
                population.append(s)
            stagnant_count = 0
            continue

        # Adaptive mutation rate (increase when stagnant)
        mutation_rate = base_mutation_rate + (stagnant_count * 0.01)
        mutation_rate = min(mutation_rate, 0.5)  # Cap at 50%

        # Elitism: keep best individuals
        elite = [s for _, s in scored[:elite_size]]
        
        # Generate offspring
        children = []
        while len(children) < population_size - elite_size:
            # Tournament selection for parents
            p1 = tournament_selection(scored, tournament_size)
            p2 = tournament_selection(scored, tournament_size)
            
            # Crossover
            child = crossover(p1, p2)
            
            # Mutation
            mutate(child, mutation_rate=mutation_rate)
            
            children.append(child)

        # New population
        population = elite + children

    print(f"\nGenetic algorithm completed. Best fitness: {best_ever_score}")
    return best_ever_schedule if best_ever_schedule else scored[0][1]


if __name__ == "__main__":
    print("=" * 60)
    print("COURSE SCHEDULING WITH GENETIC ALGORITHM")
    print("=" * 60)

    students = angkatan25() + angkatan24() + angkatan23()
    print(f"\nTotal students: {len(students)}")

    best = genetic_algorithm(
        courses_data, 
        rooms_data, 
        timeslots_data, 
        students,
        population_size=100,
        generations=500,
        elite_size=10,
        tournament_size=5,
        base_mutation_rate=0.15,
        local_search_frequency=10
    )

    print("\n" + "=" * 60)
    print("FINAL SCHEDULE")
    print("=" * 60)
    
    final_fitness = best.fitness(students)
    print(f"\nFinal Fitness (Penalty): {final_fitness}")
    
    if final_fitness == 0:
        print("✓ Perfect schedule with no conflicts!")
    else:
        print("⚠ Schedule has some conflicts/penalties")

    print("\n=== Course Schedule ===")
    sorted_assignments = sorted(
        best.assignments.items(),
        key=lambda x: (x[0].course.name, x[0].section)
    )
    
    for cclass, (room, ts) in sorted_assignments:
        student_count = len(cclass.students)
        capacity_status = "✓" if student_count <= room.capacity else "⚠ OVER"
        print(f"{cclass.course.name:20s} {cclass.section} | "
              f"{cclass.teacher:20s} | {room.name:15s} | "
              f"{ts} | {student_count:3d}/{room.capacity:3d} {capacity_status}")

    print("\n=== Teacher Schedule ===")
    teacher_schedule = {}
    for cclass, (room, ts) in best.assignments.items():
        if cclass.teacher not in teacher_schedule:
            teacher_schedule[cclass.teacher] = []
        teacher_schedule[cclass.teacher].append((cclass, room, ts))

    for teacher in sorted(teacher_schedule.keys()):
        assignments = teacher_schedule[teacher]
        print(f"\n{teacher}:")
        sorted_assignments = sorted(assignments, key=lambda x: x[2].id)
        for cclass, room, ts in sorted_assignments:
            print(f"  {cclass.course.name:20s} {cclass.section} | "
                  f"{room.name:15s} | {ts}")

    print("\n" + "=" * 60)
