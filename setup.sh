#!/bin/bash

# === Variables ===
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$REPO_DIR/scripts/git-hooks"
GIT_HOOKS_DIR="$REPO_DIR/.git/hooks"
DEPLOY_SCRIPT="$REPO_DIR/backend/deploy.sh"

# === 1. Create post-merge Git hook if not already linked ===
POST_MERGE="$GIT_HOOKS_DIR/post-merge"
SOURCE_HOOK="$HOOKS_DIR/post-merge"

echo "[SETUP] Linking post-merge Git hook..."
if [ ! -L "$POST_MERGE" ] || [ "$(readlink -- "$POST_MERGE")" != "$SOURCE_HOOK" ]; then
  mkdir -p "$HOOKS_DIR"
  mkdir -p "$GIT_HOOKS_DIR"
  echo -e "#!/bin/bash\n\ncd \"$REPO_DIR/backend\" && ./deploy.sh" > "$SOURCE_HOOK"
  chmod +x "$SOURCE_HOOK"
  ln -sf "$SOURCE_HOOK" "$POST_MERGE"
  echo "[SETUP] post-merge hook set!"
else
  echo "[SETUP] post-merge hook already in place."
fi

# === 2. Run the deploy script ===
echo "[SETUP] Running deploy.sh to install services and dependencies..."
chmod +x "$DEPLOY_SCRIPT"
"$DEPLOY_SCRIPT"

echo "[SETUP COMPLETE] Everything is configured. Future 'git pull' will auto-deploy. 🚀"
