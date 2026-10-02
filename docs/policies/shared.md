[](){#ref-policies-fair-use}
# Fair Usage of Shared Resources

[](){#ref-policies-fair-use-slurm}
## Slurm
The [Slurm][ref-slurm] scheduling system is a shared resource that can handle a limited number of batch jobs and interactive commands simultaneously. Therefore users should not submit hundreds of Slurm jobs and commands at the same time, as doing so would infringe our fair usage policy.

[](){#ref-policies-fair-use-login-node}
## Login nodes
Let us also remind you that **running compute or memory intensive applications on the login nodes is forbidden**. Please submit batch jobs with the Slurm scheduler, in order to allocate and run your processes on compute nodes: compute or memory intensive processes affecting the performance of login nodes will be terminated without warning.
We have enforced limits on the number of maximum logins, processes/threads, [CPU time](https://en.wikipedia.org/wiki/CPU_time) and amount of memory that can be used on the login nodes.
These limits are necessary because login nodes are shared resources used by many users simultaneously and are intended primarily for lightweight tasks such as connecting to the system, managing files, and submitting jobs.
Without appropriate limits, a single user or application can consume excessive resources, causing the login nodes to become slow, unresponsive, or even crash, which affects everyone using the system.
These safeguards help ensure that the login nodes remain stable, responsive, and available to all users, while resource-intensive workloads should be run through the appropriate compute resources.
If you encounter issues, please reach out to use to discuss your workflow in detail.

!!! Tip "Getting the current login node limits"
    To get the current limits, you must login to the login node and inspect the current limits
    In the example below the following limits apply:

    - at most 60 minutes CPU time
    - at most 5 logins
    - at most 1000 threads
    - at most 183868981248 bytes of memory (~170GB)
    - pinned to 48 cores

    ```console
    $ cat /etc/security/limits.conf | grep cpu
    1000:	hard	cpu	60
    $  cat /etc/security/limits.conf | grep login
    1000:	hard	maxlogins	5
    $ cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/pids.max
    1000
    $ cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/memory.max
    183868981248
    $ cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/cpuset.cpus.effective
    0,8,11-12,16,25,31,43,50,61-62,69,77,84,88,92,101,106,115,117,120,124,132,142,145,149,152,161,171,176,178,189,192,198-199,210,216,218,222,226-227,246,252,254-255,275,281,283
    ```

    Different limits might apply to different login nodes.

!!! Warning "Agents and VSCode are thread hungry"
    Please not that agentic tools (`claude`, `codex`, ...) and VSCode have been observed to be quite thread hungry.
    This means that you might hit the threads limit.
    Especially VSCode is known to leave old sessions running on the login node, leaving many threads open.
    To check the currently running threads, you can use the command (this is how a fresh SSH login should look like)

    ```console
    $ ps -eLf | grep $(id -un)
    alice    65923      1  65923  0    1 15:27 ?        00:00:00 /usr/lib/systemd/systemd --user
    alice    66055  65923  66055  0    1 15:27 ?        00:00:00 (sd-pam)
    alice    66202  65911  66202  0    1 15:27 ?        00:00:00 sshd: anfink@pts/9
    alice    66205  66202  66205  0    1 15:27 pts/9    00:00:00 -bash
    alice    95684  66205  95684  0    1 15:57 pts/9    00:00:00 ps -eLf
    alice    95685  66205  95685  0    1 15:57 pts/9    00:00:00 grep anfink
    ```
