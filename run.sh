#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/credentials.sh"
"$DIR/update_dns.py" -R ph34r.mrskeltal.io -v
