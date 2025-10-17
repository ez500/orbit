#!/usr/bin/env bash
# Update local repo with all new branches from origin and pull latest changes.
# Usage:
#   ./git-update-all.sh                # merge (default)
#   REBASE=1 ./git-update-all.sh       # use --rebase pulls
#   EXCLUDE='^(experimental|wip/)' ./git-update-all.sh   # skip matching branches
#
# Notes:
# - Requires: git, bash
# - Works best in Git Bash / macOS / Linux
# - Only touches the current repo (run inside a Git repo)

set -u  # (no -e so we can continue after a per-branch failure)

# --- helpers ---------------------------------------------------------------
err() { printf >&2 "[ERR] %s\n" "$*"; }
log() { printf "[INFO] %s\n" "$*"; }

# --- preflight -------------------------------------------------------------
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  err "Not a git repository. cd into a repo first."
  exit 1
fi

REMOTE="${REMOTE-origin}"
REBASE="${REBASE-0}"
EXCLUDE="${EXCLUDE-}"       # regex to skip branches, e.g. '^(experimental|wip/)'
PULL_ARGS=()
if [[ "$REBASE" == "1" ]]; then
  PULL_ARGS+=(--rebase)
fi

# Remember where we started.
current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '')"
if [[ "$current_branch" == "HEAD" ]]; then
  current_branch=""  # detached
fi

# Detect a dirty working tree (uncommitted changes)
dirty=0
if ! git diff --quiet || ! git diff --cached --quiet; then
  dirty=1
  stash_name="auto-stash-$(date +%s)"
  log "Working tree dirty — stashing changes as '$stash_name'..."
  git stash push -u -k -m "$stash_name" >/dev/null 2>&1 || err "Stash failed (continuing)"
fi

# --- fetch/prune/tags ------------------------------------------------------
log "Fetching from '$REMOTE' (with prune + tags)..."
git fetch "$REMOTE" --prune --tags || err "Fetch failed (continuing)"

# --- create local tracking branches for new remote branches ----------------
log "Ensuring local tracking branches exist for all remote branches..."
# list remote branches (origin/*) except origin/HEAD
while IFS= read -r rb; do
  [[ -z "$rb" ]] && continue
  [[ "$rb" == "origin/HEAD" ]] && continue
  local_branch="${rb#origin/}"

  # Skip excluded branches
  if [[ -n "$EXCLUDE" ]] && [[ "$local_branch" =~ $EXCLUDE ]]; then
    log "Skipping (excluded): $local_branch"
    continue
  fi

  if git show-ref --verify --quiet "refs/heads/$local_branch"; then
    # already have a local branch
    continue
  fi

  log "Creating tracking branch: $local_branch -> origin/$local_branch"
  git branch --track "$local_branch" "origin/$local_branch" >/dev/null 2>&1 \
    || err "Could not track origin/$local_branch"
done < <(git for-each-ref --format='%(refname:short)' "refs/remotes/$REMOTE" | sed 's#^remotes/##' | sed 's#^'"$REMOTE"'/##' | sed 's#^#origin/#' | sed 's#^origin/origin/#origin/#' | sort -u)

# The above dance normalizes output across environments; simpler equivalent:
# git for-each-ref --format='%(refname:short)' refs/remotes/origin | grep -v '^origin/HEAD$' | sed 's#^origin/##'

# --- pull each local branch ------------------------------------------------
log "Pulling latest changes for all local branches..."
mapfile -t local_branches < <(git for-each-ref --format='%(refname:short)' refs/heads | sort)

for b in "${local_branches[@]}"; do
  # Skip excluded branches
  if [[ -n "$EXCLUDE" ]] && [[ "$b" =~ $EXCLUDE ]]; then
    log "Skipping (excluded): $b"
    continue
  fi

  log "Updating branch: $b"
  if ! git checkout -q "$b"; then
    err "Checkout failed for $b — skipping"
    continue
  fi

  # Determine its upstream (if any)
  if git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
    # Has upstream; normal pull
    if ! git pull "${PULL_ARGS[@]}"; then
      err "Pull failed on $b — leaving as-is"
      continue
    fi
  else
    # No upstream; if remote branch exists, set upstream and pull
    if git show-ref --verify --quiet "refs/remotes/$REMOTE/$b"; then
      log "Setting upstream: $b -> $REMOTE/$b"
      git branch -u "$REMOTE/$b" "$b" >/dev/null 2>&1 || err "Failed to set upstream for $b"
      if ! git pull "${PULL_ARGS[@]}"; then
        err "Pull failed on $b — leaving as-is"
        continue
      fi
    else
      log "No upstream and no matching remote for $b — skipping pull"
    fi
  fi
done

# --- return to original branch --------------------------------------------
if [[ -n "${current_branch:-}" ]]; then
  git checkout -q "$current_branch" || err "Could not return to $current_branch"
fi

# --- restore stash if we stashed ------------------------------------------
if [[ "$dirty" -eq 1 ]]; then
  log "Restoring stashed changes..."
  if ! git stash pop >/dev/null 2>&1; then
    err "Automatic stash pop failed. Use 'git stash list' and 'git stash pop' manually."
  fi
fi

log "Done. ✅"
