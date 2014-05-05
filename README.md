raes_common
===========

Common utilities, configurations, and other stuff that is generally useful.


# Virtual Machines #
The virtual machines are located at [R:\AES\Software\VMs](R:\AES\Software\VMs "R:\AES\Software\VMs"). 

- Ubuntu 12.04 Common 64
	- Description
		- Fresh install of Ubuntu 12.04 64-bit. All updates have been applied after the initial install.
		- Use this as a baseline Ubuntu system.
	- Notes for _v1 (TODO)
		- Update Eclipse with ros style formatting and doxygen 
- ROS Hydro Common 64
	- Description
		- Ubuntu 12.04 with install of **hydro-desktop-full**
		- Eclipse Indigo IDE with C++ development kit
		- git
		- meld
	- _v0 (notes)
		- Fresh install of Eclipse
	- Notes for _v1 (TODO)
		- Incorporate changes from **Ubuntu 12.04 Common 64_v1**
- ROS Hydro Common
	- Description
		- Ubuntu 12.04 32-bit with install of hydro-desktop-full
		- Eclipse Indigo IDE with C++, Python, Java development kits
		- TODO add other packages
		- Note: VM based on (TODO) VM
- ROS Training Hydro
- ROS Training Groovy

# Things to do with New VM Installation #

- Update git config
	- git config --global user.name "Your Name"
	- git config --global user.email you@example.com


# Desktop Shortcuts #

- LibreOffice.desktop
	- Designed to replace multiple LibreOffice desktop icons with 1 expandable icon.
	- Copy to ~/.local/applications. Make sure file is allowed to execute.
	- Run desktop icon and lock to launcher.
	- Log out/in to fully enable functionality.

# Eclipse Configuration #

- Make sure ros-style formatting is selected
- Import C++ code templates: **Window:Preferences:C/C++:Code Style:Code Templates:Import**. Templates can be selected when creating a new file using Eclipse.