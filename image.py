import os
import utils
import parse
from PIL import Image, ImageDraw, ImageFont

IMGDIR = os.path.join('img', 'caret-up.png')
IMGSIZE = 200
ROW = 8
COL = 6
COLORS = ['#C7E889', '#F2CB8F', '#DB8DAC', '#D7D8F5', '#D1EBE1']
COLORBACKS = [Image.new('RGBA', (IMGSIZE, IMGSIZE), c) for c in COLORS]
imgset = [None] + [Image.open(IMGDIR).resize((IMGSIZE, IMGSIZE))
                   .rotate(-90 * i) for i in range(4)]


def _coloring(r, c):
    return COLORBACKS[(2 * r + c) % 5]


def _gen_cardback(seq, bg_color='#DB8DAC', title='Deck 1', card_name=''):
    '''seq: list. sequence of cards with length ROW * COL'''
    size = (COL * IMGSIZE, (ROW + 1) * IMGSIZE)
    back = Image.new('RGBA', size, bg_color)
    front = Image.new('RGBA', size, '#00000000')
    fnt = ImageFont.truetype(os.path.join('font', 'NotoSansTC-Medium.otf'), 45)
    draw = ImageDraw.Draw(front)
    for c in range(COL):
        for r in range(ROW):
            board_no = r * COL + c + 1
            back.paste(_coloring(r, c), (c * IMGSIZE, r * IMGSIZE))
            front.paste(imgset[seq[board_no - 1]], (c * IMGSIZE, r * IMGSIZE))

            w, h = draw.textsize(str(board_no), font=fnt)
            draw.text(
                ((c + 0.5) * IMGSIZE - w / 2, (r + 0.5) * IMGSIZE - h / 2),
                str(board_no), fill='#333333', font=fnt
            )
    title_fnt = ImageFont.truetype(
        os.path.join('font', 'NotoSansTC-Medium.otf'), 90
    )
    w, h = draw.textsize(title, font=title_fnt)
    draw.text(
        (COL * IMGSIZE / 2 - w / 2, (ROW + 0.5) * IMGSIZE - h / 2),
        title, fill='black', font=title_fnt
    )
    card_name_fnt = ImageFont.truetype(
        os.path.join('font', 'NotoSansTC-Medium.otf'), 30
    )
    w, h = draw.textsize(card_name, font=card_name_fnt)
    draw.text(
        (COL * IMGSIZE - w, (ROW + 0.5) * IMGSIZE - h / 2),
        card_name, fill='#999999', font=card_name_fnt
    )
    return Image.alpha_composite(back, front)


def _batch_gen(seqs):
    cards = []
    for i, seq in enumerate(seqs):
        # card_name = utils._num_to_str(i)
        card_name = str(i)
        cards.append(_gen_cardback(seq, card_name=card_name))
    return cards


def collate(inpath, outpath, dim=(2, 3), resolution=300,
            nrow=8, ncol=6, page_dim=(3, 3), PADDING=75,
            paper_size=(2480, 3508)):
    deals = []
    with open(inpath, 'r') as f:
        for i, line in enumerate(f.read().split('\n'), 1):
            try:
                deals.append(parse._parse_rbn(line))
            except ValueError as e:
                raise ValueError(f'Error in deal {i}: {e}')
    seqs = []
    for i in range(52):
        card = []
        for deal in deals:
            card.append(deal[i])
        seqs.append(card)
    imgs = _batch_gen(seqs)
    wratio = imgs[0].size[0] / (dim[0] * resolution)
    hratio = imgs[0].size[1] / (dim[1] * resolution)
    ratio = max(wratio, hratio)
    newsize = (int(imgs[0].size[0] / ratio), int(imgs[0].size[1] / ratio))
    resized_images = [img.resize(
        newsize, Image.ANTIALIAS).convert('RGB') for img in imgs]
    pdf_pages = []
    for i, img in enumerate(resized_images):
        c = i % page_dim[0]  # row of the image in pdf
        r = ((i - c) / page_dim[0]) % page_dim[1]  # column of the image in pdf
        if c == 0 and r == 0:
            # new page
            pdf_pages.append(Image.new('RGB', paper_size, color='white'))
        left_pad = (paper_size[0] - (page_dim[0] * newsize[0])
                    - (page_dim[0] - 1) * PADDING) / 2
        top_pad = (paper_size[1] - (page_dim[1] * newsize[1])
                   - (page_dim[1] - 1) * PADDING) / 2
        paste_loc = (int(left_pad + PADDING * c + newsize[0] * c),
                     int(top_pad + PADDING * r + newsize[1] * r))
        pdf_pages[-1].paste(img, paste_loc)

    pdf_pages[0].save(outpath, resolution=resolution, save_all=True,
                      append_images=pdf_pages[1:])
