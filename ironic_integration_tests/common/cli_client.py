"""
Copyright 2017 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import datetime
import logging
import os
import subprocess
import time

logfile = "ironic_tests_{0}.log".format(
    datetime.datetime.now().strftime("%y-%m-%d_%H-%M"))
log_format = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
logging.basicConfig(filename=logfile, format=log_format, level=logging.DEBUG)
LOG = logging.getLogger(__name__)


class CommandFailed(Exception):
    def __init__(self, message):
        super(CommandFailed, self).__init__(message)


class CLIClient(object):

    def execute_cmd(self, cmd, fail_ok=False):
        LOG.debug(cmd)
        env = os.environ.copy()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env)
        result, result_err = proc.communicate()

        if not fail_ok and proc.returncode != 0:
            LOG.error(result_err)
            raise CommandFailed("Command '{0}' failed: {1}".format(
                cmd, result_err))
        if fail_ok and proc.returncode != 0:
            LOG.debug(result_err)
            return result_err

        LOG.debug(result)
        return result

    def execute_w_retry(self, cmd, attempts=40, delay=15):
        attempt = 1
        last_exception = None
        while attempt <= attempts:
            try:
                result = self.execute_cmd(cmd)
                return result
            except CommandFailed as e:
                LOG.debug("Attempt {0} of command failed. "
                          "Retrying in {1} seconds...".format(
                            attempt, delay))
                last_exception = e
                attempt += 1
                time.sleep(delay)
        LOG.error(last_exception)
        raise last_exception
