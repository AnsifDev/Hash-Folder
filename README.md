# Hash Folder

![Icon](https://ansifdev.github.io/Hash-Folder/src/resources/app/org.htg.hashfolder.svg)

This project is a simple idea which provides you the controll on your own private repositories in your account. This tool allows you to clone private repositories instantly and lets you to do all git actions even if you logged out from all your accounts.

NB: The system which the repository is cloned only be connected if and only if the key is authorized in the github. If the authurization revoked from your side from any client the system which uses that key will not able to connect to your account anymore. This gives you the controll on your repository from cloned devices

This tool is using SSH Keys for authentication, so only the systems which has the ssh key and its pass pharse can connect to the remote repository thus security can be achieved.

### Highlights:
- Uses gh CLI tool to lets you login to the github repository, so the app can fetch the data.
- SSH Protocol is used for git transactions
- Key will be already generated for you if it is not found in the system.
- Key will be automatically get registered to your github account once you logged in.
- Gh CLI will take care of other authentication related tasks, no need to manually create any Access Tokens for authentication
- If in case the cloning via SSH not working, we provide you another working ssh port, so the problem will be solved
- Browse through your repositories and clone them if you want, no matter it is public or private.
- Logout from the app will not lose your connection between cloned repositories and their remotes unless keys are present in both side
- Application is cross-distro, thanks to flatpak framework

## Installation
1. Install the [flatpak](https://flatpak.org/setup/) framework if not already installed
2. Download the [Hash Folder Installer](https://ansifdev.github.io/Hash-Folder/org.htg.hashfolder.flatpakref)
3. Install it either running this code (Recommended Method):
   ```
   flatpak install ./org.htg.hashfolder.flakpatref
   ```
   or by just double clicking the file which opens the software installer for a GUI installation but not recommended

### Automated Installation
Installation can be automated by simply running this [Debian Automated Installer](https://ansifdev.github.io/Hash-Folder/debian_based_installer) on Ubuntu or Debian Based Systems and [RedHat Automated Installer](https://ansifdev.github.io/Hash-Folder/red_hat_based_installer) on Fedora or RedHat Based Systems

## App Features:
- [x]  Fully automated login
- [x]  SSH Port Configuration via app
- [x]  Browsable and Clonable Repository Management Page
- [x]  Repository Searching and Filtering
- [x]  Responssive UI (Compatable on Mobile Form Facter)
- [x]  Theme aware UI which can change its theme by its self
- [ ]  Suggesting for changing the SSH Port if cloning fails
- [ ]  Open with feature for cloned repositories
- [ ]  Device Manager Page which can manage the access of other systems
- [ ]  Guest Mode and Clear System from Account Options
