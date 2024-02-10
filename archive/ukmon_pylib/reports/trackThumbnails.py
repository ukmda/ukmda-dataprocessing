import pandas as pd
from PIL import Image, ImageFont, ImageDraw, ImageOps
import os
import random
import datetime
import shutil
import argparse
import requests
from tempfile import mkdtemp
from meteortools.utils import greatCircleDistance

RAD2DEG=57.2958


def getFilteredEvents(sdtstr, edtstr, obslat, obslng, maxdist=100):
    pqfile = f'https://archive.ukmeteors.co.uk/browse/parquet/matches-full-{sdtstr[:4]}.parquet.snap'
    df = pd.read_parquet(pqfile, columns=['_localtime', '_lat1', '_lng1', 'img','dtstamp'])
    # filter by date
    stdt = datetime.datetime.strptime(sdtstr, '%Y%m%d')
    eddt = datetime.datetime.strptime(edtstr, '%Y%m%d')
    df = df[df.dtstamp >= stdt.timestamp()]
    df = df[df.dtstamp < eddt.timestamp()]
    # filter by location
    df['gsdist'] = df.apply(lambda x: greatCircleDistance(obslat/RAD2DEG, obslng/RAD2DEG, x._lat1/RAD2DEG, x._lng1/RAD2DEG), axis=1)
    df = df[df.gsdist <= maxdist]
    df['img'] = df.img.str.replace('ukmeteornetwork.co.uk','ukmeteors.co.uk')
    return list(df.img)


def getGroundTracks(imgs, outdir):
    localfs = []
    for img in imgs:
        fname = os.path.join(outdir, os.path.split(img)[1])
        get_response = requests.get(img, stream=True)
        with open(fname, 'wb') as f:
            for chunk in get_response.iter_content(chunk_size=4096):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        localfs.append(fname)
    return localfs


def generateThumbnail(image_path, output_dir, thumbnail_size):
    image = Image.open(image_path)
    fname = os.path.split(image_path)[1]
    dtstr = fname[:15]
    # Center square crop
    width, height = image.size
    if width > height:
        left = (width - height) // 2
        right = left + height
        top = 0
        bottom = height
    else:
        top = (height - width) // 2
        bottom = top + width
        left = 0
        right = width
    image = image.crop((left, top, right, bottom))
    image = ImageOps.expand(image, border=20, fill=(255,255,255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("FONTS/arial.ttf", 72)
    draw.text((0,bottom-30),dtstr,(0,0,0), font=font)
    image.thumbnail(thumbnail_size)
    image.save(os.path.join(output_dir, os.path.basename(image_path)))
    return 


def createContactSheet(image_paths, output_file, img_size=0, shuffle=False, thumbsize=100, sheetwidth=10):
    if img_size == 0:
        img_size = len(image_paths)
    # Create the output directory for thumbnails
    output_dir = "c:/temp/thumbnails"
    os.makedirs(output_dir, exist_ok=True)
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir,f))

    # Use multiprocessing to generate thumbnails
    thumbnail_size = (thumbsize, thumbsize)  # Adjust the size as per your requirement
    results = []
    for image_path in image_paths[0:img_size]:
        results.append(generateThumbnail(image_path, output_dir, thumbnail_size))
    # Create the contact sheet
    thumbnails = [Image.open(os.path.join(output_dir, file)) for file in os.listdir(output_dir)]
    if shuffle:    
        random.shuffle(thumbnails)
    num_thumbnails = len(thumbnails)
    contact_sheet_width = int(num_thumbnails**0.5)  # Number of thumbnails per row
    contact_sheet_width = sheetwidth
    contact_sheet_height = (num_thumbnails // contact_sheet_width) + (num_thumbnails % contact_sheet_width > 0)
    # Calculate the square size based on the contact sheet dimensions
    thumbnail_size = max(thumbnail_size)
    square_size = (thumbnail_size * contact_sheet_width, thumbnail_size * contact_sheet_height)
    contact_sheet = Image.new("RGB", square_size)
    x_offset, y_offset = 0, 0
    for thumbnail in thumbnails:
        contact_sheet.paste(thumbnail, (x_offset, y_offset))
        x_offset += thumbnail_size
        if x_offset >= thumbnail_size * contact_sheet_width:
            x_offset = 0
            y_offset += thumbnail_size
    # Save the contact sheet
    contact_sheet.save(output_file)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="""Plot a ground map of many detections.""",
        formatter_class=argparse.RawTextHelpFormatter)

    arg_parser.add_argument('start_date', type=str, help='start date in yyyymmdd format')
    arg_parser.add_argument('end_date', type=str, help='end date in yyyymmdd format')
    #arg_parser.add_argument('-i', '--stationid', metavar='STATID', help='Station id eg UK0006')
    #arg_parser.add_argument('-m', '--minmag', metavar='MINMAG', type=float, help='Minimum magnitude to filter for')
    arg_parser.add_argument('-l', '--obs_lat', metavar='OBSLAT', help='Observer latitude (degrees')
    arg_parser.add_argument('-g', '--obs_lon', metavar='OBSLON', help='Observer longitude (degrees)')
    arg_parser.add_argument('-d', '--event_distance', metavar='EVTDIST', help='Distance from observer (km)')
    arg_parser.add_argument('-o', '--outdir', metavar='OUTDIR', help='Location to save jpg into')

    cml_args = arg_parser.parse_args()
    if not cml_args.obs_lat or not cml_args.obs_lon or not cml_args.event_distance:
        print('if providing an observer latitude, must also supply longitude and distance')
        exit(0)
    else:
        obslat = float(cml_args.obs_lat)
        obslng = float(cml_args.obs_lon)
        evtdist = float(cml_args.event_distance)
    outdir = cml_args.outdir
    if not outdir:
        outdir = '.'
    events = getFilteredEvents(cml_args.start_date,cml_args.end_date,obslat, obslng, maxdist=evtdist)
    tmpdir = mkdtemp()
    tracks = getGroundTracks(events, tmpdir)
    outfname = os.path.join(outdir, f'trackthumbs-{cml_args.start_date}-{cml_args.end_date}.png')
    createContactSheet(tracks, outfname, thumbsize=300, sheetwidth=5)
    shutil.rmtree(tmpdir)
