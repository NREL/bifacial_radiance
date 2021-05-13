## Run TKinter GUI from within Docker Container

### Windows
Currently unsupported

### Linux
Execute this block within a shell:
```sh
ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
xhost + $ip
docker run -it -e DISPLAY=$ip:0 -v /tmp/.X11-unix:/tmp/.X11-unix bifipv python -c "import bifacial_radiance; bifacial_radiance.gui()"
```

### macOS
Make sure you have XQuartz installed and running prior to launching the container.

For detailed guidance consult: https://fredrikaverpil.github.io/2016/07/31/docker-for-mac-and-gui-applications/

Once XQuartz is installed, execute this block within a shell:
```sh
ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
xhost + $ip
docker run -it -e DISPLAY=$ip:0 -v /tmp/.X11-unix:/tmp/.X11-unix bifipv python -c "import bifacial_radiance; bifacial_radiance.gui()"
```