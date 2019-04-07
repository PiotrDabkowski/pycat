import os
import sys
import base64
import io
import logging

from PIL import Image
import numpy as np

from . import config
from .xterm_colors import rgb_to_cmd



def iTerm_protocol_encode(pil_image, h_fraction=0.5):
    with io.BytesIO() as buffer:
        pil_image.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    beg = u'\u001B]1337;File=inline=1;height=%d%%;preserveAspectRatio=1:' % int(h_fraction*100)

    return  beg + img_str + u'\u0007\n'



SPACE_H_TO_W_RATIO = 34. / 14.
TOP_FRAC = 19. / 36.
BOTTOM_FRAC = 2./ 36.

class PrintableImage:
    def __init__(self, path_or_pil_or_np_array, full_width=False, use_h_res_augmentation_method=True):
        self.full_width = full_width
        self.use_h_res_augmentation_method = use_h_res_augmentation_method
        if isinstance(path_or_pil_or_np_array, str):
            self.im = Image.open(path_or_pil_or_np_array)
        elif isinstance(path_or_pil_or_np_array, Image.Image):
            self.im = path_or_pil_or_np_array
        elif isinstance(path_or_pil_or_np_array, np.ndarray):
            arr = _to_correct_shape_arr(_to_uin8_arr(path_or_pil_or_np_array))
            self.im = Image.fromarray(arr)
        else:
            raise TypeError('invalid type of path_or_pil_or_uint_rgb_arr')



    def show(self):
        try:
            rows, cols = list(map(int, os.popen('stty size', 'r').read().split()))
        except:
            rows, cols = 20, 80
            logging.warning("Could not get terminal specs, image may not show properly.")
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

def _to_uin8_arr(x):
    if x.dtype == np.uint8:
        return x
    # try to guess the format...
    low = np.min(x)
    high = np.max(x)
    if low < 0 or high > 255:
        return np.asarray((x - low) / (high - low + 1e-3) * 255, np.uint8)
    elif low >= 0 and high <= 1:
        return np.asarray(x * 255, np.uint8)
    else:
        return np.asarray(x, np.uint8)

def _to_correct_shape_arr(x):
    if len(x.shape) == 3:
        if 3 in x.shape:
            idx = x.shape.index(3)
        elif 1 in x.shape:
            idx = x.shape.index(1)
        else:
            raise ValueError("Invalid array shape %s" % x.shape)
        if idx != 2:
            if idx == 0:
                order = [1, 2, 0]
            else:
                assert idx == 1
                order = [0, 2, 1]
            x = np.transpose(x, order)
    elif len(x.shape) == 2:
        x = np.expand_dims(x, 2)
    else:
        raise ValueError("Invalid array shape %s" % x.shape)
    if x.shape[-1] == 3:
        return x
    elif x.shape[-1] == 1:
        return np.concatenate((x, x, x), axis=2)
    else:
        raise ValueError("Invalid array shape %s" % x.shape)


def show(path_or_pil_or_np_array):
    """Shows the image if the terminal supports image protocol / colors.

    path_or_pil_or_uint_rgb_arr can be:
        string: a path to the image to show
        np.array: a numpy array with the image data. Ideally should be [H, W, 3] and with np.uint8 dtype. But can be also 2D (in such case the image will be gray).
            dtypes other than uint8 are supported as well and in such case we will do the best job to determine the range of data, no guarantees though.
            [H, W, 3], [H, W, 1], [H, W], [3, H, W], [1, H, W] are supported shapes.
        pil.Image: a pil.Image object
    """
    PrintableImage(path_or_pil_or_np_array).show()

if __name__=='__main__':
    show(os.path.join(os.path.dirname(__file__), 'test.jpg'))
