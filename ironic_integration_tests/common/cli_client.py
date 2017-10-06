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
import os
import subprocess
import time

from ironic_integration_tests.common import output_parser as parser


class CommandFailed(Exception):
    def __init__(self, message):
        super(CommandFailed, self).__init__(message)


class CLIClient(object):

    def execute_cmd(self, cmd, fail_ok=False):
        env = os.environ.copy()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env)
        result, result_err = proc.communicate()

        if not fail_ok and proc.returncode != 0:
            raise CommandFailed("Command '{0}' failed: {1}".format(
                cmd, result_err))
        if fail_ok and proc.returncode != 0:
            return result_err

        print result
        return result

    def execute_w_retry(self, cmd, attempts=20, delay=15):
        attempt = 1
        last_exception = None
        while attempt <= attempts:
            try:
                result = self.execute_cmd(cmd)
                return result
            except CommandFailed as e:
                print "Attempt {0} of command failed. Retrying...".format(
                    attempt)
                last_exception = e
                attempt += 1
                time.sleep(delay)
        raise last_exception

    def wait_for_status(self, cmd, status_key, status_value):
        result = self.execute_cmd(cmd)
        resource = parser.details(result)
        attempts = 0
        while resource.get(status_key) != status_value and attempts < 20:
            if resource.get(status_key).lower() == "error":
                return resource
            attempts += 1
            time.sleep(15)
            result = self.execute_cmd(cmd)
            resource = parser.details(result)
        return resource

    def wait_for_deletion(self, cmd):
        attempts = 0
        try:
            while attempts < 20:
                self.execute_cmd(cmd)
                attempts += 1
                time.sleep(15)
        except CommandFailed:
            return
