import os
import utils
import parse
from PIL import Image, ImageDraw, ImageFont


class CardBack:
    def __init__(self):
        self.title = ''
        self.seqs = []
        self.tiles_dim = (6, 8)
        self.color_palette = ['#DB8DAC', '#C7E889', '#F2CB8F', '#DB8DAC', '#D7D8F5', '#D1EBE1']
        self.IMGDIR = os.path.join('img', 'caret-up.png')
        self.card_dim = (2, 3)  # in inches
        self.collate_dim = (3, 3)  # arrangement on a page
        self.paper_dim = (2480, 3508)  # in pixels
        self.resolution = 300
        self.gap = 75  # gap between two cards (in pixel)
        self.IMGSIZE = 200
        self.color_backs = self.gen_color_backs()
        self.imgset = self.gen_image_set()

    def _coloring(self, r, c):
        return self.color_backs[(2 * r + c) % 5 + 1]

    def set_color_palette(self, color_palette):
        self.color_palette = color_palette
        self.color_backs = gen_color_backs()

    def gen_color_backs(self):
        return [Image.new('RGBA', (self.IMGSIZE, self.IMGSIZE), c) for c in self.color_palette]

    def gen_image_set(self):
        arrow = Image.open(self.IMGDIR)
        return [None] + [arrow.resize((self.IMGSIZE, self.IMGSIZE))
                         .rotate(-90 * i) for i in range(4)]

    def _gen_cardback(self, seq, card_name=''):
        '''seq: list. sequence of cards with length ROW * COL'''
        col, row = self.tiles_dim
        bg_color = self.color_palette[0]
        size = (col * self.IMGSIZE, (row + 1) * self.IMGSIZE)  # card size
        back = Image.new('RGBA', size, bg_color)
        front = Image.new('RGBA', size, '#00000000')
        fnt = ImageFont.truetype(os.path.join('font', 'NotoSansTC-Medium.otf'), 45)
        draw = ImageDraw.Draw(front)
        for c in range(col):
            for r in range(row):
                board_no = r * col + c + 1
                back.paste(self._coloring(r, c), (c * self.IMGSIZE, r * self.IMGSIZE))
                front.paste(self.imgset[seq[board_no - 1]], (c * self.IMGSIZE, r * self.IMGSIZE))

                w, h = draw.textsize(str(board_no), font=fnt)
                draw.text(
                    ((c + 0.5) * self.IMGSIZE - w / 2, (r + 0.5) * self.IMGSIZE - h / 2),
                    str(board_no), fill='#333333', font=fnt
                )
        title_fnt = ImageFont.truetype(
            os.path.join('font', 'NotoSansTC-Medium.otf'), 90
        )
        w, h = draw.textsize(self.title, font=title_fnt)
        draw.text(
            (col * self.IMGSIZE / 2 - w / 2, (row + 0.5) * self.IMGSIZE - h / 2),
            self.title, fill='black', font=title_fnt
        )
        card_name_fnt = ImageFont.truetype(
            os.path.join('font', 'NotoSansTC-Medium.otf'), 30
        )
        w, h = draw.textsize(card_name, font=card_name_fnt)
        draw.text(
            (col * self.IMGSIZE - w, (row + 0.5) * self.IMGSIZE - h / 2),
            card_name, fill='#999999', font=card_name_fnt
        )
        return Image.alpha_composite(back, front)

    def _batch_gen(self):
        cards = []
        for i, seq in enumerate(self.seqs):
            # card_name = utils._num_to_str(i)
            card_name = str(i)
            cards.append(self._gen_cardback(seq, card_name=card_name))
        return cards

    def collate(self, inpath, outpath, title):
        self.title = title
        deals = []
        with open(inpath, 'r') as f:
            for i, line in enumerate(f.read().split('\n'), 1):
                try:
                    deals.append(parse._parse_rbn(line))
                except ValueError as e:
                    raise ValueError(f'Error in deal {i}: {e}')
        for i in range(52):
            card = []
            for deal in deals:
                card.append(deal[i])
            self.seqs.append(card)
        imgs = self._batch_gen()
        wratio = imgs[0].size[0] / (self.card_dim[0] * self.resolution)
        hratio = imgs[0].size[1] / (self.card_dim[1] * self.resolution)
        ratio = max(wratio, hratio)
        newsize = (int(imgs[0].size[0] / ratio), int(imgs[0].size[1] / ratio))
        resized_images = [img.resize(
            newsize, Image.ANTIALIAS).convert('RGB') for img in imgs]
        pdf_pages = []
        left_pad = int((self.paper_dim[0] - (self.collate_dim[0] * newsize[0])
                       - (self.collate_dim[0] - 1) * self.gap) / 2)
        top_pad = int((self.paper_dim[1] - (self.collate_dim[1] * newsize[1])
                      - (self.collate_dim[1] - 1) * self.gap) / 2)
        for i, img in enumerate(resized_images):
            c = i % self.collate_dim[0]  # row of the image in pdf
            r = ((i - c) / self.collate_dim[0]) % self.collate_dim[1]  # column of the image in pdf
            if c == 0 and r == 0:
                # new page
                pdf_pages.append(Image.new('RGB', self.paper_dim, color='white'))
            paste_loc = (int(left_pad + self.gap * c + newsize[0] * c),
                         int(top_pad + self.gap * r + newsize[1] * r))
            pdf_pages[-1].paste(img, paste_loc)

        pdf_pages[0].save(outpath, resolution=self.resolution, save_all=True,
                          append_images=pdf_pages[1:])
