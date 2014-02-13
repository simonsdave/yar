# sudo docker build -t key_server_img .
# KS1=$(sudo docker run -name key_server_001 -d key_server_img)
# KS1_IP=$(sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $KS1)

FROM yar_img

MAINTAINER Dave Simons

EXPOSE 8070

CMD ["--lon=8070", "--log=info"]

USER daemon

ENTRYPOINT key_server
