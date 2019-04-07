import os
import logging
SUPPORTS_IMG_PROTOCOL = True
SUPPORTS_TRUE_COLORS = True
SUPPORTS_ASCII_COLORS = True


def has_img_protocol_support():
    return SUPPORTS_IMG_PROTOCOL

def set_img_protocol_support(is_available):
    global SUPPORTS_IMG_PROTOCOL
    SUPPORTS_IMG_PROTOCOL = is_available

def has_true_color_support():
    return SUPPORTS_TRUE_COLORS

def set_true_color_support(is_available):
    global SUPPORTS_TRUE_COLORS
    SUPPORTS_TRUE_COLORS = is_available

def has_ascii_color_support():
    return SUPPORTS_ASCII_COLORS

def set_ascii_color_support(is_available):
    global SUPPORTS_ASCII_COLORS
    SUPPORTS_ASCII_COLORS = is_available

def _set_img_support_level(level):
    set_ascii_color_support(level > 0)
    set_true_color_support(level > 1)
    set_img_protocol_support(level > 2)

def guess_terminal_support():
    img_support_levels_by_terminal_id = {
        'iTerm.app': 3,
        'Apple_Terminal': 2,
    }
    terminal_id = os.environ.get('TERM_PROGRAM', 'unknown')
    warnings_by_terminal_id = {
        'Apple_Terminal': "Apple terminal is not recommended for image visualisation. Use iTerm2.",
        'unknown': "Could not recognise terminal, may not have full image support. Recommended to use iTerm2."
    }
    if terminal_id in warnings_by_terminal_id:
        logging.warning(warnings_by_terminal_id[terminal_id])
    img_support_level = img_support_levels_by_terminal_id.get(terminal_id, 3)
    _set_img_support_level(img_support_level)

guess_terminal_support()