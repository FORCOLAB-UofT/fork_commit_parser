import pandas as pd
from REQUESTS_HANDLER import requestHandler
import csv
import pathlib
from datetime import datetime
import time
import numpy as np

request_handler = requestHandler()

def main():
    df = pd.read_csv('./src_data/astropy_pkgs_forks.csv')
    astropy_pkgs_forks = df['fork_slug'].unique().tolist()
    df = pd.read_csv('./src_data/dev_activities.csv')
    latest_activity_repos = list(set(df['latest_commit_repo'].dropna().unique().tolist()) | set(df['latest_pr_repo'].dropna().unique().tolist()) | set(df['latest_issue_repo'].dropna().unique().tolist()))
    df = pd.read_csv('./src_data/51_repo_slug.csv')
    astropy_pkgs = df['repo_name'].unique().tolist()
    astropy_pkgs_owners = set()
    astropy_pkgs_repos = set()
    for p in astropy_pkgs:
        astropy_pkgs_owners.add(p.split('/')[0])
        astropy_pkgs_repos.add(p.split('/')[1])
    astropy_pkgs_owners = list(astropy_pkgs_owners)
    astropy_pkgs_repos = list(astropy_pkgs_repos)
    
    suspects = []
    for r in latest_activity_repos:
        owner = r.split('/')[0]
        repo = r.split('/')[1]
        if owner in astropy_pkgs_owners or repo in astropy_pkgs_repos:
            if r not in astropy_pkgs and r not in astropy_pkgs_forks:
                suspects.append(r)

    print(suspects)

    


    
        


    
            
            

    
    

if __name__ == '__main__':
    main()