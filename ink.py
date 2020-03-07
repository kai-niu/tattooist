#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys

import logging
from lib.waveshare_epd import epd7in5
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import numpy as np


def init_epd(epd, clear=False, verbose=logging.DEBUG):
     # set the debug level
    logging.basicConfig(level=verbose)

    try:
        # init the epaper
        logging.info('init the canvas ...')
        epd.init()
        if clear:
            logging.info('clear the canvas ...')
            epd.Clear()

        return Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame

    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd.epdconfig.module_exit()
        exit()


###
#
# render image box widget
#
###
def render_image(canvas, image_array, coord, resize='aspect', rotate=0, padding=0, outline=0):
    '''
    @param::canvas: the PIL image canvas
    @param::image_array: the numpy image array
    @param::coord: the user coordiantes of image box
    @param::resize: the resize method: aspect/fill/crop
    @param::rotate: rotate the image counter clockwise. The rotation happens before the resize.
    @param::padding: the padding around the image
    @param::outline: the width of box outline
    return none
    '''
    # translate the coordinate
    x,y,w,h = coord
    row,col = image_array.shape
    outline_coord = (x,y,x+w,y+h)
    x = x + padding
    y = y + padding
    w = w - padding*2
    h = h - padding*2
    crop_box = (0,0,min(w,col),min(h,row))
    # convert to image object
    bmp = Image.fromarray(image_array)
    # rotate
    if rotate != 0:
        bmp = bmp.rotate(rotate)
    # resize
    if resize == 'fill':
        bmp = bmp.resize((w,h))
    elif resize == 'crop':
        bmp = bmp.crop(crop_box)
    else:
        bmp.thumbnail((w,h))
    # paint
    if outline > 0:
        draw_rect(canvas, outline_coord, outline=outline)
    draw_image(canvas, bmp, (x,y))
    
###
#
# render text box widget
#
###
def render_text_box(canvas, text, coord, outline=1, font_size=16, line_padding=2, font_face='UbuntuMono-Regular.ttf'):
    '''
    @param::canvas: the PIL canvas object
    @param::text: the text content
    @param::coord: the user coordinates of textbox x,y,w,h
    @param::outline: the border width
    @param::font_size: the size of the font
    @param::line_padding: the paddings around each text line
    @param::font_face: the font face
    return none
    '''
    # translate the coord
    # the inner coord system is left-upper point (x1,y1) - bottom-right point (x2,y2)
    # the user coord is (x,y,w,h)
    x,y,w,h = coord
    rect_coord = (x,y,x+w,y+h)
    text_coord = (x+line_padding, y+line_padding, w-line_padding*2, h-line_padding*2)
    # draw rect box
    draw_rect(canvas, rect_coord, outline=outline)
    # write text inside of box
    write_text(canvas, text, text_coord, font_size=font_size, line_padding=line_padding, font_face=font_face)

###
#
# left aign and fit the text into the rectangle specified by width and height
# 
###
def fit_text(text, font_size, width, height, line_padding=2):
    '''
    @param::text: the input text string
    @param::font_size: the size of the font face
    @param::width: the width of the text box
    @param::height: the height of the text box
    @param::line_padding: the padding around the each text line
    return the list of text line
    '''
    max_line_len = width//(font_size * 0.5)
    max_num_lines = height//(font_size + line_padding)
    substrs = []
    line_num_count = 0
    line_len_count = 0
    tokens = text.split(' ')
    tmpstr = []
    for t in tokens:
        if line_num_count >= max_num_lines:
            break
        elif line_len_count + len(t) <= max_line_len:
            tmpstr.append(t)
            line_len_count = line_len_count + len(t) + 1
        else:
            substrs.append(' '.join(tmpstr))
            tmpstr = [t]
            line_len_count = len(t) + 1
            line_num_count += 1

    return substrs
        
def write_text(canvas, text, coord, font_size=16, line_padding=2, font_face='UbuntuMono-Regular.ttf'):

    # load fonts
    font = ImageFont.truetype('fonts/%s'%(font_face), font_size)

    try:
        # draw the font
        logging.info('draw text ...')
        draw = ImageDraw.Draw(canvas)
        
        # break the long string into sub-str 
        # that fits the canvas dim
        x,y,w,h = coord
        substr_list = fit_text(text,font_size,w,h, line_padding=line_padding)
        for substr in substr_list:
            draw.text((x,y), substr, font = font, fill = 0)
            y += font_size + line_padding

    except IOError as e:
        logging.info(e)

def draw_image(canvas, image, coord):

    # draw the array as bitmap image
    try:
        logging.info("paint image array at coord: %s,%s ..."%(coord))
        canvas.paste(image, coord)

    except IOError as e:
        logging.info(e)

def draw_rect(canvas, coord, outline = 1):
    x,y,w,h = coord
    try:
        logging.info("draw rect ...")
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((x, y, w, h), outline = outline)

    except IOError as e:
        logging.info(e)

def display(epd, canvas):
    try:
        epd.display(epd.getbuffer(canvas))
        time.sleep(2)

    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd.epdconfig.module_exit()
        exit()


if __name__ == '__main__':

    try:
        # init epd
        epd = epd7in5.EPD()
        canvas = init_epd(epd)

        # render image
        im = Image.open('misc/wow.jpg').convert('L').resize((640,384))
        foo = np.array(im, dtype = np.uint8)
        render_image(canvas, foo, (310,8,300,300), resize='crop', padding=3, outline=1)
        render_image(canvas, foo, (210,8,95,200), rotate=-90, resize='aspect', padding=2, outline=1)

        # render text box
        text = u"The noble Paladin, Tirion Fordring, had always believed the savage Orcs to be vile and corrupt. He had spent his life fighting ceaselessly to protect humanity from their foul treachery. But an unexpected act of honor and compassion sets in motion a chain of events that will challenge Tirion's most fundamental beliefs, and force him to decide once and for all who are the men -- and who are the monsters."
        render_text_box(canvas, text, (8,8,200,200), font_size=10)
        render_text_box(canvas, text, (8,210,300,150), font_size=26)

        # display
        display(epd, canvas)

        #foo = fit_text(text, 16, 300, 300)
        #for f in foo:
        #    print(f)


    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd.epdconfig.module_exit()
        exit()




