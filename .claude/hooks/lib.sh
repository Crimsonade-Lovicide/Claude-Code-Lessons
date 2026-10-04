#!/usr/bin/env bash
# Shared helpers for the starter-kit hooks. Sourced by the other scripts, not run directly.
# Written for bash 3.2 so it works with the bash that ships on macOS.

# Project root: Claude Code sets CLAUDE_PROJECT_DIR for hooks.
kit_root() {
  if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
    printf '%s' "$CLAUDE_PROJECT_DIR"
  else
    git rev-parse --show-toplevel 2>/dev/null || pwd
  fi
}

# Load .claude/kit.conf if present (sets KIT_TEST_CMD, KIT_FORMAT_CMD, KIT_STOP_GATE).
kit_load_conf() {
  local conf
  conf="$(kit_root)/.claude/kit.conf"
  # shellcheck source=/dev/null
  [ -f "$conf" ] && . "$conf"
  return 0
}

# Absolute path for a file path that may be relative to the project root.
kit_abspath() {
  case "$1" in
    /*) printf '%s' "$1" ;;
    *) printf '%s/%s' "$(kit_root)" "$1" ;;
  esac
}

# Path relative to the project root (unchanged if it is outside the root).
kit_relpath() {
  local root
  root=$(kit_root)
  case "$1" in
    "$root"/*) printf '%s' "${1#"$root"/}" ;;
    *) printf '%s' "$1" ;;
  esac
}

# Nearest directory at or above $1 (but not above the project root) that contains $2.
kit_nearest() {
  local dir=$1 marker=$2 root
  root=$(kit_root)
  # Deleted files: walk up until we reach a directory that exists.
  while [ ! -d "$dir" ] && [ "$dir" != "/" ]; do dir=$(dirname "$dir"); done
  while :; do
    if [ -e "$dir/$marker" ]; then
      printf '%s' "$dir"
      return 0
    fi
    if [ "$dir" = "$root" ] || [ "$dir" = "/" ]; then
      return 1
    fi
    dir=$(dirname "$dir")
  done
}

# Strip leading and trailing whitespace.
kit_trim() {
  local s=$1
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

# Decide whether a path is protected by a rules file (gitignore-like, last match wins).
#   pattern            protect matching paths
#   !pattern           un-protect (for exceptions such as !.env.example)
#   existing:pattern   protect only files that already exist (new files allowed)
# A pattern without "/" matches the file name anywhere; with "/" it matches the
# path from the project root. "*" also matches "/".
# Returns 0 when protected and sets KIT_MATCH to the deciding rule.
kit_is_protected() {
  local rel=$1 abs=$2 list=$3 raw line target negate existing_only protected=1
  KIT_MATCH=""
  while IFS= read -r raw || [ -n "$raw" ]; do
    line=$(kit_trim "$raw")
    case "$line" in ''|'#'*) continue ;; esac
    negate=0
    existing_only=0
    case "$line" in '!'*) negate=1; line=${line#!} ;; esac
    case "$line" in existing:*) existing_only=1; line=${line#existing:} ;; esac
    case "$line" in
      */*) target=$rel ;;
      *) target=${rel##*/} ;;
    esac
    # shellcheck disable=SC2053 # $line is intentionally an unquoted glob
    if [[ $target == $line ]]; then
      if [ "$negate" = 1 ]; then
        protected=1
        KIT_MATCH=""
      elif [ "$existing_only" = 1 ] && [ ! -e "$abs" ]; then
        : # creating a new file in an append-only location is allowed
      else
        protected=0
        # shellcheck disable=SC2034 # read by the scripts that source this file
        KIT_MATCH=$raw
      fi
    fi
  done < "$list"
  return $protected
}
