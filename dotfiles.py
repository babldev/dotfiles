import argparse
import logging
import os
import re

import dotfiles


MODULE_PATH = os.path.dirname(dotfiles.__file__)

# Create the logger.
FORMAT = ': %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('dotfiles')
logger.setLevel(logging.WARNING)


class Dotfile(object):
    """A single dotfile for installation."""

    def __init__(self, path):
        self.path = path

    def install(self):
        f = open(self.install_file_path, 'r')
        logger.info("Running install commands for \"%s\" dotfile path \"%s\"." % (self.path, self.install_file_path))

        for line in f.readlines():
            action = LinkAction.action_from_string(self.path, line)
            if action:
                action.link()

        f.close()

    @property
    def install_file_path(self):
        """Path to the /install file."""
        return os.path.join(self.path, "install")

    @staticmethod
    def all_dotfiles():
        """Find all directories containing an 'install' file in the module."""
        dotfiles = []
        for dir in os.listdir(MODULE_PATH):
            if os.path.exists(os.path.join(dir, "install")):
                dotfiles.append(Dotfile(os.path.join(MODULE_PATH, dir)))
        return dotfiles


class LinkAction(object):
    """A single install action for creating a symlink."""

    FORMAT = re.compile(r"^link \"?(.*?)\"? to \"?(.*?)\"?\s*$")

    def __init__(self, source, dest):
        self.source = source
        self.dest = dest

    def link(self):
        """Create the symlink."""
        if os.path.lexists(self.dest) and os.path.samefile(self.source, self.dest):
            logger.info("Correct symlink for \"%s\" in place." % (self.dest))
        elif not os.path.exists(self.dest) and not os.path.lexists(self.dest):
            os.symlink(self.source, self.dest)
            logger.info("Successfully symlinked to destination \"%s\"." % (self.dest))
        else:
            logger.error("Failed to symlink to destination \"%s\". File exists." % (self.dest))

    @classmethod
    def action_from_string(cls, dir, str):
        """Create a LinkAction object from a string command.

        Example: link source_str to dest_str.
        """
        result = cls.FORMAT.match(str).groups()

        if len(result) == 2:
            source_path = os.path.join(dir, result[0])
            dest_path = os.path.expanduser(result[1])
            return cls(source=source_path, dest=dest_path)

        return None


def install_dotfiles():
    dotfiles = Dotfile.all_dotfiles()
    logger.info('Installing %s dotfile(s).' % len(dotfiles))
    for d in dotfiles:
        d.install()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Install the dotfiles.')
    parser.add_argument("-v", "--verbose", action='store_true', help="Include to enable verbose mode.")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.INFO)
        logger.info('Enabling verbose mode...')

    install_dotfiles()
