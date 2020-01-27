# -*- coding: utf-8 -*-

from polylogyx.application import create_app
from polylogyx.settings import CurrentConfig
from polylogyx.tasks import pull_and_match_with_rules
import threading

app = create_app(config=CurrentConfig)

thread_count = 1
for i in range(thread_count):
    t = threading.Thread(target=pull_and_match_with_rules)
    t.start()

