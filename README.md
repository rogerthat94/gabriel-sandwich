# Overview [![Docker Image Status][docker-image]][docker] [![License][license-image]][license]

Cognitive Assistance for making a sandwich. Click below for the demo video. This cognitive assistance is designed for this [Sandwich kit](https://www.amazon.com/Small-World-Toys-Living-Sandwich/dp/B00004W156).

[![Demo Video](https://img.youtube.com/vi/USakPP45WvM/0.jpg)](https://www.youtube.com/watch?v=USakPP45WvM)

[States and transitions](https://docs.google.com/drawings/d/15wmevFqD2FE_dqVGJI0EU3L5igNC6SEnNhNdw40KNkI)

[docker-image]: https://img.shields.io/docker/build/cmusatyalab/gabriel-sandwich.svg
[docker]: https://hub.docker.com/r/cmusatyalab/gabriel-sandwich

[license-image]: http://img.shields.io/badge/license-Apache--2-blue.svg?style=flat
[license]: LICENSE

# Installation
## Client
An Android client is available on [Google Play](https://play.google.com/store/apps/details?id=edu.cmu.cs.gabrielclient). The source code is available [here](https://github.com/cmusatyalab/gabriel-instruction/tree/master/android-client).

## Server
Running the server application using Docker is advised. If you want to install from source, please see [Dockerfile](Dockerfile) for details.


# How to Run
## Client
From the main activity one can add servers by name and IP/domain. Subtitles for audio feedback can also been toggled. This option is useful for devices that may not have integrated speakers (like ODG R-7).
Pressing the 'Play' button next to a server will initiate a connection to the Gabriel server at that address.

## Server
### Container
```bash
docker run --rm -it --gpus all -p 9099:9099 cmusatyalab/gabriel-sandwich:latest
```
