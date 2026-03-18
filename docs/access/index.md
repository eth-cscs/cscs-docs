# Connecting to Alps

This section covers how to access CSCS Alps systems and services. All methods share the same authentication foundation: a CSCS account, project membership, and multi-factor authentication.

!!! note "Prerequisites"
    Before using any access method you need:

    1. A CSCS account that is part of a project with allocated resources — see [accounts and projects][ref-account-management]
    2. Multi-factor authentication (MFA) set up — required for all CSCS services — see [MFA][ref-mfa]

!!! info "Platform transition: UMP → Waldur"
    CSCS is transitioning from the legacy User Management Portal (UMP) at [account.cscs.ch](https://account.cscs.ch) to a new ecosystem based on **Waldur** at [portal.cscs.ch](https://portal.cscs.ch).

    - **portal.cscs.ch** (Waldur) — new portal for project and resource management, user invitations, and service accounts
    - **account.cscs.ch** (UMP) — still active for SSH key management and MFA enrollment

    This documentation will be updated as the transition progresses.

## Access methods

Choose the access method that fits your workflow:

| Method | Best for |
|--------|----------|
| [SSH][ref-ssh] | Terminal access, job submission, file transfer |
| [Web portals][ref-access-web] | Browser-based access to CSCS services |
| [JupyterLab][ref-jupyter] | Interactive notebooks on compute nodes |
| [VS Code][ref-access-vscode] | Remote IDE development |
| [HPC Console][hpc-console] | Web-based job management and file browsing |
| [FirecREST][ref-firecrest] | Programmatic / API access, CI/CD pipelines |

<div class="grid cards" markdown>

-   :material-lock-check: __Multi-factor authentication__

    Required before using any CSCS service. Set up a TOTP authenticator and enroll your device.

    [:octicons-arrow-right-24: MFA setup][ref-mfa]

-   :fontawesome-solid-globe: __Web portals__

    Browser-based access to CSCS services via Single Sign-On.

    [:octicons-arrow-right-24: Web portals][ref-access-web]

-   :fontawesome-solid-terminal: __SSH__

    Terminal access to Alps clusters using signed SSH keys via the Ela jump host.

    [:octicons-arrow-right-24: SSH access][ref-ssh]

-   :material-console: __HPC Console__

    Web-based dashboard for job submission, monitoring, and file browsing.

    [:octicons-arrow-right-24: HPC Console][hpc-console]

-   :simple-jupyter: __JupyterLab__

    Interactive notebook environment running directly on Alps compute nodes.

    [:octicons-arrow-right-24: JupyterLab][ref-jupyter]

-   :material-microsoft-visual-studio-code: __VS Code__

    Remote IDE development on Alps using VS Code tunnels or SSH.

    [:octicons-arrow-right-24: VS Code][ref-access-vscode]

-   :material-fire-circle: __FirecREST__

    RESTful API for programmatic HPC access, CI/CD pipelines, and portal integration.

    [:octicons-arrow-right-24: FirecREST][ref-firecrest]

</div>
