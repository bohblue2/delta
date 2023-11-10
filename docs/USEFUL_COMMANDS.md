```bash
poetry2conda pyproject.toml environment.yaml --dev
```

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
conda env create -f environment.yaml
```

```bash
conda env export > environment.yaml
```