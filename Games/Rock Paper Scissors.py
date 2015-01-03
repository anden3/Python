from random import randint


def rps():
    player_choice = input('Rock, paper or scissors?: ').casefold()
    comp_choice = randint(0, 2)

    if player_choice == 'rock':
        player_choice = 0
    elif player_choice == 'paper':
        player_choice = 1
    elif player_choice == 'scissors':
        player_choice = 2

    if player_choice == comp_choice:
        print('Draw')
    elif player_choice == comp_choice + 1 or player_choice == comp_choice - 2:
        print('Player has won!')
    elif comp_choice == player_choice + 1 or comp_choice == player_choice - 2:
        print('Computer has won!')

rps()