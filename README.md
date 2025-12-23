# 项目概述

Message Dispatcher 是一个基于 FastAPI 和 RabbitMQ 构建的轻量级消息分发系统，
主要用于 异步任务处理 与 消息队列管理，适合在微服务架构中作为任务分发或消息中转组件使用。

# 快速开始

## 环境要求

- Git
- Docker & Docker Compose
- Python 3.10 及以上
- Poetry（推荐版本：2.2.1）

## 方式一：本地启动（开发说明）

1. **克隆项目**

```bash
git clone <repository-url>
cd message-dispatcher
```

2. **配置环境变量**

复制环境变量模板文件，**并根据您的需求调整配置**：

```bash
cp .env.example .env
```

3. **安装依赖项**

```bash
poetry install
```

> Poetry 安装参考：[官网](https://poetry.pythonlang.cn/docs/#installation)，推荐使用 Poetry 2.2.1
>
> poetry 常用命令（更多操作请自行查阅）：
> - `poetry env use python3.x`: 指定 Python 版本创建虚拟环境
> - `poetry env remove python3.x`: 删除指定 Python 版本的虚拟环境
> - `poetry env activate`: 查看当前虚拟环境路径
> - `poetry run <command>`: 不进入虚拟环境直接执行命令，如：`poetry run pip list`、`poetry run python --version`
> - `poetry install`: 根据 pyproject.toml 和 poetry.lock 安装依赖
> - `poetry add <package>`: 添加依赖（并锁定版本）
> - `poetry remove <package>`: 移除依赖（自动清理子依赖）

4. **启动 RabbitMQ 服务**

如果你已经有可用的 RabbitMQ 服务，可跳过本步骤，否则，推荐使用 Docker 单独启动 RabbitMQ

4.1 修改端口映射

编辑`docker-compose-base.yml`，将`expose`注释掉，并在`ports`中添加宿主机端口映射，例如：

```yaml
  broker:
    image: rabbitmq:3.12-management-alpine
    # expose:
    #   # RabbitMQ 服务端口
    #   - "5672"
    ports:
      # RabbitMQ 管理界面端口
      - "${BROKER_MANAGEMENT_PORT:-15672}:15672"
      - "5673:5672"
```

4.2 启动 RabbitMQ 服务

```bash
docker compose -f docker-compose-base.yml up -d
```

**⚠️注意：**
RabbitMQ 启动完成后，请确认并修改 .env 文件中的 RABBITMQ_URL 配置，确保地址与端口正确

5. **启动 API 服务**

```bash
poetry run python -m dispatcher.main
```

> 无需手动进入虚拟环境，直接使用`poetry run`即可

## 方式二：容器启动（部署说明）

1. **克隆项目**

```bash
git clone <repository-url>
cd message-dispatcher
```

2. **配置环境变量**

复制环境变量模板文件，**并根据您的需求调整配置**：

```bash
cp .env.example .env
```

3. **构建 Docker 镜像**:

```bash
docker build -t message-dispatcher-api-server:latest .
```

4. **启动生产环境**:

```bash
docker compose up -d
```

5. **启动服务**

```bash
docker compose up -d
```

## 服务访问

服务启动成功后，可通过以下地址访问：

- **API 服务**

```cpp
http://<localhost 或 server_ip>:8080
```

- **RabbitMQ 管理界面**

```cpp
http://<RabbitMQ 所在机器 IP>:15672
```

默认账号：
- 用户名：admin
- 密码：admin123
