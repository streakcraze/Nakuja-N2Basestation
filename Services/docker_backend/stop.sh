cd /home/pi/NakujaN2/n2Basestation/Services/docker_backend/

if [ "$(docker ps -f name=nakuja -l -q)" != "" ]
then
    make stop
else
    echo "No containers"
fi
