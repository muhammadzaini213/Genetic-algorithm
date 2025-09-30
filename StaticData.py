from DataTypes import Course, Room, Timeslot

courses_data = [
    Course("Aljabar Linier dan Geometri", ["Ramadhan Paninggalih"], num_classes=3),
    Course("Arsitektur Komputer", ["Aninditya Anggari Nuryono", "Aninditya Anggari Nuryono", "Riska Kurniyanto Abdullah"], num_classes=3),
    Course("Deep Learning", ["Boby Mugi Pratama"], num_classes=1),
    Course("Desain Web", ["Rizal Kusuma Putra"], num_classes=2),
    Course("Implementasi dan Pengujian Perangkat Lunak", ["Nur Fajri Azhar"],
           num_classes=3),
    Course("Interaksi Manusia dan Komputer", ["Nisa Rizqiya Fadhliana"], 
           num_classes=3),
    Course("Keamanan Siber (Pengayaan)", ["Darmansyah"], num_classes=1),
    Course("Kecerdasan Web", ["Gusti Ahmad Fanshuri Alfarisy"],
           num_classes=1),
    Course("Keprofesian Informatika", ["Nur Fajri Azhar", "Darmansyah"], num_classes=2),
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
    Course("Visi Komputer", ["Rizky Amelia"], num_classes=1),

]

rooms_data = [
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
    Room("E-304", 40, {8}),
    Room("E-305", 100, {3,4,7,9,12}),
    Room("E-306", 40, {8,13}),
    Room("E-307", 40, {1,8,12,16,18}),
    Room("F-103", 40, {1}),
]

timeslots_data = [
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

