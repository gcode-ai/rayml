"""CLI commands."""

import click

from rayml.utils.cli_utils import print_info


@click.group()
def cli():
    """CLI command with no arguments. Does nothing."""
    pass


@click.command()
def info():
    """CLI command with `info` argument. Prints info about the system, rayml, and dependencies of rayml."""
    print_info()


cli.add_command(info)
