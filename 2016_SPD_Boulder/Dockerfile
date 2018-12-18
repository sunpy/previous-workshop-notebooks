FROM andrewosh/binder-base

USER main

RUN conda create -y -c conda-forge -n sunpy python=3.5 sunpy jupyter
RUN /bin/bash -c "source activate sunpy && ipython kernel install --user"
