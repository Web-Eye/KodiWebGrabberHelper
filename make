#!/bin/bash

echo "Installing KodiWebGrabber..."
pg=$(dirname "$0")

rm -r /usr/share/KodiWebGrabber
cp -r "$pg"/KodiWebGrabber /usr/share/
chmod +x /usr/share/KodiWebGrabber/kwg.py
chown root:root -R /usr/share/KodiWebGrabber

echo "complete"

