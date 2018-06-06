# Overview [![Docker Image Status][docker-image]][docker] [![License][license-image]][license]

Cognitive Assistance for making a sandwich. Click below for the demo video.

[![Demo Video](https://img.youtube.com/vi/USakPP45WvM/0.jpg)](https://www.youtube.com/watch?v=USakPP45WvM)

[docker-image]: https://img.shields.io/docker/build/cmusatyalab/gabriel-sandwich.svg
[docker]: https://hub.docker.com/r/cmusatyalab/gabriel-sandwich

[license-image]: http://img.shields.io/badge/license-Apache--2-blue.svg?style=flat
[license]: LICENSE

# Installation
Running the application using Docker is advised. If you want to install from source, please see [Dockerfile](Dockerfile) for details.

# How to Run
## Client
Run Gabriel's [legacy Android Client](https://github.com/cmusatyalab/gabriel/tree/master/client/legacy-android-client). You'll need Android Studio to compile and install the apk.
Make sure to change IP address of GABRIEL_IP variable at src/edu/cmu/cs/gabriel/Const.java to point to your server.

## Server
### Container
```bash
nvidia-docker run --rm -it --name sandwich \
-p 0.0.0.0:9098:9098 -p 0.0.0.0:9111:9111 -p 0.0.0.0:22222:22222 \
-p 0.0.0.0:8080:8080 \
cmusatyalab/gabriel-sandwich:latest
```
