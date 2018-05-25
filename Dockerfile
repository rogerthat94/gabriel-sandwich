FROM cmusatyalab/gabriel
MAINTAINER Satyalab, satya-group@lists.andrew.cmu.edu

WORKDIR /
RUN git clone https://github.com/cmusatyalab/gabriel-sandwich.git

EXPOSE 7070 9098 9111
CMD ["bash", "-c", "gabriel-control -n eth0 -l & sleep 5; gabriel-ucomm -s 127.0.0.1:8021 & sleep 5; cd /gabriel-sandwich && python proxy.py -s 127.0.0.1:8021"]
