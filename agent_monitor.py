#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyrigth @ 2020 , Inc

""" The file is main enterance, it prepares env and init
"""

import sys, os, uuid
import time, threading
from optparse import OptionParser

import log
import __version__
import pppoe_dial
import agent_api
from net_flow import NetFlow

from daemon import Daemon

_u_id = uuid.uuid1()
_ppp_config_path = os.getcwd() + "/conf/ppp_configs"

def version():
  print("{}".format(__version__.__version__))

def handle_signal(option):
  if option == "start":
    _agent.start()
  elif option == "stop":
    _agent.stop()
  elif option == "restart":
    _agent.restart()
  else:
    print("agent-monitor: invalid option: '-s {}'".format(option))

def pppoe_run():
  log.logger.info("ppp_config_path {}".format(_ppp_config_path))
  pppoe_mgr = pppoe_dial.PPPoEManager(_ppp_config_path)
  while True:
    pppoe_mgr.on_timer()
    time.sleep(0.01)

def net_flow_run():
  net = NetFlow(_u_id)
  while True:
    net.on_timer()
    time.sleep(0.01)

class AgentMonitor(Daemon):
  def run(self):
    # pppoe dial
    pppoe_th = threading.Thread(target=pppoe_run)
    pppoe_th.start()
    # net flow
    net_flow_th = threading.Thread(target=net_flow_run)
    net_flow_th.start()

    while True:
      agent_api.load_ppp_config(_u_id, _ppp_config_path)
      time.sleep(20*60)

_agent_pid = os.getcwd() + "/agent-monitor.pid"
_agent = AgentMonitor(_agent_pid)

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-v", action="store_true", dest="verbose", help="show version")
  parser.add_option("-s", dest="signal", help="send signal process: start, stop or restart")
  parser.add_option("-u", dest="u_id", help="node unique indentification")
  (options, args)  =  parser.parse_args()
  if options.verbose:
    version()
  if options.u_id:
    _u_id = options.u_id
  if options.signal:
    handle_signal(options.signal)
