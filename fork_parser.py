import pandas as pd
import os
from GIT_LOG_PARSER import *
from REQUESTS_HANDLER import requestHandler
from datetime import datetime, timedelta
import csv

request_handler = requestHandler()

def check_validity(repo_url):
    '''
    Check validity of the given repo:
        - exists
        - not a mirror
        - permission
    '''
    repo = request_handler.get_repo(repo_url)
    repo_br = request_handler.get_branches(repo)
    if repo is None or repo_br is None:
        return None
    mirror = request_handler.is_mirror(repo_url)
    if mirror:
        return None
    return repo

def count_type_commits(commits, label):
    commits_count = 0
    for commit in commits:
        if commit['type'] == label:
            commits_count += 1
    return commits_count

def latest_fork_commit_date(fork_commits, fork_latest_commits):
    cur_date = datetime.min
    for latest in fork_latest_commits:
        for commit in fork_commits:
            if commit['commit'] == latest:
                cur_date = max(cur_date, commit['committer_date'])
    return cur_date

def main():
    raw_forks = pd.read_csv('./src_data/tmp.csv')
    upstream_slugs = raw_forks['upstream_slug'].unique().tolist()
    forks_grps = {}
    for up in upstream_slugs:
        forks_grps[up] = {}
        tmp = raw_forks[raw_forks['upstream_slug'] == up]
        fork_slugs = tmp['fork_slug'].tolist()
        for fo in fork_slugs:
            forks_grps[up][fo] = tmp[tmp['fork_slug'] == fo]

    processed_forks = []

    
    for up in upstream_slugs:
        upstream = check_validity(up)
        # print(upstream)
        if not upstream:
            continue
        [upstream_commits, upstream_latest_commits] = get_upstream_commits(upstream)
        fork_slugs = list(forks_grps[up])
        print(fork_slugs)
        for fo in fork_slugs:
            print("upstream: {} - fork: {}".format(up, fo))
            fork = check_validity(fo)
            if not fork:
                continue
            [fork_commits, fork_latest_commits] = get_fork_commits(fork)
            parsed_commits = get_all_commits(upstream_commits, upstream_latest_commits, fork_commits, fork_latest_commits, fork.created_at)
            OnlyF = count_type_commits(parsed_commits, 3)
            OnlyU = count_type_commits(parsed_commits, 2)
            F2U = count_type_commits(parsed_commits, 5)
            U2F = count_type_commits(parsed_commits, 4)
            data = forks_grps[up][fo].to_dict('records')[0]
            data['latest F commit date'] = latest_fork_commit_date(fork_commits, fork_latest_commits)
            data['OnlyF'] = OnlyF
            data['OnlyU'] = OnlyU
            data['F2U'] = F2U
            data['U2F'] = U2F
            data['active'] = False 
            if (OnlyF > 0):
                if (datetime.utcnow() - latest_fork_commit_date(fork_commits, fork_latest_commits) < timedelta(days = 90)):
                    data['active'] = True
            processed_forks.append(data)
            
            with open('result-realtime.csv', 'a') as f:
                w = csv.DictWriter(f, data.keys())
                w.writerow(data)

            df = pd.DataFrame(parsed_commits)
            df.to_csv(
                './results/{}---{}.csv'.format(upstream.full_name.replace("/", "#"), fork.full_name.replace("/", "#")))


    df = pd.DataFrame(processed_forks)
    df.to_csv("result.csv")
            
            

    
    

if __name__ == '__main__':
    main()