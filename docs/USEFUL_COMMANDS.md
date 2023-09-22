```bash
poetry2conda pyproject.toml environment.yaml
```

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
conda env create -f environment.yaml
```