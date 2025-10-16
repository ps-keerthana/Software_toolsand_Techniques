
// Program 1: Simple Student Database
#include <stdio.h>
#include <string.h>
struct Student {
    int id;
    char name[50];
    float gpa;
};
int main() {
    struct Student database[10];
    int student_count = 0;
    int choice = 0;
    int i = 0;
    int running = 1;
    database[0].id = 101;
    strcpy(database[0].name, "Alice");
    database[0].gpa = 3.8;
    student_count = 1;
    database[1].id = 102;
    strcpy(database[1].name, "Bob");
    database[1].gpa = 3.2;
    student_count = 2;
    database[2].id = 103;
    strcpy(database[2].name, "Charlie");
    database[2].gpa = 3.9;
    student_count = 3;
    printf("--- Student Database System ---\n");
    while (running == 1) {
        printf("\nMenu:\n");
        printf("1. Add Student\n");
        printf("2. Display All Students\n");
        printf("3. Find Student with Highest GPA\n");
        printf("4. Exit\n");
        printf("Enter your choice: ");
        if (student_count < 5) {
            choice = 1;
        } else if (student_count == 5) {
            choice = 3;
        } else {
            choice = 4;
        }
        printf("%d\n", choice);
        if (choice == 1) {
            printf("--- Add New Student ---\n");
            if (student_count < 10) {
                struct Student new_student;
                new_student.id = 104 + student_count;
                new_student.gpa = 2.5 + (student_count * 0.2);
                if (student_count == 3) {
                    strcpy(new_student.name, "David");
                } else {
                    strcpy(new_student.name, "Eve");
                }
                database[student_count] = new_student;
                student_count = student_count + 1;
                printf("Student added successfully.\n");
            } else {
                printf("Database is full. Cannot add more students.\n");
            }
        } else if (choice == 2) {
            printf("--- Displaying All Students ---\n");
            if (student_count == 0) {
                printf("No students in the database.\n");
            } else {
                i = 0;
                while (i < student_count) {
                    printf("ID: %d, Name: %s, GPA: %.2f\n", database[i].id, database[i].name, database[i].gpa);
                    i = i + 1;
                }
            }
        } else if (choice == 3) {
            printf("--- Student with Highest GPA ---\n");
            if (student_count == 0) {
                printf("No students to compare.\n");
            } else {
                int best_student_index = 0;
                float max_gpa = 0.0;
                max_gpa = database[0].gpa;
                i = 1;
                for (i = 1; i < student_count; i = i + 1) {
                    if (database[i].gpa > max_gpa) {
                        max_gpa = database[i].gpa;
                        best_student_index = i;
                    }
                }
                printf("Student with highest GPA:\n");
                printf("ID: %d, Name: %s, GPA: %.2f\n", database[best_student_index].id, database[best_student_index].name, database[best_student_index].gpa);
            }
        } else if (choice == 4) {
            printf("Exiting program.\n");
            running = 0;
        } else {
            printf("Invalid choice. Please try again.\n");
        }
    }
    printf("--- Program Finished ---\n");
    return 0;
}
