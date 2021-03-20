FROM gitpod/workspace-full

USER gitpod

# SSH Server
# -------------------------------------------------------------------------------------------------

USER root

# Update
RUN apt-get update -yq

# Install Dropbear SSH server
RUN DEBIAN_FRONTEND=noninteractive apt-get install -yq \
        dropbear \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/*

# Install Chisel
RUN curl https://i.jpillora.com/chisel! | bash

USER gitpod

# Application dependencies
# -------------------------------------------------------------------------------------------------

RUN pip install git+https://git@github.com/tcosta84/python-lojaintegrada.git
