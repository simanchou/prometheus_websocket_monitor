#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time       : 2017/11/29 15:42
# @Author     : 周星星 Siman Chou
# @Site       : https://github.com/simanchou
# @File       : export_pgateway.py
# @Description: monitor websocket by pushgateway of prometheus.Check the http status code, 101 is normal.


import requests
import websocket
import six
import time
import yaml
import os


def get_conf(file="export_pgateway.yml"):
    conf_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], file)
    if os.path.exists(conf_file):
        with open(conf_file, "r", encoding="utf-8") as fp:
            conf = yaml.load(fp.read())
        return conf
    else:
        print("Error,while loading conf file '{}'".format(file))
        return None


def get_ws_status(uri):
    #websocket.enableTrace(True)
    try:
        ws = websocket.create_connection(uri)
        code = ws.status
        ws.close(status=1000, reason=six.b("Connect from monitor by prometheus"))
        print("{:<40}\t{}\t{}".format(uri, code, time.asctime()))
        return code
    except:
        code = 0
        print("{:<40}\t{}\t{}".format(uri, code, time.asctime()))
        return code


def export_to_pushgateway(gateway, job, metric, group, instance, m_value):
    gw_url = "http://{}/metrics/job/{}/group/{}/instance/{}".format(gateway,
                                                                    job,
                                                                    group,
                                                                    instance.replace("//", "||"))
    data = "{}{} {}\n".format(metric, "{}", m_value)
    r = requests.put(gw_url, data=data)
    return r.text


if __name__ == "__main__":
    conf = get_conf()
    gateway = conf["global"]["gateway"]
    interval = conf["global"]["interval"]
    metric = "probe_http_status_code"

    # test
    #job = conf["target_configs"][0]["job"]
    #group = "url-monitor_hces888.com"
    #instance = "wss://bmsg.hces999.com:9508"
    #m_value = get_ws_status(instance)
    #r = export_to_pushgateway(gateway, job, metric, group, instance, m_value)
    #print(r)

    while True:
        for i in conf["target_configs"]:
            job = i["job"]
            for j in i["static_configs"]:
                group = j["group"]
                for instance in j["targets"]:
                    m_value = get_ws_status(instance)
                    export_to_pushgateway(gateway, job, metric, group, instance, m_value)
        time.sleep(interval)