:'
Generate an SSH key pair if you don’t already have one:
    `ssh-keygen -t ed25519 -C "your_email@example.com"`

Copy the contents of the public key (~/.ssh/id_ed25519.pub):
    `cat ~/.ssh/id_ed25519.pub`
Add this key to the GitHub account with the repo.

Initialize a new repository :
    `git init`
    `git remote add origin git@github.com:yourusername/yourrepository.git`
'
STATS_FILE='/stats/'
COMMIT_MESSAGE='Auto-update stats file'

git add $(basename $STATS_FILE)

git commit -m "$COMMIT_MESSAGE"

git push origin main