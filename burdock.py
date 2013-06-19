#!/usr/bin/env python

import os
import ftplib
import argparse
import yaml
import git
import sys

VERSION = "0.1"
REVISION_FILE = '.revision'


parser = argparse.ArgumentParser()
parser.add_argument("--config", help="Use the given configuration file",
                    default="dandelion.yml")
parser.add_argument("--repo", help="Use the given repository",
                    default=".")
parser.add_argument("-q", "--quiet", action="store_true",
                    help="Don't display file details")
parser.add_argument("-f", "--force", action="store_true",
                    help="Force deployment of unpushed commit")
parser.add_argument("-p", "--profile",
                    help="Choose a profile")
parser.add_argument("--fake", action="store_true",
                    help="Don't deploy, but write the remote revision file")
parser.add_argument("--dryrun", action="store_true",
                    help="Don't deploy, just print what would be written")
parser.add_argument('--version', action='version',
                    version='%(prog)s ' + VERSION,
                    help="Display the current version")
parser.add_argument('command', choices=['deploy', 'status', 'ls'])
args = parser.parse_args()


repo = git.Repo()
local_revision = repo.head.commit.hexsha
remote_revision = None
ftp = None

config_filename = args.config if args.config is not None else 'dandelion.yml'
try:
    config_file = open(config_filename)
except IOError:
    try:
        config_file = open(os.path.join(repo.working_tree_dir, config_filename))
    except IOError:
        print "Configuration file not found."
        sys.exit(1)

settings = yaml.safe_load(config_file)
config_file.close()

revision_file = settings.get('revision_file', REVISION_FILE)
if 'exclude' not in settings:
    settings['exclude'] = []
settings['exclude'].append(config_filename)

if args.profile is not None:
    if 'profiles' not in settings or args.profile not in settings['profiles']:
        print "Profile '{0}' not found in {1}".format(args.profile,
                                                      config_filename)
        sys.exit(1)
    profile = settings['profiles'][args.profile]
    for key in profile:
        settings[key] = profile[key]


def get_remote_revision(line):
    global remote_revision
    remote_revision = line


def change_directory(filename):
    if not hasattr(change_directory, "path"):
        change_directory.path = '/'
    filepath = os.path.split(filename)[0]
    if (filepath != change_directory.path):
        ftp.cwd("{0}/{1}".format(settings.get('path', '/'), filepath))
        change_directory.path = filepath


def delete_file(filename):
    if not args.quiet:
        print "DELETE {1}".format(filename)
    change_directory(filename)
    basename = os.path.split(filename)[1]
    if filename not in settings['exclude'] and args.dryrun is False:
        ftp.delete(basename)


def upload_file(abspath, filename, show_progress=True):
    if show_progress is True and args.quiet is False:
        print "UPLOAD {0} -> {1}".format(abspath, filename)
    change_directory(filename)
    basename = os.path.split(filename)[1]
    if filename not in settings['exclude'] and args.dryrun is False:
        with open(abspath) as f:
            ftp.storlines("STOR " + basename, f)


def update_remote_revision():
    local_filename = os.path.join(repo.working_tree_dir, revision_file)
    with open(local_filename, "w") as f:
        f.write(local_revision)
    upload_file(local_filename, revision_file, False)
    os.remove(local_filename)


def deploy():
    for diff in repo.commit(remote_revision).diff():
        if diff.deleted_file:
            delete_file(diff.b_blob.path)
        elif diff.renamed:
            # TODO ... er, yeah. this bit.
            print "Haven't done RENAME actions yet"
        else:
            upload_file(diff.b_blob.abspath, diff.b_blob.path)
    update_remote_revision()


def connect():
    global ftp

    if args.dryrun:
        print "--- DRY RUN --"

    print "Connecting to {scheme}://{username}@{host}/{path}".format(**settings)
    ftp = ftplib.FTP(settings['host'], settings['username'], settings['password'])

    if (settings.get('path')):
        ftp.cwd(settings.get('path'))

    ftp.retrlines('RETR ' + revision_file, get_remote_revision)


def disconnect():
    if args.dryrun:
        print "--- DRY RUN --"


if args.command == 'ls':
    if 'profiles' in settings:
        for profile in settings['profiles']:
            print profile
    else:
        print "No alternate profiles are configured."
elif args.command == 'status':
    connect()
    print "{0: <23}{1}".format('Local HEAD revision:', local_revision)
    print "{0: <23}{1}".format('Remote revision:', remote_revision)
    disconnect()
elif args.command == 'deploy':
    connect()
    print "{0: <23}{1}".format('Remote revision:', remote_revision)
    print "{0: <23}{1}".format('Deploying revision:', local_revision)
    if local_revision == remote_revision:
        print "Nothing to deploy"
    elif args.fake is True:
        print "Faking deployment"
        if not args.quiet:
            print "Updating revision to", local_revision
        update_remote_revision()
    else:
        if args.force is False:
            local_commit = repo.commit()
            origin = git.remote.Remote(repo, 'origin')
            origin_commit = origin.fetch()[0].commit
            if local_commit.hexsha != origin_commit.hexsha:
                print "Warning: you are trying to deploy unpushed commits"
                print "This could potentially prevent others from being able to deploy"
                print "If you are sure you want to do this, use the -f option to force deployment"
            else:
                deploy()
        else:
            deploy()
    print "Deployment complete"
    disconnect()
