FROM freesurfer/freesurfer:7.1.1

# shell settings
WORKDIR /

# install utils
RUN yum -y update
RUN yum -y install bc libgomp perl tar tcsh wget vim-common
RUN yum -y --enablerepo=extras install epel-release
RUN yum -y update
RUN yum clean all && yum -y install libXmu libXrender libXext libSM ImageMagick glx-utils mesa-libGLU mesa-libGL mesa-libGLU-devel mesa-libGL-devel mesa-dri-drivers mesa-private-llvm libXmu libXmu-devel libX11 libX11-devel libXt-devel xorg-x11-server-Xorg xorg-x11-server-Xvfb mesa-libxatracker xorg-x11-drivers xorg-x11-drv-vmware qt-x11 libXScrnSaver dbus qt GConf2 qt5-qtx11extras
RUN yum clean all

# Copy in the license file
COPY license.txt /usr/local/freesurfer/license.txt

# Update packages and download PUP
RUN yum -y --enablerepo=extras install epel-release
RUN yum -y update
RUN rpm --rebuilddb && yum -y --enablerepo=extras install curl zip unzip tar tcsh make cpp gcc-c++ gcc gcc-gfortran dbus libgomp netcdf netcdf-devel perl perl-core bc java gunzip

# Download PUP repo from github
RUN curl -LO https://github.com/ysu001/PUP/archive/master.zip
RUN unzip master.zip

RUN mkdir -p /4dfp
RUN mkdir -p /pup

RUN cp -r /PUP-master/* /pup/.

# Compile 4dfp tools
ENV NILSRC /pup/4dfp
ENV RELEASE /4dfp
ENV OSTYPE "linux"

RUN /bin/tcsh -c ./pup/4dfp/make_nil-tools.csh

# Build PUP tools
RUN /bin/tcsh -c "cd /pup/src; make release ALL"

# Copy in the ROIs file
RUN cp /pup/ROIs /pup/ROIs_orig
RUN rm /pup/ROIs
COPY ROIs_fs711 /pup/ROIs_fs711
COPY ROIs_fs53 /pup/ROIs_fs53

# Copy in the Freesurfer lookup tables for each version.
RUN cp /usr/local/freesurfer/FreeSurferColorLUT.txt /usr/local/freesurfer/FreeSurferColorLUT_orig.txt
RUN rm /usr/local/freesurfer/FreeSurferColorLUT.txt
COPY FreeSurferColorLUT_fs711.txt /usr/local/freesurfer/FreeSurferColorLUT_fs711.txt
COPY FreeSurferColorLUT_fs53.txt /usr/local/freesurfer/FreeSurferColorLUT_fs53.txt

# install ecat tools
RUN rpm --rebuilddb && yum -y --enablerepo=extras install autoconf m4 patch
RUN tar -xzvf /pup/4dfp/ecat/libecat7-1.5.tgz -C /pup/4dfp/ecat

# Build ecat tools
RUN /bin/tcsh -c "cd /pup/4dfp/ecat/libecat7-1.5; ./configure; make"
RUN /bin/tcsh -c "cd /pup/4dfp/ecat; make -f ecatto4dfp.mak"
RUN /bin/tcsh -c "cd /pup/4dfp/ecat; make -f ecat_header.mak"

RUN yum -y install python3 python3-pip openssl-devel
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir datetime lxml numpy matplotlib requests

# Update OS
RUN yum -y update && \
    yum --enablerepo=extras install epel-release -y && \
    yum install -y wget zip unzip && \
    yum install -y epel-release && \
    yum install -y python-pip && \
    yum install -y python3-pip

# Install QMENTA SDK
RUN pip3 install qmenta-sdk-lib

# Copy look up tables
RUN mkdir -p /pup/lut
COPY pet.lkup /pup/lut

RUN mkdir -p /pup/config
COPY pup_plot_fs.config /pup/config

# Create input and output folders for QMENTA
RUN mkdir -p /root/INPUT
RUN mkdir -p /root/OUTPUT
RUN mkdir -p /data/input/params
RUN mkdir -p /data/input/PET
RUN mkdir -p /data/input/FreeSurfer

# Configure cshrc to source SetUpFreeSurfer.csh
RUN /bin/tcsh -c 'echo -e "source $FREESURFER_HOME/SetUpFreeSurfer.csh &>/dev/null" >> /root/.cshrc '

ENV PATH /pup/scripts:/pup/src:/pup/4dfp/ecat:/pup/4dfp/ecat/libecat7-1.5:/4dfp:/usr/local/freesurfer/bin:/usr/local/freesurfer/fsfast/bin:/usr/local/freesurfer/tktools:/usr/local/freesurfer/mni/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

COPY FreeSurferColorLUT_fs720.txt /usr/local/freesurfer/FreeSurferColorLUT_fs720.txt

# Add tool script
COPY tool.py /root/tool.py
COPY entrypoint.sh /root/entrypoint.sh
COPY rootpetproc.sh /root/rootpetproc.sh

# Configure entrypoint
RUN python3 -m qmenta.sdk.make_entrypoint /root/entrypoint.sh /root/
RUN chmod +x /root/entrypoint.sh
RUN chmod +x /root/rootpetproc.sh