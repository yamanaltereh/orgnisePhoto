# orgnisePhoto

Python script to organise photos by day into year/month/day folder structure.

## How it works

`managePhotos.py` reads all photos from the source folder recursively, extracts the date from each filename (supports formats like `IMG_20191021_172027.jpg`, `20191021_172027.jpg`, `VID_20210523_102919.mp4`, and Eastern Arabic numerals), then copies them into the target folder organised as:

```
TargetPhotos/
  2025/
    8.2025/
      24.8.2025/
        photo.jpg
```

Files with unrecognised dates go to `data/others/`. Files with rejected extensions (e.g. `.json`) go to `data/rejectedExtensions/`.

## Scripts

| Script | Description |
|---|---|
| `managePhotos.py` | Organises photos from source into dated folder structure |
| `verifyOutput.py` | Verifies the output matches the source (file count and total size) |

## Usage

### 1. Organise photos

```bash
python3 managePhotos.py
```

Or using the shell script, which runs both organise and verify steps (logs organise output to `managePhotos.log`):

```bash
./run.sh
```

### 2. Verify the output

Run after `managePhotos.py` to confirm every source file was copied correctly:

```bash
python3 verifyOutput.py
```

Example output:

```
=== Photo Organisation Verification ===

Summary:
+----------------+-------+------------+------------------------------------------------------------+
|                | Files | Total Size | Path                                                       |
+----------------+-------+------------+------------------------------------------------------------+
| Source         | 120   | 1.23 GB    | ./data/SourcePhotos                                        |
| Output (total) | 120   | 1.23 GB    | ./data/TargetPhotos, ./data/others, ./data/rejectedExtens… |
+----------------+-------+------------+------------------------------------------------------------+

Output folder breakdown:
+-----------------------------+-------+------------+
| Folder                      | Files | Total Size |
+-----------------------------+-------+------------+
| ./data/TargetPhotos         | 115   | 1.22 GB    |
| ./data/others               | 3     | 5.00 MB    |
| ./data/rejectedExtensions   | 2     | 1.00 MB    |
+-----------------------------+-------+------------+

Verification results:
+--------------------+--------+------------------------------+
| Check              | Result | Detail                       |
+--------------------+--------+------------------------------+
| File count match   | PASS   | 120 == 120                   |
| Total size match   | PASS   | 1.23 GB == 1.23 GB           |
| Missing files      | PASS   | 0 missing                    |
| Extra files        | WARN   | 0 extra                      |
+--------------------+--------+------------------------------+

Overall: ALL CHECKS PASSED
```

The script exits with code `0` on success and `1` if any check fails, making it suitable for use in shell pipelines. Extra files in the output produce a `WARN` (not a failure).

## Configuration

Paths are defined as constants at the top of each script:

| Constant | Default | Description |
|---|---|---|
| `SOURCE_FOLDER_PATH` | `./data/SourcePhotos` | Input photos folder |
| `TARGET_FOLDER_PATH` | `./data/TargetPhotos` | Output organised folder |
| `OTHER_FOLDER_NAME` | `./data/others` | Files with no recognisable date |
| `REJECTED_EXTENSIONS_FOLDER_NAME` | `./data/rejectedExtensions` | Files with unsupported extensions |
