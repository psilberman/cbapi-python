#!/usr/bin/env python

import json

from cbapi.response.models import Sensor

from cbapi.example_helpers import build_cli_parser, get_cb_response_object
from cbapi.errors import ServerError

import logging

class InventoryProcessor():

    def __init__(self,cbapi):
        self.cb = cbapi 

    def sensor_lookup(self,line):
        sensor = None
        line_json = json.loads(line)
        if "sensor_id" in line_json:
            sensor = self.cb.select(Sensor,line_json['sensor_id'])
        elif 'ip' in line_json:
            sensor = self.cb.select(Sensor).where("ip:"+line_json['ip']).first()
        elif 'host' in line_json:
            sensor = self.cb.select(Sensor).where("hostname:"+line_json['host']).first()
        elif 'mac' in line_json:
            sensors = self.cb.select(Sensor)
            for s in sensors:
                for nic in s.network_interfaces:
                    if nic.macaddr == line_json['mac']:
                        sensor = s
        if sensor:
            line_json["sensor_id"]=sensor.id

        return json.dumps(line_json)+"\n" 

    def process_inventory(self,inventory,verbose=False):
        writelines = []
        with open(inventory,"r") as inventory_file:
            lines = inventory_file.readlines() 
            writelines = map(self.sensor_lookup,lines)
        with open(inventory+".out","w") as inventory_file:
            inventory_file.writelines(writelines)

def main():
    parser = build_cli_parser()
    parser.add_argument("-i","--inventory",action="store",help="Inventory",dest="inventory",required=True)
    args = parser.parse_args()
    cb = get_cb_response_object(args)
    ip = InventoryProcessor(cbapi=cb) 
    ip.process_inventory(inventory = args.inventory)
    
if __name__=="__main__":
    main()

