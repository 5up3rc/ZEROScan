#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import json
import re

from lib.core import logger
from lib.thirdparty import requests
from lib.thirdparty.threadpool import threadpool

author = "Z3r0yu"
scope = "All CMS"
description = "CMS 识别"
reference = "http://zeroyu.xyz/"
options = [
    {
        "Name": "URL",
        "Current Setting": "",
        "Required": True,
        "Description": "网站地址"
    },
    {
        "Name": "Thread",
        "Current Setting": "50",
        "Required": True,
        "Description": "线程数"
    },
]


class WhatWeb(object):
    """
    CMS 识别
    """

    def __init__(self, url, thread_num):
        with open("data/whatweb.json") as f:
            self.rules = json.load(f)
        self.url = url
        self.thread_num = thread_num
        self.result = ""

    def identify_cms(self, cms):
        """
        识别 CMS
        :param cms: str, CMS 名称
        :return: str, CMS 名称
        """
        for rule in self.rules[cms]:
            try:
                headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.0.1471.914 Safari/537.36'}
                r = requests.get(self.url + rule["url"],headers=headers,timeout=5)
                r.encoding = r.apparent_encoding
                r.close()
                if ("md5" in rule
                    and hashlib.md5(r.content).hexdigest() == rule["md5"]) \
                        or ("field" in rule and rule["field"] in r.headers
                            and rule["value"] in r.headers[rule["field"]]) \
                        or ("head" in rule and rule["head"] in r.headers)\
                        or ("text" in rule and rule["text"] in r.text) \
                        or ("regexp" in rule
                            and re.search(rule["regexp"], r.text)):
                    return cms

            except Exception:
                pass

    def log(self, request, result):
        """
        线程池的 callback
        :return:
        """
        if result:
            self.result = "%s: %s" % (self.url, result)
            logger.success(self.result)
            raise threadpool.NoResultsPending

    def run(self):
        """
        多线程
        :return:
        """
        pool = threadpool.ThreadPool(self.thread_num)
        reqs = threadpool.makeRequests(self.identify_cms, self.rules, self.log)
        for req in reqs:
            pool.putRequest(req)
        pool.wait()


def exploit(URL, Thread):
    w = WhatWeb(URL, Thread)
    w.run()
    if w.result:
        return w.result
