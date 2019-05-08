FROM lavasoftware/amd64-lava-dispatcher:2019.01

# install snmp package
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-add-repository non-free
RUN apt-get update
RUN apt-get install -y snmp snmp-mibs-downloader lava-lxc-mocker python3-serial
RUN download-mibs

# Add MIBs
RUN mkdir -p /usr/share/snmp/mibs/
ADD powernet428.mib /usr/share/snmp/mibs/

# Add lab scripts
RUN mkdir -p /usr/local/lab-scripts/
ADD https://git.linaro.org/lava/lava-lab.git/plain/shared/lab-scripts/snmp_pdu_control /usr/local/lab-scripts/
RUN chmod a+x /usr/local/lab-scripts/snmp_pdu_control
ADD https://git.linaro.org/lava/lava-lab.git/plain/shared/lab-scripts/eth008_control /usr/local/lab-scripts/
RUN chmod a+x /usr/local/lab-scripts/eth008_control

ADD power_control.py /usr/local/lab-scripts/
RUN chmod a+x /usr/local/lab-scripts/power_control.py
