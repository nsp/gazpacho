#!/usr/bin/python -tt
"""
    vidscraper.py
    @author: Nate Parsons
    @summary:
        vidscraper grabs the audio and slides from a URL and turns them into a 
        nice video.

"""

import os, re, sys, urllib

def usage():
    print "usage: vidscraper.py url outfile.avi"
    sys.exit(1)

if len(sys.argv) < 3:
    usage()

skipdl = False
if sys.argv[1] == '--skipdl':
    skipdl = True
    del(sys.argv[1])

url = sys.argv[1]
outfname = sys.argv[2]

if not skipdl:
    # fetch url
    page = urllib.urlopen(url)
    pagetxt = page.read()
    page.close()

    # Find the manifest.js
    manifesturl = re.findall(r'<script src="(.+manifest\.js.+)" ', pagetxt)[0]

    # fetch manifest.js
    page = urllib.urlopen(manifesturl)
    manifesttxt = page.read()
    page.close()

    # Grab Manifest.SlideBaseURL
    # Manifest.SlideBaseUrl="(url)";
    slidebaseurl = re.findall(r'Manifest\.SlideBaseUrl="(.+)";', manifesttxt)[0]

    # Grab Manifest.SlideImageFileNameTemplate
    # Manifest.SlideBaseFileNameTemplate="(tmpl)";
    slidenametmpl = re.sub(r'{0:D(\d)}',r'%0\1d', re.findall(r'Manifest.SlideImageFileNameTemplate="(\S+)";', manifesttxt)[0])

    # Grab Manifest.Title
    # Manifest.Title="(title)";
    title = re.findall(r'Manifest.Title="(.+)";', manifesttxt)[0]

    # Grab Manifest.Slides (grabbing the # and milliseconds of each one)
    # Store each slide as a tuple, (#, time)
    slides = map(lambda(x,y):(int(x),int(y)),re.findall(r'Manifest.Slides\[(\d+)\] = new Slide\("",(\d+),""\);', manifesttxt))

    # Get each slide
    if not os.path.exists('imgs'):
        os.mkdir('imgs')

    timings = open(os.path.join('imgs', 'timings.txt'), 'w')
    for slide in slides:
        urllib.urlretrieve((slidebaseurl+(slidenametmpl % (slide[0]))), os.path.abspath(os.path.join('imgs', ('%04d.jpg' % slide[0]))))
        timings.write('%04d, %09d\n' % slide)
    timings.close()

# end if not skipdl

# Put slides together into a video
