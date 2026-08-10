# Publishing

The recommended initial repository is private:

```bash
gh repo create jaredleishman/converge-workflows \
  --private \
  --source=. \
  --remote=origin \
  --push \
  --description "Front-loaded software change planning and bounded code review"
```

To publish it publicly instead, replace `--private` with `--public`.

Before publishing or tagging a release:

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
git status --short
```

To release a new version:

```bash
python scripts/sync_version.py 0.2.0
# Update CHANGELOG.md
python scripts/validate.py
python -m unittest discover -s tests -v
git add .
git commit -m "Release Converge 0.2.0"
git tag v0.2.0
git push origin main --tags
```
