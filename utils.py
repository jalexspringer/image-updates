#!/usr/bin/env python

from datetime import datetime

import requests
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.style as style

from json.decoder import JSONDecodeError


def read_replace_datetime(dates):
    out = [datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in dates]
    return out

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
    
    
def get_update_dictionary(repos, years, quiet):
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
            if not quiet:
                print('Found', tag, '- loading update history')
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
                if not quiet:
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

def plotter(updates, styl, output, height, width):
    # Pixels and plots for fun and profit!
    style.use(styl)
    fig = plt.figure(1)
    ax = fig.add_subplot(1,1,1)
    counter, labels, y = 1, [], []
    for k,v in updates.items():
        y.append(counter)
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
    fig.set_figwidth(width)

    # Fiddle with the y axis
    ax.set_ylim(.75, counter)
    plt.yticks(y, labels)
    if height < 0:
        height = .75 * len(labels)
    if height <= 1:
        fig.set_figheight(1.25)
    else:
        fig.set_figheight(height)

    plt.tight_layout()
    if output:
        plt.savefig(output)
