#!/usr/bin/python

import paramiko

DEFAULT_USERNAME = 'root'
DEFAULT_KEY_FILE = '/Users/youpengfei/.ssh/id_aliyun'


def trans_data(hostname, key_file=DEFAULT_KEY_FILE, remote_path=None, local_path=None):
    t = paramiko.Transport(hostname, 22)
    key = paramiko.RSAKey.from_private_key_file(key_file)
    t.connect(username=DEFAULT_USERNAME, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.put(local_path, remote_path)
    t.close()


def command_with_result(hostname, key_file=DEFAULT_KEY_FILE, command=None):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, 22, DEFAULT_USERNAME, key_filename=key_file)
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.readlines()
    finally:
        ssh.close()


#
# rem = ParamikoMachine(host="115.28.105.10", keyfile='/Users/youpengfei/.ssh/id_aliyun', user='root')
# path = rem.path("test.sh")
# print(path.write("echo hello"))
# print rem.session().run('chmod 755 %s' % str(path) )

# print path.chmod(0755)


def escapeshellarg(arg):
    return "\\'".join("'" + p + "'" for p in arg.split("'"))
