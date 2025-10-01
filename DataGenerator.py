from DataTypes import Student
def angkatan25():
    akt25 = []
    for i in range (1,10):
        akt25.append(Student(f"1125100{i}", ["Matematika Diskrit", 
                                            "Pengantar Informatika",
                                             "Sistem Digital"]))
    for i in range (10, 99):
         akt25.append(Student(f"1125100{i}", ["Matematika Diskrit",             
                                              "Pengantar Informatika",
                                              "Sistem Digital"]))
    return akt25

def angkatan24():
    akt24 = []

    for i in range (1, 10):
        akt24.append(Student(f"1124100{i}", ["Aljabar Linier dan Geometri", 
                                             "Arsitektur Komputer", 
                                             "Desain Web", 
                                             "Interaksi Manusia dan Komputer",
                                             "Pengantar Kecerdasan Artifisial", 
                                             "Sistem Operasi", "Struktur Data"]))
    for i in range (10, 40):
        akt24.append(Student(f"112410{i}", ["Aljabar Linier dan Geometri",
                                            "Arsitektur Komputer",
                                            "Pengantar Kecerdasan Artifisial",
                                            "Sistem Operasi", 
                                            "Struktur Data"]))
    for i in range (40, 70):
        akt24.append(Student(f"112410{i}", ["Aljabar Linier dan Geometri",                  
                                            "Arsitektur Komputer",                              
                                            "Pengantar Kecerdasan Artifisial",              
                                            "Sistem Operasi", 
                                            "Struktur Data"]))
    for i in range (70,93):
        akt24.append(Student(f"112410{i}", ["Aljabar Linier dan Geometri",
                                            "Arsitektur Komputer",
                                            "Pengantar Kecerdasan Artifisial",
                                            "Sistem Operasi", "Struktur Data",
                                            "Keprofesian Informatika"]))
    return akt24

def angkatan23():
    akt23 = []
    for i in range (0,10):
        akt23.append(Student(f"1123100{i}", ["Implementasi dan Pengujian Perangkat Lunak",
                                             "Interaksi Manusia dan Komputer",
                                             "Pengantar Kecerdasan Artifisial",
                                             "Manajemen Basis Data", "Pengolahan Citra Digital",
                                             "Desain Web", "Pemrograman Fungsional",            
                                             "Pengembangan Aplikasi Perangkat Bergerak"]))
    for i in range (10, 40):
        akt23.append(Student(f"112310{i}", ["Implementasi dan Pengujian Perangkat Lunak",       
                                            "Pengantar Kecerdasan Artifisial",
                                             "Manajemen Basis Data",
                                            "Pemrograman Fungsional",]))
    for i in range (40,93):
        akt23.append(Student(f"112310{i}", ["Interaksi Manusia dan Komputer",                                                                    "Pengantar Kecerdasan Artifisial",
                                             "Manajemen Basis Data",
                                             "Pengolahan Citra Digital",
                                             "Desain Web", "Pemrograman Fungsional",]))
    return akt23


