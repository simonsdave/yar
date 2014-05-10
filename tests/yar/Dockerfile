# this Dockerfile creates a base image for all yar servers
# all the python pre-reqs are installed and the yar package
# is also installed
#
# to build the image
#
#   sudo docker build -t yar_img .
#
# useful for interactive testing/debugging
#
#   sudo docker run -i -t yar_img /bin/bash

FROM yarbase_img

MAINTAINER Dave Simons

# :TRICKY: ADD command decompresses the archive and extracts
# all the files in the archive
ADD artifacts/yar-1.0.tar.gz /tmp/.

RUN pip install /tmp/yar-1.0
