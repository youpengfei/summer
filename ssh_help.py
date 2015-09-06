#!/usr/bin/python

import paramiko

DEFAULT_USERNAME = 'tomcat'


def trans_data(hostname, key_file, remote_path, local_path):
    t = paramiko.Transport((hostname, 22))
    key = paramiko.RSAKey.from_private_key_file(key_file)
    t.connect(username=DEFAULT_USERNAME, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.put(local_path, remote_path)
    t.close()


def command(hostname, key_file, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, 22, DEFAULT_USERNAME, key_filename=key_file)
    stdin, stdout, stderr = ssh.exec_command(command)
    if not stderr.readlines():
        print stdout.readlines()
    ssh.close()


if __name__ == '__main__':
    trans_data()
