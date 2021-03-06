#!/usr/bin/env python
import subprocess
import json
import argparse
import sys
import os


class VideoFile:
    def __init__(self, path):
        self.path = path
        self.duration = get_duration(path)


def get_duration(path):
    p = subprocess.Popen('ffprobe -v quiet -show_format \'%s\' -print_format json' % path,
                         shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    ffp_output = ''.join(p.stdout.readlines())
    json_data = json.loads(ffp_output)
    return float(json_data['format']['duration'])

def get_args():
    parser = argparse.ArgumentParser(description='Automatically take screenshots.')

    parser.add_argument('-s', dest='num_shots', type=int,
                        metavar='number_of_screenshots', default=20,
                        help='Number of screenshot to take per file (default: 20)')
    parser.add_argument('-d', dest='destination', type=str,
                        metavar='save_directory', default='sshot',
                        help='Save directory (default: sshot)')
    parser.add_argument('-p', dest='padding', type=int, metavar='P',
                        help='Number of zeros to pad the file names with (default: 3)'
                        , default=3)
    parser.add_argument('--delim', type=str, default='_',
                        help='Delimiter for use with --flat (default: _)')
    parser.add_argument('--flat', action='store_true',
                        help='Put all screenshots in same destination',)
    parser.add_argument('--keep-exts', dest='exts', action='store_true',
                        help='Keep file extensions with all file names')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--grind', action='store_true',
                        help='Doesn\'t wait for children to finish causing CPU and I/O grind')
    parser.add_argument('files', type=str, metavar='files',
                        nargs='+', help='videos to screenshot')


    args = parser.parse_args()
    return args


def take_screenshots(args, video):
    if args.verbose: print "Now processing %s" % video.path
    cmd = 'ffmpeg -ss %s -y -i \'%s\' -f image2 -vframes 1 \'%s.png\''
    interval = video.duration / args.num_shots
    filename = None
    destination = args.destination

    t_p = os.path.split(video.path)[1]
    filename = t_p if args.exts else os.path.splitext(t_p)[0]

    if not args.flat:
        nested_d = os.path.join(args.destination, filename)
        make_dir(nested_d)
        destination = nested_d

    for i in range(1, args.num_shots + 1):
        if args.verbose: print "Taking screenshot %d/%d" % (i, args.num_shots)
        f_dest = os.path.join(destination, str(i).zfill(args.padding))
        if args.flat:
            f_dest = os.path.join(destination, filename + '_' + str(i).zfill(args.padding))

        p_cmd = cmd % (str(interval * i), video.path, f_dest)
        p = subprocess.Popen(p_cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        if not args.grind:
            p.wait()
        if args.debug: print ''.join(p.stdout.readlines())

def make_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

def extract_subtitles(args, video):
    cmd = 'ffmpeg -y -i \'%s\' -an -vn -scodec copy -copyinkf -f ass \'%s\''
    sub_file = os.path.join(args.destination, 'sub.ass')
    p_cmd = cmd % (video.path, sub_file)
    if args.verbose: print p_cmd
    p = subprocess.Popen(p_cmd, shell=True, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
    p.wait()
    if args.debug: print ''.join(p.stdout.readlines())
    return sub_file

def main():
    args = get_args()
    vids = [ VideoFile(p) for p in args.files ]

    make_dir(args.destination)

    for v in vids:
        # if args.verbose: print "Creating subtitle file"
        # sub = extract_subtitles(args, v)
        # if args.verbose: print "Created " + sub
        take_screenshots(args, v)
        # if args.verbose: print "Removing " + sub
        # os.remove(sub)

main()
