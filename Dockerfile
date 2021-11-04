FROM ctfd/ctfd

COPY / /opt/CloudCTF

RUN pip install -r /opt/CloudCTF/requirements.txt && \
    /bin/bash /opt/CloudCTF/build_scripts/setup_cisco_ctfd.sh
  # && \
#    chown 1001:1001 /opt/CloudCTF/CTFd/CTFd/config.ini && \
#    rm /opt/CTFd/CTFd/config.ini && \
#    ln -s /opt/CloudCTF/CTFd/CTFd/config.ini /opt/CTFd/CTFd/config.ini