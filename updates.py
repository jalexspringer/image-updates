#!/usr/bin/env python

from datetime import datetime
import sys

import click
import requests
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateFormatter, AutoDateLocator

def req_url(reg, rep, tag, image_id):
    url="https://anchore.io/service/registries/dockerhub/repositories/{}%252F{}/tags/{}/list-package-detail/{}/changelog"
    return url.format(reg,rep,tag,image_id)
    
def get_id(reg,rep,tag):
    url = "https://anchore.io/service/registries/dockerhub/repositories/{}%252F{}/tags?privaterepo=false"
    ret = requests.get(url.format(reg,rep)).json()['tags']['results']
    for r in ret:
        if r['name'] == tag:
            return r['image_id']
    
    
def get_update_dictionary(repos, years):
    updates = {}
    for r in repos:
        ret = requests.get(req_url(r[0], r[1], r[2], get_id(r[0],r[1],r[2]))).json()
        tag = '{}/{}:{}'.format(r[0],r[1],r[2])
        try:
            most_recent = datetime.fromtimestamp(ret['changelog']['history'][0]['created_at'])
            second_most = datetime.fromtimestamp(ret['changelog']['history'][1]['created_at'])
            print('Found', tag, '- loading update history.')
            updates[tag] = [most_recent, second_most]
            try:
                while updates[tag][-1].year > datetime.now().year - years:
                    ret = requests.get(req_url(r[0], r[1], r[2], ret['changelog']['history'][1]['image_id'])).json()
                    updates[tag].append(datetime.fromtimestamp(ret['changelog']['history'][1]['created_at']))
                print(tag, 'history loaded')
            except KeyError as e:
                print('Image history is not that long!')
                continue
        except KeyError as e:
            print(tag, '- image not found. Check spelling of image and tags.')
            continue
    return updates

@click.command()
@click.argument('repos', nargs=-1)
@click.option('--years', '-y', default=1, help='Number of years (from this one) to look back.')
@click.option('--output', '-o', default='results.png', help='Output file for the plot.')
def plot_updates(repos, years, output):
    """This script returns the update frequency of Docker Hub images and generates a plot with update dates.
       Pass any number of of images/repos - accepts the following formats: library/ubuntu:latest, ubuntu:latest, ubuntu'
    """
    matplotlib.style.use('ggplot')
    reps = []
    fig, ax = plt.subplots(1)
    for repo in repos:
        if '/' in repo:
            if ':' in repo:
                r = repo.split('/')[1].split(':')
                r.insert(0, repo.split('/')[0])
                reps.append(r)
            else:
                r = repo.split('/')
                r.append('latest')
                reps.append(r)
        elif ':' in repo:
            r = repo.split(':')
            r.insert(0, 'library')
            reps.append(r)
        else:
            reps.append(['library', repo, 'latest'])
    updates = get_update_dictionary(reps, years)
    for k,v in updates.items():
        l = []
        for i in v:
            l.append(k.split(':')[0])
        ax.plot(v,l, ls='None', marker='s', markeredgecolor='black')
    xtick_locator = AutoDateLocator()
    xtick_formatter = AutoDateFormatter(xtick_locator)
    ax.xaxis.set_major_locator(xtick_locator)
    ax.xaxis.set_major_formatter(xtick_formatter)
    plt.tight_layout()
    plt.savefig(output)
    
