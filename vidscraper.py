#!/usr/bin/python -tt
"""
    vidscraper.py
    @author: Nate Parsons
    @summary:
        vidscraper grabs the audio and slides from a URL and turns them into a 
        nice video.

"""

import os, urllib

def usage():
    print "usage: vidscraper.py url outfile.avi"
    sys.exit(1)

if len(sys.argv) < 3:
    usage()

url = argv[1]
outfname = argv[2]

# fetch url

# Find the manifest.js

# fetch manifest.js

# Grab Manifest.SlideBaseURL
# Grab Manifest.SlideImageFileNameTemplate
# Grab Manifest.Title
# Grab Manifest.Slides (grabbing the # and milliseconds of each one)

# Get each slide

# Put slides together into a video
