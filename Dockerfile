# Gate an eval from inside a container:
#
#   docker build -t evalgate .
#   docker run --rm evalgate proportions \
#     --baseline-score 0.90 --baseline-n 2000 \
#     --candidate-score 0.88 --candidate-n 2000
#
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/jmweb-org/evalgate"
LABEL org.opencontainers.image.description="Decide whether an eval delta is a real regression or sampling noise."
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --no-cache-dir .

ENTRYPOINT ["evalgate"]
CMD ["--help"]
