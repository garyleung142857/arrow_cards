SUITS = ['S', 'H', 'D', 'C']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

def _parse_rbn(rbnstr):
    deck = [0] * 52
    hands = []
    a = rbnstr.replace(';', '.').split(':')
    for b in a:
        hands.append(b.split('.'))
    for i, h in enumerate(hands, 1):
        for j, s in enumerate(h):
            for c in s:
                card_index = j * 13 + RANKS.index(c)
                if deck[card_index] == 0:
                    deck[card_index] = i
                else:
                    raise ValueError(f'Card {SUITS[j]}{c} is assigned more than once.')
    if deck.count(1) == 13 and deck.count(2) == 13 and deck.count(3) == 13:
        deck = [x if x > 0 else 4 for x in deck]
    else:
        raise ValueError('Wrong format.')
    return deck
    