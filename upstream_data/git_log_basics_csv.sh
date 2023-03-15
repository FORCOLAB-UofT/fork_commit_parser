git -C ./repo log \
    --pretty=format:'"%H","%aN","%ai","%aE","%cN","%ci","%cE","%P","%f"%n' \
    --all \
    --reverse