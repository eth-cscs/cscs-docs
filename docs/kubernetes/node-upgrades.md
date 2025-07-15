# Kubernetes Nodes OS Update Policy

To ensure the **security** and **stability** of our infrastructure, CSCS will perform **monthly OS updates** on all nodes of our Kubernetes clusters.

## 🔄 Maintenance Schedule

- **Frequency**: Every **first week of the month**  
- **Reboot Window**: **Monday to Friday**, between **09:00 and 15:00**  
- **Time Zone**: Europe/Zurich

These updates include important security patches and system updates for the operating systems of cluster nodes.

> ⚠️ **Note:** Nodes will be **rebooted only if required** by the updates. If no reboot is necessary, nodes will remain in service without disruption.

## 🚨 Urgent Security Patches

In the event of a **critical zero-day vulnerability**, we will apply patches and perform reboots (if required) **as soon as possible**, outside of the regular update schedule if needed.  

- Affected nodes will be updated **immediately** to protect the platform.
- Users will be notified ahead of time **when possible**.
- Standard safety and rolling reboot practices will still be followed.

## 🛠️ Reboot Management with Kured

We use [**Kured** (KUbernetes REboot Daemon)](https://github.com/kubereboot/kured) to safely automate the reboot process. Kured ensures that:

- Reboots are triggered **only when necessary** (e.g., after kernel updates).
- Nodes are rebooted **one at a time** to avoid service disruption.
- Reboots occur **only during the defined window** 
- Nodes are **cordoned**, **drained**, and **gracefully reintegrated** after reboot.

## ✅ Application Requirements

To avoid service disruption during node maintenance, applications **must be designed for high availability**. Specifically:

- Use **multiple replicas** spread across nodes.
- Follow **cloud-native best practices**, including:
  - Proper **readiness** and **liveness probes**
  - **Graceful shutdown** support
  - **Stateless design** or resilient handling of state
  - Appropriate **resource requests and limits**

> ❗ Applications that do not meet these requirements **may experience temporary disruption** during node reboots.

## 👩‍💻 Need Help?

If you have questions or need help preparing your applications for rolling node maintenance, please contact the Network and Cloud team via Service Desk ticket.

