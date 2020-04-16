"""Contains task functionality for executable-based tasks.

Note that none of these functions themselves are registered with Celery;
instead they are used by other functions which *are* registered with
Celery.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import json
import os
import git
import shlex
import subprocess
from .utils import create_local_directory

GIT_REPO = git.Repo(os.getcwd(), search_parent_directories=True)
GIT_ROOT = GIT_REPO.git.rev_parse("--show-toplevel")


def run_executable_command(uuid, command_to_run, env_vars_list, args_dict, json_file_option):
    """Launch an executable within a Docker container.

    Args:
        uuid: A string containing the uuid of the job being run.
        command_to_run: A string containing the command to run.
        env_vars_list: A list of strings containing the environment
            variable names for the worker to consume from its
            environment.
        args_dict: A dictionary containing arguments and corresponding
            values.
        json_file_option: A string (or None) containing the name of the
            command line option to specify a JSON-encoded file to read
            from.

    Raises:
        KeyError: An environment variable specified was not available in
            the worker's environment.
        subprocess.CalledProcessError: The process returned with a
            non-zero code.
    """
    # Set up the host log directory for the job
    host_logs_path = os.path.join(os.environ["WORKER_LOGS_DIRECTORY"], uuid)

    create_local_directory(host_logs_path)

    # Build paths to stdout and stdin files
    host_stdout_log_path = os.path.join(host_logs_path, uuid + "-" + "stdout.txt")

    host_stderr_log_path = os.path.join(host_logs_path, uuid + "-" + "stderr.txt")

    # Consume necessary environment variables
    try:
        environment = {key: os.environ[key] for key in env_vars_list}
    except KeyError as e:
        raise KeyError("Environment variable %s not present in the worker's environment!" % e)

    # Also pass along the job's UUID
    environment["JOB_UUID"] = uuid

    # And PATH
    try:
        environment["PATH"] = os.environ["PATH"]
    except KeyError:
        # Okay, no path defined. No big deal
        pass

    # Interpret the command to run: split the string into
    # substrings "naturally" (see Python's shlex library); and
    # try to process anything that looks like an environment
    # variable.
    command_to_run = os.path.expandvars(command_to_run)
    cmd_list = shlex.split(command_to_run)

    # Add in arguments. Option 1: the task type wants to read the
    # arguments for a file; in this case we'll write the arguments to a
    # file and pass it to the specified json_file_option. Option 2: we
    # pass in the arguments JSON on the command line directly. Option 3:
    # there are no arguments, so we don't bother giving the command
    # anything.
    temp_files_to_clean_up = []

    if args_dict:
        if json_file_option:
            # Write the the JSON args to a file, and then pass them
            # along to the command after the flag
            json_file_path = os.path.join(os.environ["WORKER_TEMP_DIRECTORY"], uuid + "_args.json")

            with open(json_file_path, "w") as f:
                print(json.dumps(args_dict), file=f)

            cmd_list += [json_file_option, json_file_path]

            # Clean up the temp file after we're done with it
            temp_files_to_clean_up += [json_file_path]

        else:
            # check if jira in args
            # this determines if task is to run analysis
            # and adds args to command such that cmd is
            # compatiable with click
            if 'jira' in args_dict:
                cmd_list += [
                    str(args_dict['analysis_id']),
                    "--saltant",
                ]

                if 'update' in args_dict:
                    cmd_list += ["--update"]

                if 'skip_missing' in args_dict:
                    cmd_list += ["--skip_missing"]

                if 'rerun' in args_dict:
                    # remove pipeline dir
                    subprocess.check_call([
                        'sudo',
                        'rm',
                        '-rf',
                        os.path.join(
                            GIT_ROOT,
                            'singlecelllogs',
                            'pipeline',
                            f"analysis_{args_dict['analysis_id']}",
                        ),
                    ])

                    # remove temp dir
                    subprocess.check_call([
                        'sudo',
                        'rm',
                        '-rf',
                        os.path.join(
                            GIT_ROOT,
                            'singlecelltemp',
                            'temp',
                            f"analysis_{args_dict['analysis_id']}",
                        ),
                    ])

            else:
                # Pass in JSON args directly
                cmd_list += [json.dumps(args_dict)]

    # Run the command
    try:
        with open(host_stdout_log_path, "w") as f_stdout:
            with open(host_stderr_log_path, "w") as f_stderr:
                print("cmd: {}".format(cmd_list), file=f_stdout)
                # Run command
                subprocess.check_call(
                    args=cmd_list,
                    stdout=f_stdout,
                    stderr=f_stderr,
                    env=environment,
                )
    finally:
        # Clean up any temp files
        for temp_file in temp_files_to_clean_up:
            os.remove(temp_file)
