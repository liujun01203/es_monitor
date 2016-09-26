es_monitor
---


* Depends:
    * 
    * 

* Deploy
    * cd es_monitor/
    * virtualenv .venv
    * source .venv/bin/activate
    * pip install setuptools -U
    * pip install pip -U
    * pip install -e .

* Config
    * file: /etc/es_monitor/monitor.conf

* Run
    * es-monitor

* Test
    * ./run_tests.sh

