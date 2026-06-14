# 基于 Flask 的软件测试学习与接口测试实训平台

本项目是一个面向软件测试学习场景的本科毕业设计系统，采用 Flask 应用工厂与 Blueprint 架构开发，集课程学习、题库练习、错题管理、接口测试实训和学习数据统计于一体。

系统使用 Jinja2 与 Bootstrap 构建页面，使用 Flask-SQLAlchemy 操作 MySQL 数据库，并通过 pytest 对主要业务流程和安全边界进行自动化测试。项目适合软件测试初学者进行基础知识学习、练习巩固和接口测试实践。

> 本项目主要用于教学、学习和毕业设计演示。内置模拟接口仅供本系统的接口实训模块使用。

## 技术栈

| 分类 | 技术 | 用途 |
| --- | --- | --- |
| 开发语言 | Python 3.10 / 3.11 | 后端开发与自动化测试 |
| Web 框架 | Flask | Web 应用、路由与 Blueprint 管理 |
| 模板引擎 | Jinja2 | 服务端页面渲染 |
| ORM | Flask-SQLAlchemy | 数据模型与数据库操作 |
| 用户认证 | Flask-Login | 登录状态与访问控制 |
| 表单安全 | Flask-WTF | CSRF 防护 |
| 数据库驱动 | PyMySQL | Python 连接 MySQL |
| 数据库 | MySQL 8 | 持久化存储业务数据 |
| 前端样式 | Bootstrap、CSS | 响应式页面与轻量仪表盘界面 |
| HTTP 请求 | requests | 执行内置模拟接口测试 |
| 测试框架 | pytest | 单元测试与功能回归测试 |
| 配置管理 | python-dotenv | 从 `.env` 读取本地配置 |

## 功能模块

### 1. 用户与权限

- 用户注册、登录和退出
- 个人中心与用户信息展示
- 密码哈希存储
- 登录状态校验和受保护页面访问控制

### 2. 课程学习

- 查看软件测试课程列表
- 查看课程章节和章节内容
- 登录用户可标记章节完成
- 按当前用户记录课程学习进度

### 3. 题库练习

- 查看软件测试题目列表
- 支持单选题和判断题练习
- 提交后展示答题结果、正确答案和答案解析
- 支持下一题、重新练习等操作

### 4. 错题本与答题记录

- 保存当前用户的答题记录
- 自动记录错题并累计错误次数
- 从错题本重新进入答题模式
- 防止空答案或非法答案写入数据库

### 5. 接口测试实训

- 查看接口实训任务及任务详情
- 填写请求头、请求参数和断言条件
- 支持状态码、返回字段和响应时间断言
- 保存测试用例、测试结果和请求异常信息
- 当前用户只能查看自己的接口测试结果
- 仅允许访问本项目内置的 `/mock/...` 模拟接口

### 6. 首页统计与学习报告

登录后，首页按当前用户展示以下统计数据：

- 已完成章节数、章节总数和学习进度
- 答题总数、答对数量和正确率
- 错题数量
- 接口测试执行次数、通过次数和通过率

未登录用户可以正常访问首页，但不会展示个人学习统计。

### 7. 系统状态检查

- `/health`：检查 Flask 服务是否正常
- `/db-check`：通过 SQLAlchemy 执行 `SELECT 1`，检查 MySQL 连接是否正常

## 项目结构

项目采用应用工厂模式创建 Flask 实例，并使用 Blueprint 按模块组织路由。

```text
software_testing_platform/
├── app.py                         # 项目启动入口
├── config.py                      # 环境变量与数据库配置
├── init_db.py                     # 数据库表初始化脚本
├── seed_courses.py                # 课程与章节种子数据
├── seed_questions.py              # 题库种子数据
├── seed_training_tasks.py         # 接口实训任务种子数据
├── requirements.txt               # Python 依赖列表
├── .env.example                   # 环境变量示例
├── .gitignore                     # Git 忽略规则
├── app/
│   ├── __init__.py                # create_app()、扩展初始化与 Blueprint 注册
│   ├── models.py                  # SQLAlchemy 数据模型
│   ├── routes/
│   │   ├── main.py                # 首页、健康检查、数据库检查
│   │   ├── auth.py                # 注册、登录、退出、个人中心
│   │   ├── course.py              # 课程学习路由
│   │   ├── question.py            # 题库、错题本、答题记录路由
│   │   └── training.py            # 接口实训与结果路由
│   ├── services/                  # 业务服务层
│   ├── mock_api/                  # 内置模拟接口
│   ├── templates/                 # Jinja2 页面模板
│   └── static/                    # CSS 等静态资源
└── tests/                         # pytest 自动化测试
```

主要数据模型包括：

- `User`
- `Course`、`Chapter`、`LearningRecord`
- `Question`、`AnswerRecord`、`WrongQuestion`
- `TrainingTask`、`ApiTestCase`、`ApiTestResult`

## 环境要求

- Windows 10 / 11
- Python 3.10 或 Python 3.11
- MySQL 8.0 及以上版本
- pip
- 支持现代 Web 标准的浏览器

建议在 Python 虚拟环境中运行项目。

## 安装依赖

进入项目根目录，在 PowerShell 中执行：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果 PowerShell 阻止当前终端激活虚拟环境，可临时执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## 数据库配置

### 1. 创建数据库

可以在 DBeaver 或 MySQL 客户端中执行：

```sql
CREATE DATABASE IF NOT EXISTS softtest_platform
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

### 2. 创建本地环境配置

复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

根据本机 MySQL 配置编辑 `.env`：

```dotenv
FLASK_DEBUG=true
SECRET_KEY=replace-with-a-random-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_NAME=softtest_platform
DB_USERNAME=your_mysql_username
DB_PASSWORD=your_mysql_password
```

请将 `SECRET_KEY`、数据库用户名和数据库密码替换为本机实际配置。不要将 `.env` 或真实凭据提交到 Git 仓库。

`config.py` 会读取以上环境变量，并构建如下格式的数据库连接：

```text
mysql+pymysql://<username>:<password>@<host>:<port>/<database>?charset=utf8mb4
```

## 初始化数据库

确认 MySQL 服务已经启动、数据库已经创建，并且 `.env` 配置正确，然后执行：

```powershell
python init_db.py
```

该命令会根据 `app/models.py` 中的数据模型创建系统所需的数据表，不会自动导入课程、题目和实训任务。

## 导入初始数据

依次执行以下命令：

```powershell
python seed_courses.py
python seed_questions.py
python seed_training_tasks.py
```

在全新数据库中，当前种子脚本将生成：

| 数据类型 | 数量 |
| --- | ---: |
| 课程 | 9 门 |
| 章节 | 30 章 |
| 题目 | 60 道左右 |
| 接口实训任务 | 4 个 |

课程和题库种子脚本采用幂等设计，重复执行不会重复插入同名课程、章节或题目，也不会删除用户已有的学习记录、答题记录和错题记录。

## 启动项目

激活虚拟环境后执行：

```powershell
python app.py
```

开发服务器默认运行在：

```text
http://127.0.0.1:5000
```

控制台出现 Flask 启动信息后，即可通过浏览器访问系统。

## 运行测试

在项目根目录执行全量测试：

```powershell
python -m pytest -q
```

当前项目测试基线为：

```text
139 passed
```

测试覆盖用户认证、CSRF、课程学习、题库练习、错题记录、接口实训、安全限制、首页统计、健康检查和数据库检查等主要功能。

## 主要页面地址

| 页面或接口 | 地址 | 访问说明 |
| --- | --- | --- |
| 首页 / 学习统计 | `/` | 所有人可访问，登录后显示个人统计 |
| 用户注册 | `/register` | 未登录用户使用 |
| 用户登录 | `/login` | 未登录用户使用 |
| 个人中心 | `/profile` | 需要登录 |
| 课程列表 | `/courses` | 所有人可查看 |
| 课程详情 | `/courses/<course_id>` | 将参数替换为实际课程 ID |
| 章节详情 | `/chapters/<chapter_id>` | 将参数替换为实际章节 ID |
| 题库列表 | `/questions` | 所有人可查看 |
| 题目练习 | `/questions/<question_id>` | 提交答案需要登录 |
| 错题本 | `/wrong-questions` | 需要登录 |
| 答题记录 | `/answer-records` | 需要登录 |
| 接口实训列表 | `/training` | 所有人可查看 |
| 接口实训详情 | `/training/<task_id>` | 执行测试需要登录 |
| 接口测试结果 | `/training/results` | 需要登录，仅显示当前用户数据 |
| 服务健康检查 | `/health` | 返回服务状态 JSON |
| 数据库连接检查 | `/db-check` | 返回数据库连接状态 JSON |

内置模拟接口包括：

- `POST /mock/login`
- `GET /mock/user/<user_id>`
- `POST /mock/product/add`

## 测试账号说明

项目不预置平台登录账号。首次启动后，请访问 `/register` 自行注册测试账号，再使用该账号体验学习记录、答题记录、错题本、接口实训结果和首页统计功能。

`/mock/login` 示例中的 `admin` 和 `123456` 仅为内置模拟接口的测试参数，不是平台登录账号，也不代表真实用户凭据。

用于截图或答辩演示时，建议单独注册演示账号，并避免在 README、截图或 Git 提交中暴露真实密码。

## 安全说明

- **密码安全**：用户密码通过 Werkzeug 安全哈希函数保存，数据库不存储明文密码。
- **CSRF 防护**：注册、登录、退出及其他表单操作启用 Flask-WTF CSRF 防护；退出登录使用 POST 请求。
- **登录跳转安全**：登录后的 `next` 参数仅允许跳转到站内安全路径，避免开放重定向。
- **数据隔离**：学习记录、答题记录、错题记录、接口测试用例和结果均按当前登录用户处理。
- **接口实训边界**：实训模块只接受以 `/mock/...` 开头的项目内置相对路径，不允许访问外部 URL、`localhost`、`127.0.0.1`、内网地址或云元数据地址。
- **断言校验**：接口测试至少需要设置一个断言条件；非法 JSON、非对象响应和请求异常会被安全处理，不会直接导致页面 500。
- **敏感配置**：数据库密码和 `SECRET_KEY` 仅保存在本地 `.env` 中，`.env` 已通过 `.gitignore` 忽略。
- **环境隔离**：`venv`、`.venv`、`__pycache__`、pytest 缓存等本地文件不应提交到 Git 仓库。

## 毕设说明

本系统主要面向软件测试学习与接口测试实训场景，围绕“学习、练习、实践、统计”形成完整流程：

1. 通过课程模块学习软件测试基础、测试流程、黑盒测试、接口测试和自动化测试等内容。
2. 通过题库练习、答题记录和错题本巩固知识并进行针对性复习。
3. 通过内置模拟接口完成请求配置、断言设计、结果分析等接口测试实践。
4. 通过首页学习报告查看个人课程、答题和接口实训进度。

项目采用 Flask 单体应用架构，结构清晰、部署成本较低，适合作为本科毕业设计进行功能演示、系统测试和论文说明，也适合软件测试初学者进行课程学习、题库练习和接口测试实践。

## 说明

本项目为学习与毕业设计用途。若用于生产环境，还需要进一步完善部署方式、日志审计、权限模型、限流、监控、备份与密钥管理等能力。
