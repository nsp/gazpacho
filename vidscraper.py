#!/usr/bin/python -tt
"""
    vidscraper.py
    @author: Nate Parsons
    @summary:
        vidscraper grabs the audio and slides from a URL and turns them into a 
        nice video.

"""

import os, re, sys, urllib, time
import shlex, subprocess

def convert_to_vids(slides):
    # Convert it all
    mp4s = []
    pause = False
    for slide in slides:
        mp4 = os.path.abspath(os.path.join(outdir, '%04d.mp4' % slide[0]))
        if os.path.exists(mp4):
            mp4s.append(mp4)
            continue
        print '-------------------------------'
        out = open(os.path.abspath(os.path.join(outdir, '%04d.out' % slide[0])), 'w')
        err = open(os.path.abspath(os.path.join(outdir, '%04d.err' % slide[0])), 'w')
        dur = (duration - slide[1])/1000.
        if not slide[0]+1 >= len(slides):
            # slides[slide[0]] is the next slide, 
            # because slide #s start with 1, not 0
            dur = (float(slides[slide[0]][1])-float(slide[1]))/1000. 
        jpg = os.path.abspath(os.path.join(outdir, '%04d.jpg' % slide[0]))
        cmd ='ffmpeg -loop_input -t %f -r 24000/1001 -i %s -threads 0 -vcodec libx264 -crf 22 -vpre veryfast %s' % (dur, jpg, mp4)
        print cmd
        try:
            subprocess.check_call(shlex.split(cmd), stdout=out, stderr=err)
        except subprocess.CalledProcessError as cpe:
            print "Error in encoding slide %d, return code: %d" % (slide[0], cpe.returncode)
        out.close()
        err.close()
        print '-------------------------------'
        mp4s.append(mp4)
        time.sleep(sleeptime)
    return mp4s

def usage():
    print "usage: vidscraper.py [--fetch] url outdir sleeptime"
    sys.exit(1)

if len(sys.argv) < 4:
    usage()

fetch = False
if sys.argv[1] == '--fetch': 
    fetch = True
    del(sys.argv[1])

url = sys.argv[1]
outdir = sys.argv[2]
sleeptime = int(sys.argv[3])
startmp4 = int(sys.argv[4])

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

mp4s = convert_to_vids(slides)

# Concatenate it all
outmp4 = os.path.abspath(os.path.join(outdir, 'video.mp4'))
for i, mp4 in enumerate(mp4s):
    if i < startmp4: continue
    out = open(os.path.abspath(os.path.join(outdir, 'mp4-%04d.out' % i)), 'w')
    err = open(os.path.abspath(os.path.join(outdir, 'mp4-%04d.err' % i)), 'w')
    cmd = ['MP4Box']
    cmd.extend(['-cat', mp4])
    cmd.append(outmp4)
    print cmd
    subprocess.check_call(cmd, stdout=out, stderr=err)
    out.close()
    err.close()
    time.sleep(sleeptime/2)

    
