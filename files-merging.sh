#!/bin/bash

# Define paths
SOURCE="/Users/yaman/projects/orgnisePhoto/data/TargetPhotos/2026/"
# ~/ only expands at the start of a path segment (no leading / before ~)
TARGET="${HOME}/Downloads/To sync/NEW TO SYNC/2026/"
LOG_FILE="/Users/yaman/projects/orgnisePhoto/files-merging-diff-log.txt"

echo "Merging SOURCE -> TARGET with rsync..."
echo "  SOURCE: $SOURCE"
echo "  TARGET: $TARGET"
echo "  Log:    $LOG_FILE"

# -a archive (perms, times, recurse). -i itemized list (what changed).
# -n is DRY-RUN only — omit it to actually copy. Preview with: rsync -ani ...
rsync -ai "$SOURCE" "$TARGET" | tee "$LOG_FILE"

# Optional: mirror and delete extras on target (dangerous): rsync -ai --delete "$SOURCE" "$TARGET"

echo "Done. See $LOG_FILE for the itemized transfer list."
