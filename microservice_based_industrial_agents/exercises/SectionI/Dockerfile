FROM ubuntu:20.04
RUN apt update && apt install -y python3-pip 
RUN pip3 install psutil
COPY my_program.py /
CMD ["python3", "-u", "my_program.py"]
