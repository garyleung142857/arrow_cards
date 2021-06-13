import os
from PIL import Image, ImageDraw, ImageFont

IMGDIR = os.path.join('img', 'caret-up.png')
IMGSIZE = 200
ROW = 8
COL = 6
COLORS = ['#C7E889', '#F2CB8F', '#DB8DAC', '#D7D8F5', '#D1EBE1']
COLORBACKS = [Image.new('RGBA', (IMGSIZE, IMGSIZE), c) for c in COLORS]
imgset = [Image.open(IMGDIR).resize((IMGSIZE, IMGSIZE)).rotate(-90 * i) for i in range(4)]

def _coloring(r, c):
    return COLORBACKS[(2 * r + c) % 5]

def _gen_cardback(seq):
    '''seq: list. sequence of cards with length ROW * COL'''
    
    size = (COL * IMGSIZE, (ROW + 1) * IMGSIZE)
    back = Image.new('RGBA', size, '#DB8DAC')
    front = Image.new('RGBA', size, '#00000000')
    fnt = ImageFont.truetype(os.path.join('font', 'NotoSansTC-Medium.otf'), 45)
    draw = ImageDraw.Draw(front)
    for c in range(COL):
        for r in range(ROW):
            board_no = r * COL + c + 1
            back.paste(_coloring(r, c), (c * IMGSIZE, r * IMGSIZE))
            front.paste(imgset[seq[board_no - 1]], (c * IMGSIZE, r * IMGSIZE))

            w, h = draw.textsize(str(board_no), font=fnt)
            draw.text(((c + 0.5) * IMGSIZE - w / 2, (r + 0.5) * IMGSIZE - h / 2), str(board_no), fill='#333333', font = fnt)
    title = 'Deck 1'
    title_fnt = ImageFont.truetype(os.path.join('font', 'NotoSansTC-Medium.otf'), 90)
    w, h = draw.textsize(title, font=title_fnt)
    draw.text((COL * IMGSIZE / 2 - w / 2, (ROW + 0.5) * IMGSIZE - h / 2), title, fill='black', font = title_fnt)
    return Image.alpha_composite(back, front)
