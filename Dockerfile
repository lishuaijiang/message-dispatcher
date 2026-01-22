FROM python:3.10-slim-bookworm

ARG POETRY_VERSION=2.2.1
ARG PIP_MIRROR=https://mirrors.aliyun.com/pypi/simple/
ARG DEPENDENCIES="\
    curl \
    vim \
    less \
    iputils-ping \
    telnet \
    rlwrap \
"

RUN set -ex \
    && { \
        echo "Types: deb"; \
        echo "URIs: http://deb.debian.org/debian"; \
        echo "Suites: bookworm bookworm-updates bookworm-backports"; \
        echo "Components: main contrib non-free non-free-firmware"; \
        echo ""; \
        echo "Types: deb"; \
        echo "URIs: http://security.debian.org/debian-security"; \
        echo "Suites: bookworm-security"; \
        echo "Components: main contrib non-free non-free-firmware"; \
    } > /etc/apt/sources.list.d/debian.sources \
    && rm -f /etc/apt/sources.list

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry==${POETRY_VERSION} -i ${PIP_MIRROR} \
    # 不创建虚拟环境（容器本身就是一个隔离环境）
    && poetry config virtualenvs.create false \
    # 安装依赖，禁止交互，禁止输出带颜色的日志，不安装项目本身
    && poetry install --no-interaction --no-ansi --no-root

COPY dispatcher ./dispatcher

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
