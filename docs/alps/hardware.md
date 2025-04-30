[](){#ref-alps-hardware}
# Alps Hardware

Alps is a HPE Cray EX3000 system, a liquid cooled blade-based, high-density system.

!!! todo
    this is a skeleton - all of the details need to be filled in

## Alps Cabinets

The basic building block of the system is a liquid-cooled cabinet.
A single cabinet can accommodate up to 64 compute blade slots within 8 compute chassis. The cabinet is not configured with any
cooling fans.
All cooling needs for the cabinet are provided by direct liquid cooling and the CDU.
This approach to cooling provides greater efficiency for the rack-level cooling, decreases power costs associated with cooling (no blowers) and utilizes a single water source per CDU One cabinet supports the following:

* 8 compute chassis
* 4 power shelves with a maximum of 6 rectifiers per shelf- 24 total 12.5 or 15kW rectifiers per cabinet
* 4 PDUs (1 per power shelf)
* 3 power input whips (3-phase)
* Maximum of 64 quad-blade compute blades
* Maximum of 64 Slingshot switch blades

[](){#ref-alps-hsn}
## Alps High Speed Network

!!! todo
    information about the network.

    * Details about SlingShot 11.
        * how many NICs per node
        * raw feeds and speeds
    * Some OSU benchmark results.
    * GPU-aware communication
    * **slingshot is not infiniband - there is no NVSwitch**

## Alps Nodes

Alps was installed in phases, starting with the installation of 1024 AMD Rome dual socket CPU nodes in 2020, through to the main installation of 2,688 Grace-Hopper nodes in 2024.

There are currently four node types in Alps, with another becoming available in 2025:

| type           | blades | nodes | CPU sockets | GPU devices |
| ----           | ------:| -----:| -----------:| -----------:|
| NVIDIA GH200   | 1344   | 2688  | 10,752      | 10,752      |
| AMD Rome       |  256   | 1024  |  2,048      | --          |
| NVIDIA A100    |   72   |  144  |    144      | 576         |
| AMD MI250x     |   12   |   24  |     24      |  96         |
| AMD MI300A     |   64   |  128  |    512      | 512         |

[](){#ref-alps-gh200-node}
### NVIDIA GH200 GPU Nodes

Perry Peak

[](){#ref-alps-zen2-node}
### AMD Rome CPU Nodes

EX425

[](){#ref-alps-a100-node}
### NVIDIA A100 GPU Nodes

Grizzly Peak

[](){#ref-alps-mi200-node}
### AMD MI250x GPU Nodes

Bard Peak

[](){#ref-alps-mi300-node}
### AMD MI300A GPU Nodes

Parry Peak

!!! info "coming soon"
    H1 2025

