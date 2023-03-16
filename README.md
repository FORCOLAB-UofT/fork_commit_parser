# fork commit parser

## Folder Structure

```
Root
|
+-fork_data - (scripts to process fork commits and hold tmp data)
|  |
|  +- shell scripts to process fork commits
|
+-upstream_data - (scripts to process upstream commits and hold tmp data)
|  |
|  +- shell scripts to process upstream commits
|
+- src_data - (src data)
|  |
|  +- tmp.csv (src data of upstream-fork pairs)
|
+-GIT_LOG_PARSER.py - (helpfer functions to process git log commit data)
|
+-REQUESTS_HANDLER.py - (helpfer functions to process GitHub API data)
|
+-fork_parser.py - (main entry point)
|
+-fork_parser.py - (main entry point)
|
+-config.json - (GitHub API tokens)


```

## Setup guide
All the dependencies used in this project can be found in requirements.txt
