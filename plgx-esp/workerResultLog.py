# -*- coding: utf-8 -*-

from polylogyx.application import create_app
from polylogyx.settings import CurrentConfig
from polylogyx.tasks import analyse_result_log_data_with_rule_ioc_intel
import threading

app = create_app(config=CurrentConfig)
def match_with_rules():
        while True:
              print('executing and matching with rules...')

              task=analyse_result_log_data_with_rule_ioc_intel.apply_async(queue='default_queue_tasks')
              task.get()
              print('execution finished...')
thread_count =1
for i in range(thread_count):
    t = threading.Thread(target=match_with_rules)
    t.start()
