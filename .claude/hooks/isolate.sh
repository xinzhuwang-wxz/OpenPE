#!/bin/bash
# Block file access outside the current analysis directory.
# In dev mode (cwd = repo root, no .analysis_config), allow everything.
#
# Symlinks within the analysis dir (e.g., conventions/) are allowed by
# checking the logical path (before symlink resolution).
#
# .analysis_config supports multiple allowed paths:
#   data_dir=/path/to/data
#   allow=/another/path
#   allow=/yet/another

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')
CWD=$(echo "$INPUT" | jq -r '.cwd')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty')

# No file path → allow (not a file-access call)
[ -z "$FILE_PATH" ] && exit 0

# Dev mode: no .analysis_config in cwd ancestry → allow everything
ANALYSIS_DIR="$CWD"
while [ "$ANALYSIS_DIR" != "/" ]; do
    [ -f "$ANALYSIS_DIR/.analysis_config" ] && break
    ANALYSIS_DIR=$(dirname "$ANALYSIS_DIR")
done
[ "$ANALYSIS_DIR" = "/" ] && exit 0

CONFIG="$ANALYSIS_DIR/.analysis_config"

# Build list of allowed paths: analysis dir, /tmp, data_dir, any allow= lines
ALLOWED=("$ANALYSIS_DIR" "/tmp")
while IFS='=' read -r key val; do
    val=$(echo "$val" | xargs)  # trim whitespace
    [ -z "$val" ] && continue
    case "$key" in
        data_dir|allow) ALLOWED+=("$val") ;;
    esac
done < <(grep -v '^#' "$CONFIG" | grep '=')

# Check logical path first (no symlink resolution — allows conventions/ symlink)
if [[ "$FILE_PATH" = /* ]]; then
    LOGICAL="$FILE_PATH"
else
    LOGICAL="$CWD/$FILE_PATH"
fi
LOGICAL=$(realpath -ms "$LOGICAL" 2>/dev/null || echo "$LOGICAL")

for dir in "${ALLOWED[@]}"; do
    [ -z "$dir" ] && continue
    case "$LOGICAL" in "$dir"/*) exit 0 ;; esac
done

# Also check physical path (resolves symlinks)
ABS=$(cd "$CWD" && realpath -m "$FILE_PATH" 2>/dev/null || echo "$FILE_PATH")

for dir in "${ALLOWED[@]}"; do
    [ -z "$dir" ] && continue
    case "$ABS" in "$dir"/*) exit 0 ;; esac
done

# Deny
jq -n --arg reason "Blocked: $TOOL access to $ABS (outside analysis dir $ANALYSIS_DIR)" \
  '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":$reason}}'
