[](){#ref-policies}

# CSCS User Policies

The CSCS [code of conduct](code-of-conduct.md) outlines the responsibilities and proper practices for the CSCS user community.

The [User Regulations][ref-policies-user-regulations] define the basic guidelines for the usage of CSCS computing resources. The right to access CSCS resources may be revoked to whoever breaches any of the user regulations.

The [User Support Policies](support.md), the [Slack Code of Conduct](slack.md) and the [Scheduled Maintenance and System Unavailability Policies](maintenance.md) provide additional information on support services, the regulations of the Users Slack space and the scheduled maintenance events.

## Resource Allocation Policies 

Compute time on Alps systems is measured in node hours. Currently, we only support exclusive node allocations. This means that even if you utilize only a portion of a node’s resources (e.g., a single GPU), your account will still be charged for the entire node.

Please note that resources at CSCS are assigned over three-months windows

* Quotas are reset on April 1st, July 1st, October 1st and January 1st
* Please make sure to use thoroughly your quarterly compute budget within the corresponding time frame
* Resources unused in the three-month periods are not transferred to the next allocation period but are forever lost

## Data Retention Policies

Data belonging to active projects in the filesystems `/users` and `/capstor/store` are under backup. There is no backup for data under the scratch filesystem, therefore no data recovery is possible in case of accidental loss or for data deleted due to the cleaning policy implemented on this filesystem.

Please note that the long term storage service is granted as long as your project is active, and the data will be removed without further notice 3 months after the expiration of the project: please check the applicable filesystem policies for the grace period granted after the expiration of the project.

Furthermore, as soon as your project expires, the backup of the data belonging to the project will be disabled immediately: therefore no data backup will be available after the final data removal.

[](){#ref-policies-fair-use}
## Fair Usage of Shared Resources

The [Slurm][ref-slurm] scheduling system is a shared resource that can handle a limited number of batch jobs and interactive commands simultaneously. Therefore users should not submit hundreds of Slurm jobs and commands at the same time, as doing so would infringe our fair usage policy.

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
    anfink    65923      1  65923  0    1 15:27 ?        00:00:00 /usr/lib/systemd/systemd --user
    anfink    66055  65923  66055  0    1 15:27 ?        00:00:00 (sd-pam)
    anfink    66202  65911  66202  0    1 15:27 ?        00:00:00 sshd: anfink@pts/9
    anfink    66205  66202  66205  0    1 15:27 pts/9    00:00:00 -bash
    anfink    95684  66205  95684  0    1 15:57 pts/9    00:00:00 ps -eLf
    anfink    95685  66205  95685  0    1 15:57 pts/9    00:00:00 grep anfink
    ```

