# Preflight every destination before writing. A different existing file
# aborts the call; byte-identical files are reused instead of overwritten.

from pathlib import Path


def save_outputs(directory, outputs):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name, raw in outputs.items():
        p = directory/name
        if p.exists() and p.read_bytes() != raw:
            raise FileExistsError(f'Existing result differs: {p}')
    for name, raw in outputs.items():
        p = directory/name
        if not p.exists():
            p.write_bytes(raw)
    return [str(directory/name) for name in outputs]

def artifact_arguments(parser, output_subdir):
    """Parse shared input, output and family options for figures and tables."""
    families = ('conductor', 'height')
    parser.add_argument('--data-dir', type=Path,
                        help='directory containing the aggregate NPZ files (default: bundled data/)')
    parser.add_argument('--family-dir', type=Path,
                        help='directory containing the corresponding family snapshots '
                             '(default: bundled data/)')
    parser.add_argument('--output-dir', type=Path,
                        help=f'destination directory (default: work/reproduced/{output_subdir}/)')
    parser.add_argument('--family', choices=families, action='append', dest='kinds',
                        help='limit generation to this family; repeat as needed (default: both)')
    args = parser.parse_args()
    return {**vars(args), 'kinds': tuple(dict.fromkeys(args.kinds or families))}
