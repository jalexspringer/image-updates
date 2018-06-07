#!/usr/bin/env python

import json

import click
import matplotlib.style as style
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from json.decoder import JSONDecodeError

from utils import *


@click.command()
@click.argument('repos', nargs=-1)
@click.option('--years', '-y', default=1, help='Number of years (from this one) to look back.')
@click.option('--output', '-o', default='results.png', help='Output file for the plot.')
@click.option('--human_readable', '-h', is_flag=True, help='Easy to read datetimes?')
@click.option('--json_out', '-j', default='None', help='Export to a JSON file. Pass file name.')
def plot_updates(repos, years, output, human_readable, json_out):
    """This script returns the update frequency of Docker Hub images and generates a plot with update dates.
       Pass any number of of images/repos - accepts the following formats: library/ubuntu:latest, ubuntu:latest, ubuntu'
    """
    reps = format_repos(repos)
    updates = get_update_dictionary(reps, years)
    
    # Output the json file on demand
    if json_out != 'None':
        with open(json_out, 'w') as outfile:
            json.dump(updates, outfile, indent=4, sort_keys=True, default=str)
            
    # Pixels and plots for fun and profit!
    style.use('ggplot')
    fig = plt.figure(1)
    ax = fig.add_subplot(1,1,1)
    counter, labels, y = 1, [], []
    for k,v in updates.items():
        y.append(counter)
        print(k, 'update times:')
        for d in v:
            print(d)
        l = []
        for i in v:
            l.append(counter)
        labels.append(k.split('/')[1])
        plt.plot(v,l, ls='None', marker='s', markeredgecolor='black')
        counter += .25
        
    # Fiddle with the x axis
    #set ticks every week
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    #set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b \'%y'))
    # Lean back
    ax.tick_params(axis='x', rotation=40)
    fig.set_figwidth(9)

    # Fiddle with the y axis
    ax.set_ylim(.75, counter)
    plt.yticks(y, labels)
    height = .75 * len(labels)
    if height < 1:
        fig.set_figheight(1)
    else:
        fig.set_figheight(height)
    plt.tight_layout()
    plt.savefig(output)
