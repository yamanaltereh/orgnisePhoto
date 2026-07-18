import os
import sys

SOURCE_FOLDER_PATH = './data/SourcePhotos'
TARGET_FOLDER_PATH = './data/TargetPhotos'
OTHER_FOLDER_PATH = './data/others'
REJECTED_FOLDER_PATH = './data/rejectedExtensions'

OUTPUT_FOLDERS = [TARGET_FOLDER_PATH, OTHER_FOLDER_PATH, REJECTED_FOLDER_PATH]


def scan_files(basepath):
    """Recursively collect all files with their sizes. Returns list of (name, size) tuples."""
    results = []
    if not os.path.exists(basepath):
        return results
    for dirpath, dirnames, filenames in os.walk(basepath):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.startswith('.'):
                continue
            full_path = os.path.join(dirpath, filename)
            size = os.path.getsize(full_path)
            results.append((filename, size))
    return results


def build_size_map(files):
    """Map filename -> total size (summing any duplicate names)."""
    size_map = {}
    for name, size in files:
        size_map[name] = size_map.get(name, 0) + size
    return size_map


def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f'{size_bytes:.2f} {unit}'
        size_bytes /= 1024
    return f'{size_bytes:.2f} TB'


def print_table(rows, headers):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
    header_row = '|' + '|'.join(f' {h:<{col_widths[i]}} ' for i, h in enumerate(headers)) + '|'

    print(separator)
    print(header_row)
    print(separator)
    for row in rows:
        print('|' + '|'.join(f' {str(cell):<{col_widths[i]}} ' for i, cell in enumerate(row)) + '|')
    print(separator)


def main():
    print('\n=== Photo Organisation Verification ===\n')

    # Scan source
    source_files = scan_files(SOURCE_FOLDER_PATH)
    source_count = len(source_files)
    source_size = sum(s for _, s in source_files)
    source_names = {name for name, _ in source_files}

    # Scan all output folders
    output_files = []
    folder_stats = []
    for folder in OUTPUT_FOLDERS:
        files = scan_files(folder)
        count = len(files)
        size = sum(s for _, s in files)
        if count > 0 or os.path.exists(folder):
            folder_stats.append((folder, count, format_size(size)))
        output_files.extend(files)

    output_count = len(output_files)
    output_size = sum(s for _, s in output_files)
    output_names = {name for name, _ in output_files}

    # Check for missing files (in source but not in any output)
    missing_in_output = source_names - output_names

    # Check for extra files (in output but not in source)
    extra_in_output = output_names - source_names

    # Overall match
    count_match = source_count == output_count
    size_match = source_size == output_size

    # --- Summary table ---
    print('Summary:')
    summary_rows = [
        ('Source', source_count, format_size(source_size), SOURCE_FOLDER_PATH),
        ('Output (total)', output_count, format_size(output_size), ', '.join(OUTPUT_FOLDERS)),
    ]
    print_table(summary_rows, ['', 'Files', 'Total Size', 'Path'])

    # --- Per-output-folder breakdown ---
    if folder_stats:
        print('\nOutput folder breakdown:')
        print_table(folder_stats, ['Folder', 'Files', 'Total Size'])

    # --- Verification results ---
    print('\nVerification results:')
    check_rows = [
        ('File count match', 'PASS' if count_match else 'FAIL', f'{source_count} == {output_count}'),
        ('Total size match', 'PASS' if size_match else 'FAIL', f'{format_size(source_size)} == {format_size(output_size)}'),
        ('Missing files', 'PASS' if not missing_in_output else 'FAIL', f'{len(missing_in_output)} missing'),
        ('Extra files', 'PASS' if not extra_in_output else 'WARN', f'{len(extra_in_output)} extra'),
    ]
    print_table(check_rows, ['Check', 'Result', 'Detail'])

    # --- Re-scan on failure to pinpoint the differing files ---
    size_diffs = []
    if not count_match or not size_match or missing_in_output:
        print('\nDiscrepancy detected — running a second scan to pinpoint the differing files...')

        source_files_2 = scan_files(SOURCE_FOLDER_PATH)
        output_files_2 = []
        for folder in OUTPUT_FOLDERS:
            output_files_2.extend(scan_files(folder))

        source_size_map = build_size_map(source_files_2)
        output_size_map = build_size_map(output_files_2)

        missing = sorted(set(source_size_map) - set(output_size_map))
        size_diffs = sorted(
            name for name in set(source_size_map) & set(output_size_map)
            if source_size_map[name] != output_size_map[name]
        )

        if missing:
            print(f'\nFiles missing from output ({len(missing)}):')
            print_table(
                [(name, format_size(source_size_map[name])) for name in missing],
                ['Missing file', 'Source size'],
            )

        if size_diffs:
            print(f'\nFiles present but with different sizes ({len(size_diffs)}):')
            print_table(
                [
                    (
                        name,
                        format_size(source_size_map[name]),
                        format_size(output_size_map[name]),
                    )
                    for name in size_diffs
                ],
                ['File', 'Source size', 'Output size'],
            )

        if not missing and not size_diffs:
            print('\nSecond scan found no per-file differences '
                  '(discrepancy may be from extra output files or duplicate names).')

    if extra_in_output:
        print(f'\nExtra files in output not found in source ({len(extra_in_output)}):')
        for name in sorted(extra_in_output):
            print(f'  - {name}')

    overall = count_match and size_match and not missing_in_output and not size_diffs
    print(f'\nOverall: {"ALL CHECKS PASSED" if overall else "VERIFICATION FAILED"}')

    return 0 if overall else 1


if __name__ == '__main__':
    sys.exit(main())
