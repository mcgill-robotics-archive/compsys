# -*- coding: utf-8 -*-

"""Parse command line arguments for subcommands and shortcuts."""

import sys
import argparse
from bag.cmd import record, merge

__author__ = "Anass Al-Wohoush"


class Help(argparse.Action):

    """Display parser's help on screen and exit."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Display parser's help on screen and exit.

        Args:
            parser: ArgumentParser instance to display help of.
            namespace: Argparse namespace generated by parse_args(). Not used.
            values: Associated command-line arguments. Not used.
            option_string: Option string used to invole this action. Not used.
        """
        parser.print_help()
        sys.exit()


class Parser(object):

    """Parse command line arguments for subcommands and shortcuts.

    Attributes:
        arg: Command-line arguments.
        original: TopicList to parse.
        executable: Name of the executable.
        description: Description of the executable for --help.
        version: Version of the executable.
        enabled: TopicList enabled by command-line arguments.
        dir: Path to directory for input/output.
        cmd: Command to run.
    """

    def __init__(self, original, description, version):
        """Construct Parser object.

        Args:
            original: TopicList to parse.
            description: Description of the executable for --help.
            version: Version of the executable.
        """
        self.arg = sys.argv[1:]
        self.original = original.topics
        self.name = None
        self.description = description
        self.version = version
        self.enabled = []
        self.dir = None
        self.cmd = None
        self.parse()

    def parse(self):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            prog="bag", description=self.description
        )

        parser.add_argument(
            "--version", action="version",
            version="v{}".format(self.version)
        )

        # Add subparsers.
        subparsers = parser.add_subparsers(
            title="commands",
            help="valid subcommands"
        )
        record_parser = subparsers.add_parser(
            "record", add_help=False, description=record.__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            help="record topics into split bags"
        )
        record_parser.set_defaults(cmd=record.Record)
        record_parser.add_argument(
            "--no-split", action="store_true",
            help="don't split bag"
        )
        record_parser.add_argument(
            "--duration", default=15,
            help="seconds per split (default: 15)"
        )
        record_parser.add_argument(
            "--bz2", action="store_true", help="use BZ2 compression"
        )
        record_parser.add_argument(
            "--lz4", action="store_true", help="use LZ4 compression"
        )

        merge_parser = subparsers.add_parser(
            "merge", add_help=False, description=merge.__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            help="merge pre-recorded bags by topics"
        )
        merge_parser.set_defaults(cmd=merge.Merge)

        for subparser in (record_parser, merge_parser):
            # Add common arguments.
            subparser.add_argument(
                "--help", nargs=0, action=Help,
                help="show this help message and exit"
            )
            subparser.add_argument(
                "--name", nargs=1, help="output name"
            )
            subparser.add_argument(
                "dir", nargs='?', default='.',
                help="default: current directory"
            )

            # Dynamically add custom shortcuts.
            for elem in self.original:
                subparser.add_argument(
                    "-" + elem.shortcut,
                    const=elem, action="store_const",
                    help=elem.description,
                )

        # Parse arguments.
        self.raw = parser.parse_args()
        self.name = self.raw.name[0] if self.raw.name else None
        self.dir = self.raw.dir
        self.cmd = self.raw.cmd
        self.enabled = [
            elem for key, elem in vars(self.raw).iteritems()
            if key != "cmd" and elem and
            type(elem) not in (int, bool, str, list)
        ]
        if len(self.enabled) == 0:
            self.enabled = self.original
