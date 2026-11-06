# Worked example: a VNC uenv on GH200

Design decisions for a remote-visualization uenv. Use as a template for reasoning about what belongs in a uenv versus what to rely on from the host.

## What to bundle in the uenv

- TurboVNC (provides Xvnc)
- VirtualGL (GPU-accelerated rendering via EGL)
- Window manager (icewm for lightweight, xfce4 for full desktop)
- X11 client libraries
- Font configuration (freetype, fontconfig, xkeyboard-config)
- Mesa (software fallback, built `~llvm` to keep it small)
- dbus (required by desktop environments)

## What to rely on from the host

- glibc and base runtime
- NVIDIA GPU drivers and EGL libraries (`/usr/lib64/libEGL_nvidia.so`, etc.)
- libglvnd (GL dispatch, already on system)
- NVIDIA EGL vendor config (`/usr/share/glvnd/egl_vendor.d/`)

## GH200-specific notes

- VirtualGL's EGL backend needs `/dev/dri/renderD*` access.
- Launch GPU-accelerated apps with `vglrun -d egl <app>`.
- Disable the compositor in the window manager (no GPU GL on the 2D X proxy).
- Verify with `vglrun -d egl glxinfo | grep -i renderer` (should show the GH200).
