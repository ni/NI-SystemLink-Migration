from slmigrate import constants
from distutils import dir_util
import json, subprocess, os, sys, shutil


def stop_sl_service(service):
    if service.require_service_restart:
        print("Stopping " +  service.service_to_restart + " service")
        subprocess.run(constants.slconf_cmd_stop_service + service.service_to_restart + " wait")
    
def start_all_sl_services(service):
    if service.require_service_restart:
        print ("Starting " + service.service_to_restart + " service")
        subprocess.run(constants.slconf_cmd_start_all)