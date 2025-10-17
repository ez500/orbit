# Make sure you’re on the correct branch
git checkout main

# Fetch all remote data (branches, tags, etc.)
git fetch --all

# Reset your branch to exactly match origin/main
git reset --hard origin/main

# (optional) Loop through all remote branches to update locals
for branch in $(git branch -r | grep -v '\->'); do
  local_branch=${branch#origin/}
  git checkout -B "$local_branch" "$branch"
done

# Return to main when done
git checkout main
