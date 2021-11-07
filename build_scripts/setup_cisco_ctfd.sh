#!/bin/bash
# Sets up the CTFd instance and installs the cisco CTF stuff

mkdir -p /opt/CTFd/CTFd/themes/core/templates/cisco
for i in `ls -1 /opt/CloudCTF/CTFd/CTFd/plugins`; do
  ln -s /opt/CloudCTF/CTFd/CTFd/plugins/$i /opt/CTFd/CTFd/plugins/$i;
  TEMPLATE_DIR="/opt/CloudCTF/CTFd/CTFd/plugins/$i/templates"
  echo "template dir: $TEMPLATE_DIR"
  if [ -d $TEMPLATE_DIR ]
  then
      echo "[Cisco] Linking $TEMPLATE_DIR to /opt/CTFd/CTFd/themes/core/templates/cisco/$i"
      ln -s $TEMPLATE_DIR /opt/CTFd/CTFd/themes/core/templates/cisco/$i
  fi
  #pip install -r /opt/CloudCTF/CTFd/CTFd/plugins/$i/requirements.txt; \
done