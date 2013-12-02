import subprocess

from plugin import CommandPlugin


class PythonSandbox(CommandPlugin):
    name = "Python Sandbox"
    description = "Provides a Python Sandbox for users to play around with. Implemented using PyPy."

    def activate(self):
        print "Got to activate in PythonSandbox"
        super(PythonSandbox, self).activate()
        self.commands = {
            "py": self.pypy_sandbox
        }

    def pypy_sandbox(self, user, channel, parameters):
        print "Got here"
        unsafe_code = ' '.join(parameters)
        filename = "sandboxed.py"
        with open('%s/sandboxed.py' % self.config['tmp_dir'], 'w') as f:
            f.write(unsafe_code)
        output = subprocess.check_output(
            'ulimit -t 2; nice -n 15 pypy-sandbox --tmp=/home/ankhmorporkian/virtualtmp /tmp/execfile.py', shell=True)
        print output
        output = ' '.join(output.split("\n"))
        if len(output) > 350:
            output = output[0:350]
        self.bot.msg(channel, output)