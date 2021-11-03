FROM ctfd/ctfd

COPY / /opt/CloudCTF

RUN pip install -r /opt/CloudCTF/requirements.txt && \
    for i in `ls -1 /opt/CloudCTF/CTFd/CTFd/plugins`; do \
      ln -s /opt/CloudCTF/CTFd/CTFd/plugins/$i /opt/CTFd/CTFd/plugins/$i; \
      #pip install -r /opt/CloudCTF/CTFd/CTFd/plugins/$i/requirements.txt; \
    done