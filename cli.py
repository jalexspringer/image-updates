#!/usr/bin/env python

import json

import click
import matplotlib.pyplot as plt

from utils import *


@click.command()
@click.argument('repos', nargs=-1)
@click.option('--years', '-y', default=1, help='Number of years (from this one) to look back.')
@click.option('--style', '-s', default='ggplot', help='Matplotlib plotting style. Defaults to ggplot.')
@click.option('--output', '-o', default='results.png', help='Output file for the plot.')
@click.option('--json_out', '-j', default='None', help='Export to a JSON file. Pass file name.')
@click.option('--verbose', '-v', is_flag=True, help='List datetimes in your terminal?')
def create_plot_file(repos, years, style, output, json_out, verbose):
    """This script returns the update frequency of Docker Hub images and generates a plot with update dates.
       Pass any number of of images/repos - accepts the following formats: library/ubuntu:latest, ubuntu:latest, ubuntu'
    """
    # TODO Check for connection - handle requests.exceptions.ConnectionError
    reps = format_repos(repos)
    updates = get_update_dictionary(reps, years)

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

    fig = plt.figure(1)
    ax = fig.add_subplot(1,1,1)
    plotter(updates, style, verbose, fig, ax)
    plt.tight_layout()
    plt.savefig(output)
