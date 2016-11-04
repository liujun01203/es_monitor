es_monitor
----------
* Env
    *Python 2.7.6

* Depends:
    * oslo.config
    * oslo.service
    * elasticsearch

* Deploy
    * cd es_monitor/
    * virtualenv .venv
    * source .venv/bin/activate
    * pip install setuptools -U
    * pip install pip -U
    * pip install -e .

* Config
    * file: /etc/es_monitor/monitor_agent.conf

* Run
    * monitor_agent

* Test

