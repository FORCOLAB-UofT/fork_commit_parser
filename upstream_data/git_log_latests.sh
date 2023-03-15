for branch in `git -C ./repo branch -r | grep -v HEAD`; \
do echo -e `git -C ./repo log -1 $branch --pretty=format:'%H'`; \
done \