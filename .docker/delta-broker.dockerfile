FROM delta:latest
ENV PYSETUP_PATH="/opt/pysetup"

# Run Application
WORKDIR $PYSETUP_PATH
CMD poetry run python -m delta -s broker
