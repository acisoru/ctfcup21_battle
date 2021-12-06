FROM keltecc/nsjail:latest

RUN apt update

RUN useradd -M -s /bin/false ctf

COPY entrypoint.sh /tmp/

RUN chmod 555 /tmp/entrypoint.sh

COPY datasaver flag.txt ld-linux-x86-64.so.2 /var/service/
COPY libs/ /var/service/libs
COPY flag.txt /tmp/

RUN chmod ugo+r /tmp/flag.txt && chmod ugo-wx /tmp/flag.txt
RUN chmod ugo+r /var/service/flag.txt && chmod ugo-wx /var/service/flag.txt
RUN chmod ugo+rx /var/service/ld-linux-x86-64.so.2 && chmod ugo-w /var/service/ld-linux-x86-64.so.2
RUN chmod ugo+rx /var/service/datasaver && chmod ugo-w /var/service/datasaver
RUN chmod ugo+rx /var/service/libs/* && chmod ugo-w /var/service/libs/*

USER ctf

ENTRYPOINT /tmp/entrypoint.sh
