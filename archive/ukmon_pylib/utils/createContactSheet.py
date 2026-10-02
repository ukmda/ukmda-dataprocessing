#
# Create a contact sheet from a set of images
#
# Copyright (C) 2018- Mark McIntyre

from PIL import Image
import glob
import boto3
import os
from tempfile import mkdtemp
import shutil
import math


def generateContacts(dtstr, outdir=None, lat=None, lon=None, gcdist=None):
    # get a list of objects to create a contact sheet from

    buck = 'ukmda-website'
    pref = f'reports/{dtstr[:4]}/orbits/{dtstr[:6]}/{dtstr}'

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(buck)
    files = [os.key for os in bucket.objects.filter(Prefix=pref)]
    reqfiles = [x for x in files if '_ground_track' in x and 'OSM' not in x]

    tmpdir = mkdtemp()
    for fil in reqfiles:
        s3.meta.client.download_file(buck, fil, os.path.join(tmpdir, os.path.basename(fil)))

    fnames = glob.glob('*_ground_track.png', root_dir=tmpdir)

    csimage = makeContactSheet([f'{tmpdir}/{x}' for x in fnames])

    if outdir is None:
        outdir = os.getenv('TEMP')
    outfname = f'{outdir}/{dtstr}_contact.png'
    csimage.save(outfname)
    shutil.rmtree(tmpdir)
    return 

def makeContactSheet(fnames,rowscols=[10,100],photodims=(240,240), margins=[10,10,10,10], padding=10):
    """\
    Make a contact sheet from a group of filenames:

    fnames       A list of names of the image files    
    rowscols     [cols, rows] number of images per row and column
    photodims    (width, height) of each individual image
    margins      [left, top, right, bottom] margins in pixels
    padding      The padding between images in pixels

    returns a PIL image object.
    """

    # Read in all images and resize appropriately
    imgs = [Image.open(fn).resize(photodims) for fn in fnames]

    # Calculate the size of the output image, based on the
    #  photo thumb sizes, margins, and padding
    marw = margins[0]+margins[2]
    marh = margins[1]+ margins[3]

    maxrows = math.ceil(len(fnames)/rowscols[0])
    padw = (rowscols[0]-1)*padding
    padh = (maxrows-1)*padding
    isize = (rowscols[0]*photodims[0] + marw + padw ,maxrows*photodims[1] + marh + padh)
    # Create the new image. The background doesn't have to be white
    white = (255,255,255)
    inew = Image.new('RGB',isize,white)
    # Insert each thumb:
    for irow in range(maxrows):
        for icol in range(rowscols[0]):
            left = margins[0] + icol*(photodims[0] + padding)
            right = left + photodims[0]
            upper = margins[1] + irow*(photodims[1]+padding)
            lower = upper + photodims[1]
            bbox = (left,upper,right,lower)
            try:
                img = imgs.pop(0)
            except:
                break
            inew.paste(img,bbox)
    return inew