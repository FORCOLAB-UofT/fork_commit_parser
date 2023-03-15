import requests
from requests.auth import HTTPBasicAuth
from github import Github
import github
import json
from urllib.parse import quote

GITHUB_API_REPO = "https://api.github.com/repos/"
GITHUB_API_SEARCH = "https://api.github.com/search/"

'''
GitHub API Requests API

Before use: create a config.json file with two attributes:
{
    "access_tokens": [],
    "auth_username": []
}
Add your own token into the access_tokens and add account name in auth_username. 
The order of two list must match.
'''


class requestHandler:
    # this class handles all interactions with github API.
    def __init__(self):
        self.cur_token = 0
        with open('config.json') as f:
            config = json.load(f)
        self.auth_username = config["auth_username"]
        self.access_tokens = config["access_tokens"]
        self.auth = HTTPBasicAuth(
            self.auth_username[self.cur_token], self.access_tokens[self.cur_token])
        self.headers = {
            'Authorization': 'token {}'.format(self.access_tokens[0]),
        }
        try:
            self.pyGithub = Github(self.access_tokens[self.cur_token])
            print("success ini")
        except github.RateLimitExceededException:
            self.switchToken()

    def switchToken(self):
        '''
        Changes to a new token. If cur_token is the last token, change to the first one.
        '''
        print("Reach query limit: switch token")
        self.cur_token = self.cur_token + \
            1 if self.cur_token < len(self.access_tokens) - 1 else 0
        print('Current token: {} -- {}'.format(
            self.auth_username[self.cur_token], self.access_tokens[self.cur_token]))
        self.auth = HTTPBasicAuth(
            self.auth_username[self.cur_token], self.access_tokens[self.cur_token])
        self.pyGithub = Github(self.access_tokens[self.cur_token])

    def get_repo(self, repo_url):
        '''
        Returns a pygithub repo based on repo_url
        repo_url: repo we want to access. E.g: markjaquith/grunt-wp-plugin
        '''
        print(repo_url)
        try:
            repo = self.pyGithub.get_repo(repo_url)
        except github.RateLimitExceededException:
            self.switchToken()
            return self.get_repo(repo_url)
        except Exception as e:
            print(e)
            return None
        
        return repo

    def get_branches(self, repo):
        '''
        Returns a pygithub list of branches based on repo_url
        repo_url: repo we want to access. E.g: markjaquith/grunt-wp-plugin       
        '''
        try:
            brs = repo.get_branches()
            # change the result to list, otherwise pygithub try to send request when iterating,
            # which may lead to rate limit error
            return list(brs)
        except github.RateLimitExceededException:
            self.switchToken()
            return self.get_branches(repo)
        except:
            return None

    def is_mirror(self, repo_url):
        '''
        Check if repo_url is a mirror repo
        '''
        url = GITHUB_API_REPO + repo_url
        try:
            mirror = requests.get(url, auth=self.auth).json()['mirror_url']
        except ValueError:
            self.switchToken()
            mirror = requests.get(url, auth=self.auth).json()['mirror_url']
        except KeyError:
            self.switchToken()
            mirror = requests.get(url, auth=self.auth).json()['mirror_url']
        return mirror is not None

    def get_pulls(self, repo_url, owner):
        '''
        Return the total count of external pull requests
        repo_url: repo we want to access. E.g: markjaquith/grunt-wp-plugin
        '''
        pull_url = "{}issues?q=is:pr+repo:{}+-author:{}".format(
            GITHUB_API_SEARCH, quote(repo_url), owner)

        try:
            rep = requests.get(pull_url, auth=self.auth)
            pulls = rep.json()
        except github.RateLimitExceededException:
            self.switchToken()
            pulls = requests.get(pull_url, auth=self.auth).json()
        except:
            return 0
        if 'message' in pulls:
            # self.switchToken()
            # pulls = requests.get(pulls, auth=self.auth).json()
            print(rep.headers)
            print(rep.text)
        return pulls['total_count']

    def get_commits(self, repo_url, branch, cur_page, page_size=100):
        '''
        Return a page of commits in given branch in given repo
        '''
        commit_url = "{}{}/commits?sha={}&per_page={}&page={}".format(
            GITHUB_API_REPO, quote(repo_url), quote(branch.name), page_size, cur_page)
        commits = requests.get(commit_url, auth=self.auth).json()
        if 'message' in commits:
            self.switchToken()
            commits = requests.get(commit_url, auth=self.auth).json()
        return commits

    def get_commit(self, repo_url, sha):
        '''
        Return a single commit by sha
        '''
        url = GITHUB_API_REPO + repo_url + '/commits/{}'.format(sha)
        commit = requests.get(url, auth=self.auth).json()
        if 'message' in commit:
            self.switchToken()
            commit = requests.get(url, auth=self.auth).json()
        return commit

    def get_contributors(self, repo_url, cur_page, page_size=100):
        '''
        Return a page of contributors in given repo
        '''
        contributor_url = "{}{}/contributors?&per_page={}&page={}".format(
            GITHUB_API_REPO, quote(repo_url), page_size, cur_page)
        contributors = requests.get(contributor_url, auth=self.auth).json()
        if 'message' in contributors:
            self.switchToken()
            contributors = requests.get(contributor_url, auth=self.auth).json()
        return contributors

    def get_forks(self, repo_url, cur_page, page_size=100):
        '''
        Return a page of forks of a given repo
        '''
        fork_url = "{}{}/forks?&per_page={}&page={}".format(
            GITHUB_API_REPO, quote(repo_url), page_size, cur_page)
        forks = requests.get(fork_url, auth=self.auth).json()
        if 'message' in forks:
            self.switchToken()
            forks = requests.get(fork_url, auth=self.auth).json()
        return forks

    def get_issues(self, repo_url, cur_page, page_size=100):
        '''
        Return all issues and PRs
        '''
        issue_url = "{}{}/issues?state=all&per_page={}&page={}".format(
            GITHUB_API_REPO, quote(repo_url), page_size, cur_page)
        issues = requests.get(issue_url, auth=self.auth).json()
        if 'message' in issues:
            self.switchToken()
            issues = requests.get(issue_url, auth=self.auth).json()
        return issues

    def get_user_latest_commit(self, username):
        '''
        Return user's latest commit
        '''
        url = "{}commits?q=author%3A{}+sort:author-date-desc&per_page=1".format(
            GITHUB_API_SEARCH, username
        )
        commit = requests.get(url, auth=self.auth).json()
        if 'message' in commit:
            self.switchToken()
            commit = requests.get(url, auth=self.auth).json()
        return commit

    def get_user_latest_pr(self, username):
        '''
        Return user's latest PR
        '''
        url = "{}issues?q=author%3A{}+type%3Apr&per_page=1".format(
            GITHUB_API_SEARCH, username
        )
        pr = requests.get(url, auth=self.auth).json()
        if 'message' in pr:
            self.switchToken()
            pr = requests.get(url, auth=self.auth).json()
        return pr

    def get_user_latest_issue(self, username):
        '''
        Return user's latest issue
        '''
        url = "{}issues?q=author%3A{}+type%3Aissue&per_page=1".format(
            GITHUB_API_SEARCH, username
        )
        issue = requests.get(url, auth=self.auth).json()
        if 'message' in issue:
            self.switchToken()
            issue = requests.get(url, auth=self.auth).json()
        return issue

    def get_user_profile(self, username):
        '''
        Return user's profile
        '''
        url = "https://api.github.com/users/{}".format(
            username
        )
        profile = requests.get(url, auth=self.auth).json()
        if 'message' in profile:
            self.switchToken()
            profile = requests.get(url, auth=self.auth).json()
        return profile
    
    def get_rate_limit(self):
        response = requests.get('https://api.github.com/rate_limit', headers=self.headers)
        return response.text
