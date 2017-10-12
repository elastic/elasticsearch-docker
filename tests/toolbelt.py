from subprocess import run, PIPE
import os


def exec_privilege_escalated_command(exec_string, *bindmounts):
    """Function to simulate sudo <command> by bind-mounting affected paths
       though docker.
       bindmounts is a list of `-v` style docker args
       e.g. `/home/user/elasticsearch-docker/tests/datadir1:/datadir1`
    """
    bind_mount_cli_args = []
    for bindarg in bindmounts:
        bind_mount_cli_args.append('-v')
        bind_mount_cli_args.append(bindarg)

    proc = run(
        ['docker', 'run', '--rm'] +
        bind_mount_cli_args +
        ['alpine', '/bin/sh', '-c', exec_string],
        stdout=PIPE)
    return proc


def create_empty_dir(path, uid, gid):
    parent_dir = os.path.dirname(os.path.abspath(path))
    base_newdir = os.path.basename(os.path.normpath(path))

    proc = exec_privilege_escalated_command(
        'mkdir /mount/{0} && chown {1}:{2} /mount/{0} && chmod 0770 /mount/{0}'.format(base_newdir, uid, gid),
        parent_dir + ":" + "/mount"
    )

    if proc.returncode != 0:
        print("Unable to mkdir: {}".format(path))

    return proc


def delete_dir(path):
    parent_dir = os.path.dirname(os.path.abspath(path))
    basedir_parent = os.path.basename(os.path.normpath(parent_dir))
    basedir = os.path.basename(os.path.normpath(path))

    proc = exec_privilege_escalated_command(
        'cd /mount/{0} && rm -rf {1}'.format(basedir_parent, basedir),
        parent_dir + ":" + "/mount/{}".format(basedir_parent)
    )

    if proc.returncode != 0:
        print("Unable to delete: {}".format(path))

    return proc


def recursive_chown(path, uid, gid):
    parent_dir = os.path.dirname(os.path.abspath(path))
    basedir_parent = os.path.basename(os.path.normpath(parent_dir))
    basedir = os.path.basename(os.path.normpath(path))

    proc = exec_privilege_escalated_command(
        'cd /mount/{0} && chown -R {1}:{2} {3} '.format(basedir_parent, uid, gid, basedir),
        parent_dir + ":" + "/mount/{}".format(basedir_parent)
    )

    if proc.returncode != 0:
        print("Unable to delete: {}".format(path))

    return proc
