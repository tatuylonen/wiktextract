FROM docker.io/python
RUN apt update && apt install -y lbzip2
COPY pyproject.toml README.md LICENSE .
COPY src src
RUN python -m pip install -U pip
RUN python -m pip install --use-pep517 .
ENTRYPOINT ["wiktwords"]
