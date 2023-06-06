#!/bin/bash
# Copyright (C) Mark McIntyre
#

# forward email for ukmonfundraiser and ukmoncommittee emails

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# ukmonfundraiser
recips=$here/ukmonfundraising.txt
tok=$here/ukmonfundraising_token.json
crd=$here/ukmonfundraising_creds.json
if [[ -f $recips && -f $tok && -f $crd ]] ; then 
    python -c "from mailForwarder import forwardFromSource; forwardFromSource('${recips}','${tok}','${crd}');"
fi
# ukmoncommittee
recips=$here/ukmoncommittee.txt
tok=$here/ukmoncommittee_token.json
crd=$here/ukmoncommittee_creds.json
if [[ -f $recips && -f $tok && -f $crd ]] ; then 
    python -c "from mailForwarder import forwardFromSource; forwardFromSource('${recips}','${tok}','${crd}');"
fi 
