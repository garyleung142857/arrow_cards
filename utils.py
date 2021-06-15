SUITS = ['S', 'H', 'D', 'C']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']


def _num_to_str(num):
    '''from 0-51 to string. eg 27-> D3'''
    suit = SUITS[num // 13]
    rank = RANKS[num % 13]
    return suit + rank


def _str_to_num(s):
    '''from string to 0-51. eg D3 -> 27'''
    return SUITS.index(s[0].upper()) * 13 + RANKS.index(s[1].upper())
