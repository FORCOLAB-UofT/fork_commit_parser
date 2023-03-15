import pandas as pd
from REQUESTS_HANDLER import requestHandler
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

def count_issues_prs(fork):
    '''
    count fork issues and PRs
    '''
    issues_count = 0
    prs_count = 0
    cur_page = 1
    while True:
        issues_prs = request_handler.get_issues(fork, cur_page)
        if issues_prs == []:
            break
        for issue_pr in issues_prs:
            if 'pull_request' in issue_pr:
                prs_count += 1
            else:
                issues_count += 1
        cur_page += 1
    return [issues_count, prs_count]

def main():
    df = pd.read_csv('./src_data/astropy_pkgs_forks.csv')
    forks = df.to_dict('records')
    for fork in forks[4579:]:
        print(fork['fork_slug'])
        fork_repo = check_validity(fork['fork_slug'])
        if ((not check_validity(fork['upstream_slug'])) or not fork_repo):
            continue
        [issues_count, prs_count] = count_issues_prs(fork['fork_slug'])
        fork['num_issues'] = issues_count
        fork['num_PRs'] = prs_count
        fork['type'] = fork_repo.owner.type
        with open('result_misc.csv', 'a') as f:
                w = csv.DictWriter(f, fork.keys())
                w.writerow(fork)
    # print(request_handler.get_rate_limit())
        
            
            

    
    

if __name__ == '__main__':
    main()