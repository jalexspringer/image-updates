#!/usr/bin/env python

import json

import click

from utils import *


@click.command()
@click.argument('repos', nargs=-1)
@click.option('--years', '-y', default=1, help='Number of years (from this one) to look back.')
@click.option('--style', '-s', default='ggplot', help='Matplotlib plotting style. Defaults to ggplot.')
@click.option('--height', '-h', default=-1, help='Custom height. Height will automatically adjust to the number of repos if this is not passed.')
@click.option('--width', '-w', default=9, help='Custom width. Default is 9')
@click.option('--output', '-o', default='results.png', help='Output file for the plot.')
@click.option('--json_out', '-j', default='None', help='Export to a JSON file. Pass file name.')
@click.option('--load_json', '-l', default='None', help='JSON updates dictionary to import from.')
@click.option('--verbose', '-v', is_flag=True, help='List datetimes in your terminal?')
@click.option('--quiet', '-q', is_flag=True, help='No working updates in terminal output at all. You\'ll still see errors.')
def create_plot_file(repos, years, style, height, width, output, json_out, load_json, verbose, quiet):
    """This script returns the update frequency of Docker Hub images and generates a plot with update dates.
       Pass any number of of images/repos - accepts the following formats: library/ubuntu:latest, ubuntu:latest, ubuntu'
    """
    # TODO Check for connection - handle requests.exceptions.ConnectionError
    reps = format_repos(repos)

    if load_json != 'None':
        # Get updates from file
        with open(load_json, 'r') as infile:
            updates = json.load(infile)
            if not quiet:
                print("Loaded the following tag info:")
                for k,v in updates.items():
                    updates[k] = read_replace_datetime(v)
    else:
        # Get updates from Anchore DB
        updates = get_update_dictionary(reps, years, quiet)

    # Output the json file on demand
    if json_out != 'None':
        with open(json_out, 'w') as outfile:
            json.dump(updates, outfile, indent=4, sort_keys=True, default=str)

    # Print results to terminal
    for k,v in updates.items():
        if verbose:
            print(k, 'update times:')
            for d in v:
                print(d)

    plotter(updates, style, output, height, width)
