#!/usr/bin/env python

from datetime import datetime
import json

import click
import requests
import matplotlib.style as style
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from json.decoder import JSONDecodeError

def req_url(reg, rep, tag, image_id):
    """
    Format the url to call Anchore Navigator (anchore.io) for the changelog information of an image

    @param reg: Docker Registry
    @param rep: Repository
    @param tag: Image Tag
    @param image_id: Image Id
    @return: formatted URL string 
    @rtype: string
    """
    url="https://anchore.io/service/registries/dockerhub/repositories/{}%252F{}/tags/{}/list-package-detail/{}/changelog"
    return url.format(reg,rep,tag,image_id)
    
def get_id(reg,rep,tag):
    """
    Query the Anchore Navigator (anchore.io) service to find the newest image id matching the tag.

    @param reg: Docker Registry
    @param rep: Repository
    @param tag: Image Tag
    @return: Image ID
    @rtype: string
    """
    url = "https://anchore.io/service/registries/dockerhub/repositories/{}%252F{}/tags?privaterepo=false"
    ret = requests.get(url.format(reg,rep)).json()['tags']['results']
    for r in ret:
        if r['name'] == tag:
            return r['image_id']
    
    
def get_update_dictionary(repos, years):
    """
    Gets all update datetimes for images in a list of repos.
    
    @param repos: list of lists of strings: ['registry', 'repo', 'tag']
    @param years: integer - number of years to look back (from the current year)
    @return: dictionary where the keys are the image string and the values are a list of update datetimes
    @rtype: dictionary
    """
    updates = {}
    for r in repos:
        tag = '{}/{}:{}'.format(r[0],r[1],r[2])
        try:
            ret = requests.get(req_url(r[0], r[1], r[2], get_id(r[0],r[1],r[2]))).json()
        except JSONDecodeError as e:
            try:
                print('Ding!')
                ret = requests.get(req_url(r[0], r[1], r[2], get_id(r[0],r[1],r[2]))).json()
            except:
                print('Ding!Ding!')
                ret = requests.get(req_url(r[0], r[1], r[2], get_id(r[0],r[1],r[2]))).json()
        try:
            most_recent = datetime.fromtimestamp(ret['changelog']['history'][0]['created_at'])
            second_most = datetime.fromtimestamp(ret['changelog']['history'][1]['created_at'])
            print('Found', tag, '- loading update history.')
            updates[tag] = [most_recent, second_most]
            try:
                while updates[tag][-1].year > datetime.now().year - years:
                    try:
                        ret = requests.get(req_url(r[0], r[1], r[2], ret['changelog']['history'][1]['image_id'])).json()
                    except JSONDecodeError as e:
                        try:
                            print('Ding!')
                            ret = requests.get(req_url(r[0], r[1], r[2], ret['changelog']['history'][1]['image_id'])).json()
                        except:
                            print('Ding!Ding!')
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

def format_repos(repos):
    """
    Parse and split different potential repo/image strings into consistent format.

    @param repos: list of imag/repo strings
    @return: list of lists of strings: ['library', 'repo', 'tag']
    @rtype: list
    """
    reps = []
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
    return reps

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
