[](){#ref-policies}

# CSCS User Policies

The CSCS [code of conduct](code-of-conduct.md) outlines the responsibilities and proper practices for the CSCS user community.

The [User Regulations][ref-policies-user-regulations] define the basic guidelines for the usage of CSCS computing resources. The right to access CSCS resources may be revoked to whoever breaches any of the user regulations.

The [User Support Policies](support.md), the [Slack Code of Conduct](slack.md) and the [Scheduled Maintenance and System Unavailability Policies](maintenance.md) provide additional information on support services, the regulations of the Users Slack space and the scheduled maintenance events.

Individual platforms may define their own policies, which take precedence over the general policies below. The [Machine Learning Platform policies][ref-mlp-policies] describe the project types, compute and storage budgets, and project lifetime rules that apply to MLP projects.

## Resource Allocation Policies 

Compute time on Alps systems is measured in node hours.
Most partitions allocate whole nodes to a job.
Some partitions can [share a node][ref-slurm-sharing] between jobs, for example the GH200 partitions on Santis.
Your project is charged for each node that your job uses, for the full run time of the job.
This also applies when the job uses only part of the node.
For example, a job that uses one GPU on a shared Santis node is charged one node hour for each hour that it runs.

Please note that resources at CSCS are assigned over three-months windows

* Quotas are reset on April 1st, July 1st, October 1st and January 1st
* Please make sure to use thoroughly your quarterly compute budget within the corresponding time frame
* Resources unused in the three-month periods are not transferred to the next allocation period but are forever lost

## Data Retention Policies

Data belonging to active projects in the filesystems `/users` and `/capstor/store` are under backup. There is no backup for data under the scratch filesystem, therefore no data recovery is possible in case of accidental loss or for data deleted due to the cleaning policy implemented on this filesystem.

Please note that the long term storage service is granted as long as your project is active, and the data will be removed without further notice 3 months after the expiration of the project: please check the applicable filesystem policies for the grace period granted after the expiration of the project.

Furthermore, as soon as your project expires, the backup of the data belonging to the project will be disabled immediately: therefore no data backup will be available after the final data removal.
