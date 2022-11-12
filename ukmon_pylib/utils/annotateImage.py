#
# annotate an image with station info and meteor count
#

from PIL import Image, ImageFont, ImageDraw 
import sys
import datetime


def annotateImage(img_path, title, metcount):
    my_image = Image.open(img_path)
    width, height = my_image.size
    image_editable = ImageDraw.Draw(my_image)
    fntheight=30
    try:
        fnt = ImageFont.truetype("arial.ttf", fntheight)
    except:
        fnt = ImageFont.truetype("DejaVuSans.ttf", fntheight)
    #fnt = ImageFont.load_default()
    image_editable.text((15,height-fntheight-15), title, font=fnt, fill=(255))
    metmsg = 'meteors: {:04d}'.format(metcount)
    image_editable.text((width-7*fntheight-15,height-fntheight-15), metmsg, font=fnt, fill=(255))
    my_image.save(img_path)


def annotateImageArbitrary(img_path, message, color='#000'):
    my_image = Image.open(img_path)
    width, height = my_image.size
    image_editable = ImageDraw.Draw(my_image)
    fntheight=30
    try:
        fnt = ImageFont.truetype("arial.ttf", fntheight)
    except:
        fnt = ImageFont.truetype("DejaVuSans.ttf", fntheight)
    #fnt = ImageFont.load_default()
    image_editable.text((15,height-fntheight-15), message, font=fnt, fill=color)
    my_image.save(img_path)


if __name__ == '__main__':
    statid = sys.argv[2]
    if len(sys.argv) > 3:
        if len(sys.argv[4]) > 6:
            now = datetime.datetime.strptime(sys.argv[4], '%Y%m%d')
            title = '{} {}'.format(statid, now.strftime('%Y-%m-%d'))
        else:
            now = datetime.datetime.strptime(sys.argv[4], '%Y%m')
            title = '{} {}'.format(statid, now.strftime('%Y-%m'))
    else:
        now = datetime.datetime.now()
        title = '{} {}'.format(statid, now.strftime('%Y-%m-%d'))
    annotateImage(sys.argv[1], title, int(sys.argv[3]))
