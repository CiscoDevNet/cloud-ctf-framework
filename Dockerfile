FROM ctfd/ctfd

COPY / /opt/CloudCTF

RUN for i in `ls -1 /opt/CloudCTF/CTFd/CTFd/plugins`; do ln -s /opt/CloudCTF/CTFd/CTFd/plugins/$i /opt/CTFd/CTFd/plugins/$i; done