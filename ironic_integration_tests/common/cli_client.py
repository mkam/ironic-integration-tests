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


class CLIClient(object):

    def execute_cmd(self, cmd, fail_ok=False):
        env = os.environ.copy()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env)
        result, result_err = proc.communicate()

        if not fail_ok and proc.returncode != 0:
            raise Exception("Command '{0}' failed: {1}".format(
                cmd, result_err))

        print result
        return result

    def wait_for_status(self, cmd, status):
        pass

    def wait_for_deletion(self):
        pass


