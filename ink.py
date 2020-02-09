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


def write_text(canvas, coord, text, font_files='Font.ttc'):

    # load fonts
    font24 = ImageFont.truetype('fonts/%s'%(font_files), 24)
    #font18 = ImageFont.truetype('fonts/%s'%(font_files), 18)

    try:
        # draw the font
        logging.info('draw text ...')
        draw = ImageDraw.Draw(canvas)
        
        # break the long string into sub-str 
        # that fits the canvas dim
        i = 0
        line_height = 26
        x,y = coord
        substr_list = text.split('\n')
        for substr in substr_list:
            draw.text((x,y), substr, font = font24, fill = 0)
            y += line_height

        time.sleep(2)

    except IOError as e:
        logging.info(e)
        

def write_image(canvas, coord, image_array):

    # draw the array as bitmap image
    try:
        logging.info("paint image array ...")
        bmp = Image.fromarray(image_array)
        canvas.paste(bmp, coord)

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
        write_image(canvas,(0,0),foo)

        # render text
        write_text(canvas, (280,150), "J.A.R.V.I.S")

        # display
        display(epd, canvas)


    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd.epdconfig.module_exit()
        exit()



