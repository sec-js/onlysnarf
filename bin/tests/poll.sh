#!/usr/bin/env bash

# Image & Poll
echo "[*] Misc - Poll"
sudo onlysnarfpy \
-debug \
-action "post" -category "image" \
-bykeywords "pussycats" \
-skip-download \
-text "poll testes" \
-duration 3 \
-questions "your mom, some toast, a nice sandwich" \
-debug-delay \
-$1 \
-verbose -verbose -verbose
# -verbose
# -verbose -verbose