git -C ./repo log \
    --pretty=format:'{%n  "sha": "%H",%n  "author_name": "%aN",%n  "author_date": "%ai",%n  "committer_name": "%cN",%n  "committer_date": "%ci",%n  "parents": "%P",%n  "message": "%f"%n},' \
    --all \
    --reverse \
    $@ | \
    perl -pe 'BEGIN{print "["}; END{print "]\n"}' | \
    perl -pe 's/},]/}]/'