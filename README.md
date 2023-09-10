# Git-Private-Repo-Cloner aka Hash Folder

This project is a simple idea which provides you the controll on your own private repositories in your account. This tool allows you to clone private repositories instantly and lets you to do all git actions even if you logged out from all your accounts.

NB: The system which the repository is cloned only be connected if and only if the key is authorized in the github. If the authurization revoked from your side from any client the system which uses that key will not able to connect to your account anymore. This gives you the controll on your repository from cloned devices

This tool is using SSH Keys for authentication, so only the systems which has the ssh key and its pass pharse can connect to the remote repository thus security can be achieved.

### Highlights:
1. Uses gh CLI tool to lets you login to the github repository, so the app can fetch the data.
2. SSH Protocol is used for git transactions
3. Key will be already generated for you if it is not found in the system.
4. Key will be automatically get registered to your github account once you logged in.
5. Gh CLI will take care of other authentication related tasks, no need to manually create any Access Tokens for authentication
6. If in case the cloning via SSH not working, we provide you another working ssh port, so the problem will be solved
7. Browse through your repositories and clone them if you want, no matter it is public or private.
8. Logout from the app will not lose your connection between cloned repositories and their remotes unless keys are present in both side
9. Application is cross-distro, thanks to flatpak framework

## Installation
