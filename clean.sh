#!/bin/sh
for PTN in "*.pyc" "*.pyo" "*~"; do
    find . -name "$PTN" | xargs rm 2>/dev/zero
done
