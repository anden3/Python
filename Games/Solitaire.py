deck = []
top_spots = [[], [], [], []]
stacks = [[], [], [], [], [], [], []]


def create_deck():
    for suit in ['K', 'R', 'H', 'S']:
        for card in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Kn', 'D', 'K']:
            deck.append(suit + "-" + card)


def fill_stacks():
    for stack_size in range(7, 0, -1):
        for stack in range(stack_size):
            stacks[stack].append(deck[0])
            deck.pop(0)

create_deck()
fill_stacks()
