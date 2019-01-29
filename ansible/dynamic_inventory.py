#!/usr/bin/python
#Author Jeganathan Swaminathan <jegan@tektutor.org> <http://www.tektutor.org>

import subprocess
import json
from os.path import expanduser

def executeDockerCommand(*args):
    return subprocess.check_output(["docker"] + list(args)).strip()

def docker_inspect(fmt, mcn):
    return executeDockerCommand("inspect", "-f", fmt, mcn)

def docker_port(machine):
       return "22"

def get_host_vars(m):
    home = expanduser("~")
    ip = [docker_inspect("{{.NetworkSettings.IPAddress}}", m)]
    name = docker_inspect("{{.Name}}", m)[1:]
    publishedPort = docker_port(m)

    ssh_vars = {
        "ansible_port": publishedPort,
        "ansible_private_key_file": home+ "/.ssh/" + "id_rsa",
        "ansible_user": "root",
        "ansible_become_user": "root",
        "ansible_become_password": "root",
    }

    if ( publishedPort == "22" ):
        ssh_vars.update({"ansible_host": docker_inspect("{{.NetworkSettings.IPAddress}}", m) })
    else:
        ssh_vars.update({"ansible_host": "localhost"})
    ssh_vars.update({"ansible_dynamic_hostname": name})
    hostConnectionDetails = {"hosts": ip, "vars": ssh_vars}
    return hostConnectionDetails

class DockerInventory():
      def __init__(self):
          self.inventory = {} # Ansible Inventory

          machines = executeDockerCommand("ps", "-q").splitlines()
          json_data = {m: get_host_vars(m) for m in machines}

          print json.dumps(json_data,indent=4,sort_keys=True)

DockerInventory()
