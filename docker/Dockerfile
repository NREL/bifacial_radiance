FROM python:3.7.8-buster
RUN apt-get update && apt-get install apt-utils wget curl git libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6 -qq 

WORKDIR /conda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN /bin/bash Miniconda3-latest-Linux-x86_64.sh -b
RUN rm -rf Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/root/miniconda3/bin:$PATH CONDA_ENV=py38
RUN /root/miniconda3/bin/conda create -y --prefix=$PWD/$CONDA_ENV python=3.8
RUN conda init
RUN . activate $PWD/$CONDA_ENV
RUN conda install dask distributed
RUN pip install dask distributed --upgrade
RUN curl -L -s https://github.com/NREL/Radiance/releases/download/5.2/radiance-5.2.dd0f8e38a7-Linux.tar.gz | tar xvz \
    && mv radiance-*/usr/local/radiance radiance ;\
    rm -rf radiance-*
RUN git clone https://github.com/NREL/bifacial_radiance.git -b development \
    && cd bifacial_radiance \
    && pip install . \
    && cp bifacial_radiance/data/gencumulativesky ../radiance/bin/ \
    && mv bifacial_radiance/HPCScripts/BasicSimulati* ../HPCScripts ;\
    rm -rf ../bifacial_radiance
ENV PATH="$PATH:/conda/radiance/bin" LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/conda/radiance/lib" RAYPATH="$RAYPATH:/conda/radiance/lib"
RUN chmod -Rv ugo+rx radiance/bin/*