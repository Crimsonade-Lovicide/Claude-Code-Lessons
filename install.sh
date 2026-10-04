#!/usr/bin/env bash
# Install the Claude Code starter kit. Never overwrites existing files.
set -euo pipefail

kit=$(cd "$(dirname "$0")" && pwd)

usage() {
  cat <<'EOF'
Usage:
  ./install.sh <path-to-repo>          install the project kit into a repo
  ./install.sh <path-to-repo> --user   also install personal files into ~/.claude
  ./install.sh --user                  personal files only

Existing files are never overwritten. Skipped files are listed so you can merge
them by hand (or ask Claude to merge them).
EOF
}

target=""
user=0
for arg in "$@"; do
  case "$arg" in
    --user) user=1 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "Unknown option: $arg" >&2; usage >&2; exit 1 ;;
    *) target=$arg ;;
  esac
done
if [ -z "$target" ] && [ "$user" = 0 ]; then usage >&2; exit 1; fi

copied=0
skipped=""

# copy_tree <source dir> <destination dir>
copy_tree() {
  local src=$1 dest=$2 rel
  while IFS= read -r rel; do
    rel=${rel#./}
    if [ -e "$dest/$rel" ]; then
      skipped="$skipped
  $dest/$rel"
    else
      mkdir -p "$(dirname "$dest/$rel")"
      cp -p "$src/$rel" "$dest/$rel"
      copied=$((copied + 1))
    fi
  done < <(cd "$src" && find . -type f | sort)
}

if ! command -v jq >/dev/null 2>&1; then
  echo "Warning: jq is not installed. The hooks need it (brew install jq, or apt install jq)." >&2
fi

if [ -n "$target" ]; then
  [ -d "$target" ] || { echo "Not a directory: $target" >&2; exit 1; }
  target=$(cd "$target" && pwd)
  git -C "$target" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    || echo "Warning: $target is not a git repository. The Stop hook only runs inside git repos." >&2
  copy_tree "$kit/template" "$target"
  chmod +x "$target"/.claude/hooks/*.sh
fi

if [ "$user" = 1 ]; then
  copy_tree "$kit/user" "$HOME/.claude"
  chmod +x "$HOME/.claude/hooks/notify.sh" 2>/dev/null || true
fi

echo "Installed $copied file(s)."
if [ -n "$skipped" ]; then
  echo "Skipped because they already exist (merge by hand):$skipped"
fi
if [ -n "$target" ]; then
  cat <<EOF

Next:
  1. cd "$target" && bash .claude/hooks/selftest.sh
  2. Start Claude Code there and run /setup-kit to tailor the kit to the repo.
  3. Review the diff, then commit .claude/ and CLAUDE.md.
EOF
fi
