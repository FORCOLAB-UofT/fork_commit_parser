git -C ./repo log \
    --numstat \
    --all \
    --reverse \
    --format='%H' \
    $@ | \
    perl -lawne '
        if (defined $F[1]) {
            $F[2] =~ tr/"//d;
            $F[2] =~ tr/\\//d;
            print qq#{"insertions": "$F[0]", "deletions": "$F[1]", "path": "$F[2]"},#;
        } elsif (defined $F[0]) {
            print qq#],\n"$F[0]": [#
        };
        END{print qq#],#}' | \
    tail -n +2 | \
    perl -wpe 'BEGIN{print "{"}; END{print "}"}' | \
    tr '\n' ' ' | \
    perl -wpe 's#(]|}),\s*(]|})#$1$2#g' | \
    perl -wpe 's#,\s*?}$#}#'