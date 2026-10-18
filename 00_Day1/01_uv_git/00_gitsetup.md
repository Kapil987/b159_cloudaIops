# GitHub SSH Setup — Windows & Linux

Short notes to configure SSH authentication between your local machine and GitHub.

## 1. Generate an SSH key

Windows (PowerShell / Git Bash) and Linux (Terminal)

```
ssh-keygen -t ed25519 -C "your_email@example.com"
```

- Press `Enter` to accept the default file location.
- Set a passphrase if required.

Default key files:

| OS      | Private key         | Public key              |
| ------- | ------------------- | ----------------------- |
| Windows | `~/.ssh/id_ed25519` | `~/.ssh/id_ed25519.pub` |
| Linux   | `~/.ssh/id_ed25519` | `~/.ssh/id_ed25519.pub` |

Never share your private key. Upload only the `.pub` public key to GitHub.

## 2. Add the public key to GitHub

Display your public key:

```
# Windows PowerShell
Get-Content ~/.ssh/id_ed25519.pub

# Linux / Git Bash
cat ~/.ssh/id_ed25519.pub
```

- Open GitHub → Settings → SSH and GPG keys.
- Select New SSH key.
- Paste the public key and save.

Direct link: [GitHub SSH Keys](https://github.com/settings/keys)

## 3. Start the SSH agent and add the key

Linux

```
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Windows (Git Bash)

```
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Windows (PowerShell)

Run PowerShell as Administrator if needed:

```
Set-Service ssh-agent -StartupType Automatic
Start-Service ssh-agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

## 4. Test GitHub SSH connectivity

Run on Windows or Linux:

```
ssh -T git@github.com
```

Expected success message:

```
Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```

## 5. Clone or switch a repository to SSH

Clone using SSH

```
git clone git@github.com:USERNAME/REPOSITORY.git
```

Change an existing repository from HTTPS to SSH

```
git remote -v
git remote set-url origin git@github.com:USERNAME/REPOSITORY.git
git remote -v
```

## 6. Troubleshooting commands

```
ssh-add -l                       # List loaded keys
ssh -vT git@github.com           # Debug SSH connection
git config --global --list       # Check Git configuration
```

Important: SSH authentication and Git identity are separate. Configure your commit identity if needed:

```
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

These settings apply to commits, not SSH authentication.