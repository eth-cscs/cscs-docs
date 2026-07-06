[](){#ref-guides-course-account}
# Setting up a course account

This guide walks course participants through everything needed to access a CSCS cluster for a course, from creating an account to connecting over SSH.
It is a streamlined path through the more detailed [account][ref-account-management], [MFA][ref-mfa] and [SSH][ref-ssh] documentation, which you can follow if you run into trouble or want more background.

## Check your email

You should have received an invitation email from CSCS that contains a link to create your account and your course username, which looks like `course_XXXXX`.

!!! note "You will sign your key once per day"
    The signed SSH certificate that lets you connect to the cluster is valid for one day.
    You will need to [sign your key][ref-guides-course-account-sign] again on each day of the course, but the setup steps are only done once.

## Create your account

Open the link in your invitation email and follow the instructions to set your password.
Your course username (for example `course_XXXXX`) is also in the invitation email — keep it handy, as you will need it when [configuring SSH][ref-guides-course-account-ssh].

See [creating an account][ref-account-create] for a full walkthrough with screenshots.

## Set up multi-factor authentication

The first time you sign in to a CSCS web application, for example [portal.cscs.ch](https://portal.cscs.ch), you are prompted to enroll in multi-factor authentication (MFA).
This is required for all CSCS services.

To enroll, install a TOTP authenticator app such as Google Authenticator on your phone, then follow the on-screen instructions: scan the displayed QR code with the app and enter the 6-digit one-time password it generates to finish the setup.

See [configure the authenticator][ref-mfa-configure-otp] for the detailed procedure.

[](){#ref-guides-course-account-ssh}
## Set up SSH access

Password authentication is not available for SSH.
Instead you generate an SSH key on your machine and have CSCS sign it.
The steps in this section only need to be done once.

### Install `cscs-key`

`cscs-key` is the CSCS command-line tool for signing and managing your SSH keys.
Follow the [installation instructions][ref-ssh-cli] to install it on your machine.

!!! note "Prefer not to install anything?"
    You can manage and sign your key entirely in the browser with the [web dashboard][ref-ssh-key-management] at [user-account.cscs.ch](https://user-account.cscs.ch).
    If you go this route, sign your key there instead of running `cscs-key sign` below.

### Generate an SSH key

Create a new key pair:

```bash title="generate an SSH key (only needed once)"
ssh-keygen -t ed25519 -f ~/.ssh/cscs-key
```

### Configure SSH

Add the following to your `~/.ssh/config` file.
Replace `course_XXXXX` with your course username, and replace `daint` with the cluster your course uses.

```text title="~/.ssh/config"
Host ela
    HostName ela.cscs.ch
    User course_XXXXX
    IdentityFile ~/.ssh/cscs-key
    IdentitiesOnly yes

Host daint
    HostName daint.alps.cscs.ch
    User course_XXXXX
    IdentityFile ~/.ssh/cscs-key
    IdentitiesOnly yes
    ProxyJump ela
```

This routes your connection through the [Ela][ref-ssh-config] jump host, so you can reach the cluster directly with the `daint` alias.

[](){#ref-guides-course-account-sign}
## Sign your key and connect

Before connecting, sign your SSH key:

```console title="sign your key (repeat each day)"
$ cscs-key sign
```

Your web browser opens — sign in with the account you created earlier to complete the process.
The signed certificate is valid for one day, so run `cscs-key sign` again each day you want to connect.

Once your key is signed, connect to the cluster:

```console title="connect to the cluster"
$ ssh daint
```

See the [`cscs-key` usage documentation][ref-ssh-cli] for more options, such as signing a key stored in a different location with the `-f` flag.

## Getting help

If you get stuck, first check the documentation linked throughout this guide.
If that does not resolve it, ask your course instructors.
For issues beyond the course, see [getting support][ref-guide-support].
