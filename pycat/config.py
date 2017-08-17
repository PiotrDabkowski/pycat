SUPPORTS_IMG_PROTOCOL = True
SUPPORTS_TRUE_COLORS = True
SUPPORTS_ASCII_COLORS = True


def has_img_protocol_support():
    return SUPPORTS_IMG_PROTOCOL

def has_true_color_support():
    return SUPPORTS_TRUE_COLORS

def has_ascii_color_support():
    return SUPPORTS_ASCII_COLORS