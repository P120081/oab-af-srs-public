# raw_code/analysis

This folder hosts orchestration scripts.

- `make_figures.py`: One-shot runner. It discovers inputs under `data/derived/` and writes outputs to `docs/`.
- Optional: `validate_data.py`: If present, it is executed first to check ASCII headers (`chi2`, `p_value`), `n11 < 3`, and `TTO > 0`.

## Examples
```bash
# all figures
python raw_code/analysis/make_figures.py

# specific targets
python raw_code/analysis/make_figures.py --fig2 --fig4 --fig6

# dry run
python raw_code/analysis/make_figures.py --dry-run
```
