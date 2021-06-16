import image
import os


if __name__ == '__main__':
    cardback = image.CardBack()
    cardback.collate(os.path.join('data', 'data1.txt'), 'all.pdf', 'Deck 1')