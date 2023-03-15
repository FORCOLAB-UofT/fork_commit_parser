import os
from datetime import datetime
import pytz
import networkx as nx
from pydriller import Repository
import json
import pandas as pd
import numpy as np


def get_upstream_commits(upstream):
    if upstream is not None:
        command = "cd ./upstream_data && git clone {} repo".format(
            upstream.clone_url)
        os.system(command)
        print("upstream cloned")
        upstream_commits = parse_all_commits('upstream')
        upstream_latest_commits = parse_latest_commits('upstream')
        os.system('cd ./upstream_data && rm -rf repo')
        return [upstream_commits, upstream_latest_commits]
    else:
        print("upstream is invalid")
        return

def get_fork_commits(fork):
    if fork is not None:
        command = "cd ./fork_data && git clone {} repo".format(
            fork.clone_url)
        os.system(command)
        print("fork cloned")
        fork_commits = parse_all_commits('fork')
        fork_latest_commits = parse_latest_commits('fork')
        os.system('cd ./fork_data && rm -rf repo')
        return [fork_commits, fork_latest_commits]
    else:
        print("fork is invalid")
        return


def get_all_commits(upstream_commits, upstream_latest_commits, fork_commits, fork_latest_commits, forking_date):
    all_commits = {x['commit']: x for x in fork_commits +
                   upstream_commits}.values()
    print("raw commits merged")

    classify_commits(
        all_commits, upstream_latest_commits, fork_latest_commits, forking_date)
    print("commit classified")

    return list(all_commits)


def find_shortest_path(g, node, branch):
    try:
        return nx.shortest_path_length(g, node, branch, 'weight')
    except nx.exception.NetworkXNoPath:
        return 999


def classify_commits(raw_commits, upstream_latest_commits, hardfork_latest_commits, forking_date):
    commits = []
    for commit in raw_commits:
        if commit['author_date'] > forking_date:
            commits.append((commit['commit'], commit))
    num_commits = len(commits)
    g = nx.DiGraph()
    g.add_nodes_from(commits)
    nodes = list(g.nodes)
    for node in nodes:
        parents = g.nodes[node]['parents']
        if parents == []:
            pass
        elif len(parents) == 2:
            if parents[1] in g.nodes:
                g.add_weighted_edges_from([(parents[1], node, 1)])
            g.add_weighted_edges_from([(parents[0], node, 0)])
        else:
            g.add_weighted_edges_from([(parents[0], node, 0)])
    print("finished adding edges")
    processed_commits = {}
    count = 0
    for node in list(g.nodes):
        to_upstream = min([find_shortest_path(g, node, branch)
                          for branch in upstream_latest_commits])
        to_hardfork = min([find_shortest_path(g, node, branch)
                          for branch in hardfork_latest_commits])
        data = {
            'to_upstream': to_upstream,
            'to_hardfork': to_hardfork
        }
        processed_commits[node] = data
        count += 1
        print("{:.2%}".format(count/num_commits))

    '''
    process commits to categorize them by commit states
    1). created before the forking point
    2). only upstream (not synchronized)
    3). only in fork (unmerged)
    4). created upstream but synchronized to the fork
    5). created in the fork but merged into upstream
    '''
    for commit in raw_commits:
        if commit['commit'] not in processed_commits:
            commit['type'] = 1
        else:
            if processed_commits[commit['commit']]["to_upstream"] != 999 and processed_commits[commit['commit']]["to_hardfork"] != 999:
                if processed_commits[commit['commit']]["to_upstream"] > processed_commits[commit['commit']]["to_hardfork"]:
                    commit['type'] = 5
                elif processed_commits[commit['commit']]["to_upstream"] < processed_commits[commit['commit']]["to_hardfork"]:
                    commit['type'] = 4
                else:
                    commit['type'] = 0
            elif processed_commits[commit['commit']]["to_upstream"] != 999:
                commit['type'] = 2
            elif processed_commits[commit['commit']]["to_hardfork"] != 999:
                commit['type'] = 3
            else:
                commit['type'] = -1


def parse_all_commits(type):
    command = "cd ./{}_data && bash git_log_basics_csv.sh > basics.csv".format(type)
    os.system(command)
    basics = pd.read_csv("./{}_data/basics.csv".format(type), header=None, names=['sha', 'author_name', 'author_date', 'author_email', 'committer_name', 'committer_date', 'committer_email', 'parents', 'message'], encoding="ISO-8859-1")
    basics = basics.replace({np.nan: None})
    basics = basics.to_dict('records')
    command = "cd ./{}_data && rm basics.csv".format(type)
    os.system(command)
    command = "cd ./{}_data && bash git_log_files.sh > files.json".format(type)
    os.system(command)
    with open("./{}_data/files.json".format(type)) as f2:
        files = json.load(f2)
        f2.close()
    command = "cd ./{}_data && rm files.json".format(type)
    os.system(command)
    commit_data = []
    if len(basics) != len(files):
        return commit_data
    for commit in basics:
        parents = []
        if commit['parents']:
            if " " in commit['parents']:
                parents = commit['parents'].split()
            else:
                parents = [commit['parents']]
        data = {
            "commit": commit['sha'],
            "message": commit['message'],
            "author_name": commit['author_name'],
            "author_date": datetime.strptime(str(commit['author_date']), '%Y-%m-%d %H:%M:%S %z').astimezone(pytz.UTC).replace(tzinfo=None),
            "committer_name": commit['committer_name'],
            "committer_date": datetime.strptime(str(commit['committer_date']), '%Y-%m-%d %H:%M:%S %z').astimezone(pytz.UTC).replace(tzinfo=None),
            "parents": parents,
            "is_merge": len(parents) > 1,
            "num_files": len(files[commit['sha']]),
            "modified_files": files[commit['sha']]
        }
        commit_data.append(data)
    return commit_data


def parse_latest_commits(type):
    command = "cd ./{}_data && bash git_log_latests.sh > git_log_latests.txt".format(type)
    os.system(command)
    latest_commits = []
    f1 = open('./{}_data/git_log_latests.txt'.format(type))
    while True:
        commit = f1.readline()
        if not commit:
            break
        latest_commits.append(commit[:-1])
    f1.close()
    os.remove('./{}_data/git_log_latests.txt'.format(type))
    return latest_commits
