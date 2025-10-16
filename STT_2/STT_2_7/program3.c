
// Program 3: Sorting Algorithm Execution
#include <stdio.h>
#define ARRAY_SIZE 15
int main() {
    int original_array[ARRAY_SIZE];
    int bubble_array[ARRAY_SIZE];
    int insertion_array[ARRAY_SIZE];
    int i = 0;
    int j = 0;
    int temp = 0;
    int key = 0;
    int choice = 1;
    printf("--- Sorting Algorithm Analyzer ---\n");
    i = 0;
    while (i < ARRAY_SIZE) {
        original_array[i] = ARRAY_SIZE - i;
        i = i + 1;
    }
    printf("Original Unsorted Array:\n");
    for (i = 0; i < ARRAY_SIZE; i = i + 1) {
        printf("%d ", original_array[i]);
        bubble_array[i] = original_array[i];
        insertion_array[i] = original_array[i];
    }
    printf("\n\n");
    if (choice == 1) {
        printf("Executing Bubble Sort...\n");
        for (i = 0; i < ARRAY_SIZE - 1; i = i + 1) {
            for (j = 0; j < ARRAY_SIZE - i - 1; j = j + 1) {
                if (bubble_array[j] > bubble_array[j + 1]) {
                    temp = bubble_array[j];
                    bubble_array[j] = bubble_array[j + 1];
                    bubble_array[j + 1] = temp;
                }
            }
        }
        printf("Array after Bubble Sort:\n");
        for (i = 0; i < ARRAY_SIZE; i = i + 1) {
            printf("%d ", bubble_array[i]);
        }
        printf("\n");
    } else {
        printf("Executing Insertion Sort...\n");
        for (i = 1; i < ARRAY_SIZE; i = i + 1) {
            key = insertion_array[i];
            j = i - 1;
            while (j >= 0 && insertion_array[j] > key) {
                insertion_array[j + 1] = insertion_array[j];
                j = j - 1;
            }
            insertion_array[j + 1] = key;
        }
        printf("Array after Insertion Sort:\n");
        for (i = 0; i < ARRAY_SIZE; i = i + 1) {
            printf("%d ", insertion_array[i]);
        }
        printf("\n");
    }
    int sorted_sum = 0;
    i = 0;
    while (i < ARRAY_SIZE) {
        if (choice == 1) {
            sorted_sum = sorted_sum + bubble_array[i];
        } else {
            sorted_sum = sorted_sum + insertion_array[i];
        }
        i = i + 1;
    }
    if (sorted_sum > 100) {
        printf("\nThe sum of sorted elements is greater than 100.\n");
    } else {
        printf("\nThe sum of sorted elements is not greater than 100.\n");
    }
    printf("--- Program Finished ---\n");
    return 0;
}
