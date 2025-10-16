
// Program 2: Text-Based Mini-Adventure Game
#include <stdio.h>
int main() {
    int player_health = 100;
    int player_gold = 10;
    int player_location = 0;
    int has_sword = 0;
    int has_key = 0;
    int game_over = 0;
    printf("Welcome to the C Dungeon Adventure!\n");
    printf("You are in the entrance hall. There are doors to the North and East.\n");
    while (game_over == 0) {
        printf("----------------------------------------\n");
        printf("Health: %d, Gold: %d\n", player_health, player_gold);
        if (player_location == 0) {
            printf("You are in the Entrance Hall. Doors are to the North and East.\n");
            int choice = 1;
            printf("You choose to go North.\n");
            if (choice == 1) {
                player_location = 1;
            } else {
                player_location = 2;
            }
        } else if (player_location == 1) {
            printf("You are in the Armory. You see a rusty sword.\n");
            if (has_sword == 0) {
                printf("You pick up the sword.\n");
                has_sword = 1;
            } else {
                printf("There is nothing else of interest here.\n");
            }
            printf("There is a door back to the South.\n");
            player_location = 0;
        } else if (player_location == 2) {
            printf("You are in the Treasury. You see a locked chest and a door to the West.\n");
            if (has_key == 1) {
                printf("You use the key to open the chest!\n");
                player_gold = player_gold + 100;
                printf("You found 100 gold!\n");
                printf("You decide to leave the dungeon with your riches.\n");
                player_location = 4;
            } else {
                printf("The chest is locked. You need a key.\n");
                player_location = 3;
            }
        } else if (player_location == 3) {
            printf("You entered a dark room. It was a trap!\n");
            player_health = player_health - 50;
            printf("You lost 50 health. You stumble out and find a key on the floor.\n");
            has_key = 1;
            if (player_health <= 0) {
                printf("Your health is too low. You have perished.\n");
                game_over = 1;
            } else {
                printf("You find your way back to the Treasury, weakened but with a key.\n");
                player_location = 2;
            }
        } else if (player_location == 4) {
            printf("You have found the exit!\n");
            game_over = 1;
        }
        if (player_health <= 0) {
            printf("You have succumbed to your injuries.\n");
            game_over = 1;
        }
        if (player_gold > 100) {
            game_over = 1;
        }
    }
    printf("--- GAME OVER ---\n");
    printf("Final Stats: Health=%d, Gold=%d\n", player_health, player_gold);
    if (player_gold > 100) {
        printf("You escaped a rich adventurer!\n");
    } else {
        printf("Your adventure has come to an end.\n");
    }
    return 0;
}
