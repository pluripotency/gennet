FROM python:3.11-alpine
RUN pip install --upgrade pip

# REMOVE ANY $TZ to enable /etc/localtime
RUN apk add --no-cache openssh-client bash tzdata \
    && cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && apk del tzdata

RUN addgroup -S user -g 1000 && adduser -S user -G user -u 1000

USER user
WORKDIR /home/user
COPY src/gennet/ ./src/gennet/
COPY pyproject.toml .
COPY README.md .
RUN python -m venv .venv
RUN . .venv/bin/activate
RUN pip install .
