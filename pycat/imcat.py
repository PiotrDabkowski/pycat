from PIL import Image
import numpy as np
import os
import sys
import base64
import cStringIO
from xterm_colors import rgb_to_cmd
import config


def iTerm_protocol_encode(pil_image, h_fraction=0.5):
    buffer = cStringIO.StringIO()
    pil_image.save(buffer, format="JPEG")

    img_str = base64.b64encode(buffer.getvalue())
    beg = u'\u001B]1337;File=inline=1;height=%d%%;preserveAspectRatio=1:' % int(h_fraction*100)

    return  beg + img_str + u'\u0007\n'



SPACE_H_TO_W_RATIO = 34. / 14.
TOP_FRAC = 19. / 36.
BOTTOM_FRAC = 2./ 36.

class PrintableImage:
    def __init__(self, path_or_pil_or_uint_rgb_arr, full_width=False, use_h_res_augmentation_method=True):
        self.full_width = full_width
        self.use_h_res_augmentation_method = use_h_res_augmentation_method
        if isinstance(path_or_pil_or_uint_rgb_arr, basestring):
            self.im = Image.open(path_or_pil_or_uint_rgb_arr)
        elif isinstance(path_or_pil_or_uint_rgb_arr, Image.Image):
            self.im = path_or_pil_or_uint_rgb_arr
        elif isinstance(path_or_pil_or_uint_rgb_arr, np.ndarray):
            self.im = Image.fromarray(path_or_pil_or_uint_rgb_arr)
        else:
            raise TypeError('invalid type of path_or_pil_or_uint_rgb_arr')



    def show(self):
        try:
            rows, cols = map(int, os.popen('stty size', 'r').read().split())
        except:
            raise ValueError('Not a terminal, please run from a terminal!')
        if config.has_img_protocol_support():
            sys.stdout.write(iTerm_protocol_encode(self.im))
            sys.stdout.flush()
            sys.stdout.write('\n')
            sys.stdout.flush()
            return


        available_ar = float(SPACE_H_TO_W_RATIO*rows)/cols
        requested_ar = float(self.im.size[1])/ self.im.size[0]


        if requested_ar > available_ar and not self.full_width:
            # limited by h
            pr_rows = rows
            pr_cols = int(round(pr_rows/requested_ar*SPACE_H_TO_W_RATIO))
        else:
            # limited by w
            pr_cols = cols
            pr_rows = int(round(pr_cols*requested_ar/SPACE_H_TO_W_RATIO))


        if not self.im.size[0] < 2*pr_cols or True:
            new_w = 2*pr_cols
            new_h = int(round(requested_ar*new_w))
            base_im = self.im.resize((new_w, new_h), resample=Image.BILINEAR)
        else:
            base_im = self.im

        w, h = map(float, base_im.size)
        pixels = np.array(base_im)

        x_step, y_step = int(w/pr_cols), int(h/pr_rows)
        y_top_step = int(round(TOP_FRAC*y_step))

        for r in range(pr_rows):
            for c in range(pr_cols):
                sample_y, sample_x = int(round(h*r/pr_rows)), int(round(w*c/pr_cols))
                a, b, c = sample_y, sample_y + y_top_step, sample_y + y_step
                if self.use_h_res_augmentation_method:
                    _top_rgb = np.mean(pixels[a:b, sample_x:sample_x+x_step], axis=(0,1))
                    bottom_rgb = np.mean(pixels[b:c, sample_x:sample_x+x_step], axis=(0,1))
                    top_rgb = (TOP_FRAC*_top_rgb+BOTTOM_FRAC*bottom_rgb)/(TOP_FRAC+BOTTOM_FRAC)
                    term = rgb_to_cmd(bottom_rgb, top_rgb)
                else:
                    rgb = np.mean(pixels[a:c, sample_x:sample_x+x_step], axis=(0,1))
                    term = rgb_to_cmd(rgb)
                sys.stdout.write(term)
            sys.stdout.write(rgb_to_cmd(-1)+'\n')

        sys.stdout.write(rgb_to_cmd(-1))



def show(path_or_pil_or_uint_rgb_arr):
    PrintableImage(path_or_pil_or_uint_rgb_arr).show()

if __name__=='__main__':
    show(os.path.join(os.path.dirname(__file__), 'test.jpg'))
