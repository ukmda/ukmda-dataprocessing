# Copyright (C) Mark McIntyre

# python script to forward email

from meteortools.utils import forwardAnEmail
import os


def forwardFromSource(recipfile, tokfile, crdfile):
    if not os.path.isfile(recipfile):
        print('unable to open recipient list')
        return False
    lis = open(recipfile, 'r').readlines()
    recips=[]
    for li in lis:
        recips.append(li.strip())
    print(f'forwarding to {recips}')
    #print(tokfile, crdfile)
    forwardAnEmail(recips, tokfile=tokfile, crdfile=crdfile)
    return True
