#!/usr/bin/python
from pathlib import Path
import sys
import os
import argparse


def check_magic_str(magic_str):
    MAGIC_STR = "postproc"
    if magic_str != MAGIC_STR:
        print('Wrong magic string: "{}" ≠ "{}"'.format(MAGIC_STR, magic_str), file=sys.stderr)
        sys.exit(1)


class PostProcesser:
    def __init__(self, dest):
        self.dest = Path(dest)

    def process_folder(self, src):
        print("folder")

    def process_file(self, src):
        print("Creating hard link for {}".format(src.stem))
        try:
            os.link(str(src), str(self.dest / src.stem))
        except IOError as e:
            print('Unable to create hard link.\n{}'.format(e))


def main():
    args = parse_args()
    print(args)
    check_magic_str(args.magic_str)

    for src in args.sources:
        src = Path(src)
        if not src.exists():
            print('"{}" does not exist. Ignoring...'.format(src), file=sys.stderr)
            continue

        pp = PostProcesser(args.dest)
        if src.is_file():
            pp.process_file(src)
        elif src.is_dir():
            pp.process_folder(src)
        else:
            print("Unsupported type", file=sys.stderr)
            sys.exit(4)


def parse_args():
    parser = argparse.ArgumentParser(description="Simple post processer")
    parser.add_argument('-d', '--dest', help="The destination folder")
    parser.add_argument('-m', '--magic-str', help="User supplied magic string")
    parser.add_argument('sources', nargs='+', help="The sources to post process")
    return parser.parse_args()

if __name__ == '__main__':
    main()
