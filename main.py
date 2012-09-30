#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The Flask part of iposonic
#
# author: Roberto Polli robipolli@gmail.com (c) 2012
#
# License AGPLv3
#
# TODO manage argv for:
#   * music_folders
#   * authentication backend
#   * reset db
#
from __future__ import unicode_literals
import logging
logging.basicConfig(level=logging.INFO)

import sys
import os
os.path.supports_unicode_filenames = True
import thread
import argparse

from iposonic import Iposonic

from webapp import Dbh

from webapp import app, log
from authorizer import Authorizer

# Import all app views
import view_browse
import view_playlist
import view_user
import view_media


def yappize():
    try:
        # profiling
        import yappi
        import signal

        def signal_handler(signal_n, frame):
            print 'You pressed Ctrl+C!'
            yappi.stop()
            yappi.print_stats(open("yappi.out", "w"))
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)

        yappi.start()
    except:
        pass


def run(argc, argv):

    parser = argparse.ArgumentParser(
                        description='Iposonic is a SubSonic compatible streaming server.'
                        + 'Run with #python ./main.py -c /opt/music')
    parser.add_argument('-c', dest='collection', metavar=None, type=str,
                        nargs="+", required=True,
                        help='Music collection path')
    parser.add_argument('-t', dest='tmp_dir', metavar=None, type=str,
                        nargs=None, default=os.path.expanduser('~/.iposonic'),
                        help='Temporary directory')
    parser.add_argument('--profile', metavar=None, type=bool,
                        nargs='?', const=True, default=False, 
                        help='profile with yappi')

    parser.add_argument(
                        '--access-file', dest='access_file', action=None, type=str,
                        default=os.path.expanduser('~/.iposonic_auth'),
                        help='Access file for user authentication. Use --access-file "no" to disable authentication.')
    parser.add_argument(
                        '--free-coverart', dest='free_coverart', action=None, type=bool,
                        const=True, default=False, nargs='?',
                        help='Do not authenticate requests to getCoverArt. Default is False: iposonic requires authentication for every request.')
    parser.add_argument('--resetdb', dest='resetdb', action=None, type=bool,
                        const=True, default=False, nargs='?',
                        help='Drop database and cache directories and recreate them.')
    parser.add_argument(
                        '--rename-non-utf8', dest='rename_non_utf8', action=None, type=bool,
                        const=True, default=False, nargs='?',
                        help='Rename non utf8 files to utf8 guessing encoding. When false, iposonic support only utf8 filenames.')

    args = parser.parse_args()
    print(args)
    
    if args.profile:
        yappize()
        
    app.config.update(args.__dict__)

    for x in args.collection:
        assert(os.path.isdir(x)), "Missing music folder: %s" % x

    app.iposonic = Iposonic(args.collection, dbhandler=Dbh,
                            recreate_db=args.resetdb, tmp_dir=args.tmp_dir)
    app.iposonic.db.init_db()
    print thread.get_ident(), "iposonic main @%s" % id(app.iposonic)

    # While developing don't enforce authentication
    #   otherwise you can use a credential file
    #   or specify your users inline
    skip_authentication = (args.access_file == 'no')
    app.authorizer = Authorizer(
        mock=skip_authentication, access_file=args.access_file)

    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == "__main__":
    argc, argv = len(sys.argv), sys.argv
    run(argc, argv)
