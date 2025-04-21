# Ryleigh Mathieu
# 10/16/22
# Project Two

from termcolor import colored


def show_instructions():
    # prints storyline and game instructions
    print('\nHARRY POTTER ADVENTURE GAME:')
    print(' Voldemort and the Death Eaters have made their way into Hogwarts.\n In order for you to save the school you'
          ' must collect all of Voldemort’s Horcruxes and destroy them with the basilisk fang.\n This will make him '
          'vulnerable, therefore helping your fellow witches and wizards end this once and for all.')
    print('\n')
    print('GAME INSTRUCTIONS:')
    print("Move commands: North, South, East, West \nAdd to inventory: Get 'item name’ \nAfter "
          "collecting all items, use command ‘destroy all’")
    print('NOTE: commands are case sensitive')
    print('------------------------------')


def main():
    # This is a dictionary linking a room to other rooms in the school as well as linking each item to their room
    rooms = {
        'Great Hall': {'South': 'Corridor', 'item': 'Voldemort'},  # location of villain
        'Dormitory': {'East': 'Gryffindor Common Room', 'item': "Tom Riddle's Diary"},
        'Gryffindor Common Room': {'West': 'Dormitory', 'East': 'Corridor', 'South': 'Room of Requirement', 'item': ''},
        'Corridor': {'West': 'Gryffindor Common Room', 'North': 'Great Hall', 'East': "Headmaster's Office", 'South':
                     'Potions Classroom', 'item': 'Nagini'},
        "Headmaster's Office": {'West': 'Corridor', 'item': "Marvolo Gaunt's Ring"},
        'Potions Classroom': {'North': 'Corridor', 'South': 'Store Room', 'item': "Salazar Slytherin’s locket"},
        'Store Room': {'North': 'Potions Classroom', 'item': "Helga Hufflepuff’s Cup"},
        'Room of Requirement': {'North': 'Gryffindor Common Room', 'South': 'Chamber of Secrets',
                                'item': "Rowena Ravenclaw’s Diadem"},
        'Chamber of Secrets': {'North': 'Room of Requirement', 'item': 'Basilisk Fang'}
    }

    current_room = 'Gryffindor Common Room'  # displays starting room
    inventory = []  # creates inventory
    show_instructions()  # displays instructions

    while True:  # while loop
        if current_room == 'Great Hall':
            # winning scenario
            if len(inventory) == 7:  # if you collect all items you will be prompted to enter a move
                print("\nYou have entered the Great Hall. In order to defeat Voldemort you must destroy all Horcruxes"
                      "with the basilisk fang --> enter 'destroy all'")
                user_input = input('Enter move')  # asks user for move
                if user_input == 'destroy all':
                    print('Congratulations you have defeated Voldemort and saved the school!')
                    print('Thank you for playing!')
                    break  # ends program
                else:
                    print(colored('invalid input', 'red'))
                    continue

            # losing scenario (user doesn't have all items before entering Great Hall)
            else:
                print('\nOh no! You did not collect all of the items!')
                print('Voldemort overpowered you and has taken control of Hogwarts.')
                print('Thanks for playing!')
                break  # ends program

        print('\nYou are in the', current_room + '.')  # prints current room location
        print('Inventory:', inventory, '\n')  # prints inventory
        print('------------------------------')

        if current_room != 'Great Hall' and current_room != 'Gryffindor Common Room' and 'item' in rooms[current_room].keys():
            print('\n* You see {} *\n'.format(rooms[current_room]['item']))
            print('------------------------------')

        user_input = input('Enter move ')  # user inputs move
        # user input for directions
        if user_input == 'exit':
            break
        elif user_input in rooms[current_room].keys():
            current_room = rooms[current_room][user_input]
        # user input for getting items
        elif user_input == str('Get ' + rooms[current_room].get("item")):
            print('You pick up {}\n'.format(rooms[current_room]["item"]))
            print('------------------------------')
            inventory.append(rooms[current_room]["item"])  # adds item to inventory
            del rooms[current_room]["item"]  # deletes item, so cannot be added again
        else:
            print(colored('Invalid move, please try again', 'red'))
            continue


main()
