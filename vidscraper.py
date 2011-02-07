#!/usr/bin/python -tt
"""
    vidscraper.py
    @author: Nate Parsons
    @summary:
        vidscraper grabs the audio and slides from a URL and turns them into a 
        nice video.

"""

import os, re, sys, urllib
import shlex, subprocess

def usage():
    print "usage: vidscraper.py [--fetch] url outdir"
    sys.exit(1)

if len(sys.argv) < 3:
    usage()

fetch = False
if sys.argv[1] == '--fetch': 
    fetch = True
    del(sys.argv[1])

url = sys.argv[1]
outdir = sys.argv[2]

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

# Grab Manifest.Duration
# Manifest.Duration=(duration);
duration = int(re.findall(r'Manifest.Duration=(\d+);', manifesttxt)[0])

# Grab Manifest.Slides (grabbing the # and milliseconds of each one)
# Store each slide as a tuple, (#, time)
slides = map(lambda(x,y):(int(x),int(y)),re.findall(r'Manifest.Slides\[(\d+)\] = new Slide\("",(\d+),""\);', manifesttxt))

# Set the first slide to 000000000
slides[0] = (0,0)

# Increment the # of each slide
slides = map(lambda(s):(s[0]+1,s[1]), slides)

# Don't fetch images if we already have them
if fetch:
    # Get each slide
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # Write it all out
    timings = open(os.path.join(outdir, 'timings.txt'), 'w')
    for slide in slides:
        urllib.urlretrieve((slidebaseurl+(slidenametmpl % (slide[0]))), os.path.abspath(os.path.join(outdir, ('%04d.jpg' % slide[0]))))
        timings.write('%04d, %09d\n' % slide)
    timings.close()

# Convert it all
mp4s = []
for slide in slides:
    out = open(os.path.abspath(os.path.join(outdir, '%04d.out' % slide[0])), 'w')
    err = open(os.path.abspath(os.path.join(outdir, '%04d.err' % slide[0])), 'w')
    dur = (duration - slide[1])/1000.
    if not slide[0]+1 >= len(slides):
        dur = (float(slides[slide[0]+1][1])-float(slide[1]))/1000.
    jpg = os.path.abspath(os.path.join(outdir, '%04d.jpg' % slide[0]))
    mp4 = os.path.abspath(os.path.join(outdir, '%04d.mp4' % slide[0]))
    if os.path.exists(mp4):
        os.remove(mp4)
    cmd ='time -v ffmpeg -loop_input -t %f -i %s -r 24000/1001 -vcodec libx264 -crf 22 -vpre veryfast %s' % (dur, jpg, mp4)
    print cmd
    try:
        subprocess.check_call(shlex.split(cmd), stdout=out, stderr=err)
    except subprocess.CalledProcessError as cpe:
        print "Error in encoding slide %d, return code: %d" % (slide[0], cpe.returncode)
    else:
        out.close()
        err.close()
        mp4s.append(mp4)


# Concatenate it all
intermediate = os.path.abspath(os.path.join(outdir, 'video.mp4'))
if os.path.exists(intermediate):
    os.remove(intermediate)
chunksize = 19
for i, chunk in enumerate(mp4s[x:x+chunksize] for x in range(0, len(mp4s), chunksize)):
    out = open(os.path.abspath(os.path.join(outdir, 'mp4-%04d.out' % i)), 'w')
    err = open(os.path.abspath(os.path.join(outdir, 'mp4-%04d.err' % i)), 'w')
    cmd = ['time', '-v', 'MP4Box']
    if os.path.exists(intermediate):
        cmd.extend(['-cat', intermediate])
    for f in chunk:
        cmd.extend(['-cat', f])
    cmd.append(intermediate)
    print cmd
    try:
        subprocess.call_check(cmd, stdout=out, stderr=err)
    except subprocess.CalledProcessError as cpe:
        print "Error in encoding slide %d, return code: %d" % (slide[0], cpe.returncode)
    else:
        out.close()
        err.close()

    
