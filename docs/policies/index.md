# CSCS User Policies

The CSCS [code of conduct](code-of-conduct.md) outlines the responsibilities and proper practices for the CSCS user community.

The [User Regulations](regulations.md) define the basic guidelines for the usage of CSCS computing resources. The right to access CSCS resources may be revoked to whoever breaches any of the user regulations.

## Computing Budget

Compute time on Alps systems is accounted in node hours; computing time on CSCS systems that allow node sharing will be accounted in core hours.

Please note that resources at CSCS are assigned over three-months windows

* Quotas are reset on April 1st, July 1st, October 1st and January 1st
* Please make sure to use thoroughly your quarterly compute budget within the corresponding time frame
* Resources unused in the three-month periods are not transferred to the next allocation period but are forever lost

## Data Retention Policies

Data belonging to active projects in the filesystems /users, /project, /store are under backup. There is no backup for data under the scratch filesystem, therefore no data recovery is possible in case of accidental loss or for data deleted due to the cleaning policy implemented on this filesystem.

Please note that the long term storage service is granted as long as your project is active, and the data will be removed without further notice 3 months after the expiration of the project: please check the applicable filesystem policies for the grace period granted after the expiration of the project.

Furthermore, as soon as your project expires, the backup of the data belonging to the project will be disabled immediately: therefore no data backup will be available after the final data removal.

[](){#policies-fair-use}
## Fair Usage of Shared Resources

The [Slurm][slurm] scheduling system is a shared resource that can handle a limited number of batch jobs and interactive commands simultaneously. Therefore users should not submit hundreds of Slurm jobs and commands at the same time, as doing so would infringe our fair usage policy.

Let us also remind you that **running compute or memory intensive applications on the login nodes is forbidden**. Please submit batch jobs with the Slurm scheduler, in order to allocate and run your processes on compute nodes: compute or memory intensive processes affecting the performance of login nodes will be terminated without warning.
