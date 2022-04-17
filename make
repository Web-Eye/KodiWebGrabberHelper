#!/bin/bash

echo "Installing KodiWebGrabber..."
pg=`dirname "$0"`

cp -r $pg/../KodiWebGrabber /usr/share/
chmod +x /usr/share/KodiWebGrabber/main.py
chown root:root -R /usr/share/KodiWebGrabber

echo "complete"

