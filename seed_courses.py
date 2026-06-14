"""Seed the database with sample courses and chapters.

Usage:
    python seed_courses.py

Idempotent: skips courses whose title already exists.
"""

from app import create_app, db
from app.models import Chapter, Course

app = create_app()

COURSES = [
    # ========== 1 ==========
    {
        "title": "软件测试基础",
        "description": "了解软件测试的基本概念、测试分类和测试原则，建立测试思维基础。",
        "sort_order": 1,
        "chapters": [
            {
                "title": "什么是软件测试",
                "content": """<h2>软件测试的定义</h2>
<p>软件测试是通过执行程序或系统，验证其是否满足规定需求，并发现缺陷的过程。</p>
<h3>测试的目的</h3>
<ul>
<li>发现软件中的缺陷和错误</li>
<li>验证软件是否满足需求规格</li>
<li>评估软件质量</li>
<li>预防缺陷的产生</li>
</ul>
<h2>测试 vs 调试</h2>
<p><strong>测试</strong>是发现缺陷的过程，<strong>调试</strong>是定位和修复缺陷的过程。测试人员负责发现缺陷，开发人员负责修复缺陷。</p>
<h3>测试的基本原则</h3>
<ol>
<li>测试只能证明缺陷存在，不能证明缺陷不存在</li>
<li>穷尽测试是不可能的</li>
<li>测试尽早介入</li>
<li>缺陷集群效应（80%的缺陷集中在20%的模块中）</li>
<li>杀虫剂悖论（重复相同的测试会降低发现新缺陷的能力）</li>
<li>测试依赖于上下文</li>
<li>无错误谬论（没有发现缺陷不等于软件可用）</li>
</ol>""",
                "sort_order": 1,
            },
            {
                "title": "测试的分类",
                "content": """<h2>按测试层次分类</h2>
<h3>单元测试（Unit Testing）</h3>
<p>对软件中最小可测试单元进行检查和验证，通常由开发人员完成。</p>
<h3>集成测试（Integration Testing）</h3>
<p>将已通过单元测试的模块组合在一起进行测试，验证模块间的接口和交互。</p>
<h3>系统测试（System Testing）</h3>
<p>对完整系统进行测试，验证系统是否满足需求规格。</p>
<h3>验收测试（Acceptance Testing）</h3>
<p>由用户或客户进行的测试，确认系统是否满足业务需求。</p>
<h2>按测试类型分类</h2>
<ul>
<li><strong>功能测试</strong>：验证软件功能是否正确</li>
<li><strong>性能测试</strong>：评估系统在特定负载下的表现</li>
<li><strong>安全测试</strong>：检查系统的安全漏洞</li>
<li><strong>兼容性测试</strong>：验证软件在不同环境下的兼容性</li>
<li><strong>易用性测试</strong>：评估软件的用户体验</li>
</ul>""",
                "sort_order": 2,
            },
            {
                "title": "黑盒测试与白盒测试",
                "content": """<h2>黑盒测试（Black-box Testing）</h2>
<p>不关注程序内部结构和实现，只关注输入和输出。根据需求规格设计测试用例。</p>
<h3>黑盒测试的常用方法</h3>
<ul>
<li>等价类划分</li>
<li>边界值分析</li>
<li>判定表</li>
<li>因果图</li>
<li>状态转换测试</li>
</ul>
<h2>白盒测试（White-box Testing）</h2>
<p>关注程序内部结构和代码逻辑，通过覆盖代码路径来设计测试用例。</p>
<h3>白盒测试的覆盖标准</h3>
<ul>
<li><strong>语句覆盖</strong>：每条语句至少执行一次</li>
<li><strong>判定覆盖</strong>：每个判定的真假分支至少执行一次</li>
<li><strong>条件覆盖</strong>：每个条件的真假值至少出现一次</li>
<li><strong>路径覆盖</strong>：覆盖所有可能的执行路径</li>
</ul>
<h2>灰盒测试</h2>
<p>结合黑盒测试和白盒测试的方法，既关注输入输出，也关注部分内部实现。</p>""",
                "sort_order": 3,
            },
        ],
    },
    # ========== 2 ==========
    {
        "title": "软件测试流程 STLC",
        "description": "学习软件测试生命周期（STLC）的各个阶段，掌握标准化的测试流程。",
        "sort_order": 2,
        "chapters": [
            {
                "title": "测试需求分析",
                "content": """<h2>需求分析的重要性</h2>
<p>测试需求分析是测试流程的第一步，明确"测什么"。只有理解了需求，才能设计出有效的测试用例。</p>
<h3>需求分析的主要活动</h3>
<ol>
<li><strong>需求评审</strong>：检查需求文档的完整性、一致性和可测试性</li>
<li><strong>需求追踪</strong>：建立需求与测试用例的映射关系</li>
<li><strong>测试范围确定</strong>：明确哪些功能需要测试、哪些不需要</li>
</ol>
<h3>需求的可测试性</h3>
<p>好的需求应该满足：</p>
<ul>
<li>明确性：没有歧义</li>
<li>可衡量性：有明确的验收标准</li>
<li>可实现性：技术上可行</li>
<li>完整性：包含所有必要信息</li>
</ul>""",
                "sort_order": 1,
            },
            {
                "title": "测试计划与设计",
                "content": """<h2>测试计划</h2>
<p>测试计划描述测试活动的范围、方法、资源和进度安排。</p>
<h3>测试计划的主要内容</h3>
<ul>
<li>测试范围和目标</li>
<li>测试策略和方法</li>
<li>测试环境</li>
<li>测试资源（人员、工具）</li>
<li>测试进度安排</li>
<li>风险评估和应对</li>
<li>准入和准出标准</li>
</ul>
<h2>测试用例设计</h2>
<p>测试用例是为特定目标设计的一组输入、执行条件和预期结果。</p>
<h3>测试用例的基本要素</h3>
<ul>
<li>用例编号</li>
<li>用例标题</li>
<li>前置条件</li>
<li>测试步骤</li>
<li>预期结果</li>
<li>实际结果</li>
<li>执行状态（通过/失败/阻塞）</li>
</ul>""",
                "sort_order": 2,
            },
            {
                "title": "测试环境与数据管理",
                "content": """<h2>测试环境</h2>
<p>测试环境是执行测试用例所需的硬件、软件和网络配置的集合。</p>
<h3>常见的测试环境层级</h3>
<ul>
<li><strong>开发环境（DEV）</strong>：开发人员自测使用</li>
<li><strong>测试环境（TEST/QA）</strong>：测试团队执行测试</li>
<li><strong>预发布环境（STAGING）</strong>：上线前的最终验证</li>
<li><strong>生产环境（PROD）</strong>：面向真实用户</li>
</ul>
<h2>测试数据管理</h2>
<p>测试数据的质量直接影响测试的有效性。</p>
<h3>测试数据准备方法</h3>
<ul>
<li><strong>手工创建</strong>：适用于小规模、简单的数据</li>
<li><strong>脚本生成</strong>：使用程序批量生成</li>
<li><strong>生产数据脱敏</strong>：从生产环境导出并脱敏</li>
<li><strong>数据工厂</strong>：使用 Faker 等库自动生成</li>
</ul>
<h3>测试数据管理原则</h3>
<ul>
<li>测试前准备，测试后清理</li>
<li>避免测试间的数据依赖</li>
<li>敏感数据必须脱敏</li>
</ul>""",
                "sort_order": 3,
            },
            {
                "title": "测试执行与报告",
                "content": """<h2>测试执行</h2>
<p>按照测试计划和测试用例执行测试，记录测试结果。</p>
<h3>测试执行的流程</h3>
<ol>
<li>搭建测试环境</li>
<li>准备测试数据</li>
<li>执行测试用例</li>
<li>记录测试结果</li>
<li>提交缺陷报告</li>
<li>回归测试</li>
</ol>
<h2>缺陷报告</h2>
<p>发现缺陷后，需要编写规范的缺陷报告。</p>
<h3>缺陷报告的主要内容</h3>
<ul>
<li>缺陷标题（简洁明了）</li>
<li>严重程度（致命/严重/一般/轻微）</li>
<li>优先级（高/中/低）</li>
<li>重现步骤</li>
<li>预期结果 vs 实际结果</li>
<li>测试环境信息</li>
<li>附件（截图、日志）</li>
</ul>
<h2>测试总结报告</h2>
<p>测试完成后，编写测试总结报告，包括测试执行情况、缺陷统计、质量评估和改进建议。</p>""",
                "sort_order": 4,
            },
        ],
    },
    # ========== 3 ==========
    {
        "title": "测试用例设计方法",
        "description": "掌握等价类、边界值、判定表等常用测试用例设计方法。",
        "sort_order": 3,
        "chapters": [
            {
                "title": "等价类划分法",
                "content": """<h2>什么是等价类划分</h2>
<p>等价类划分是将输入数据划分为若干等价类，从每个等价类中选取一个代表性数据作为测试用例的方法。</p>
<h3>有效等价类与无效等价类</h3>
<ul>
<li><strong>有效等价类</strong>：符合需求规格的合理输入数据</li>
<li><strong>无效等价类</strong>：不符合需求规格的不合理输入数据</li>
</ul>
<h2>示例</h2>
<p>需求：年龄输入框，接受 1-150 的整数。</p>
<p>等价类划分：</p>
<ul>
<li>有效等价类：1 ≤ age ≤ 150（整数）</li>
<li>无效等价类：age < 1</li>
<li>无效等价类：age > 150</li>
<li>无效等价类：非整数（小数、字母、特殊字符等）</li>
<li>无效等价类：空值</li>
</ul>""",
                "sort_order": 1,
            },
            {
                "title": "边界值分析法",
                "content": """<h2>什么是边界值分析</h2>
<p>边界值分析是对输入或输出的边界值进行测试的方法。大量的缺陷发生在输入范围的边界上。</p>
<h3>边界值的选取原则</h3>
<ul>
<li>上点：边界上的点</li>
<li>离点：距离边界最近的点</li>
<li>内点：范围内的任意点</li>
</ul>
<h2>示例</h2>
<p>需求：密码长度要求 6-20 个字符。</p>
<p>边界值测试用例：</p>
<ul>
<li>5个字符（刚好小于最小值）→ 无效</li>
<li>6个字符（最小边界值）→ 有效</li>
<li>7个字符（刚好大于最小值）→ 有效</li>
<li>19个字符（刚好小于最大值）→ 有效</li>
<li>20个字符（最大边界值）→ 有效</li>
<li>21个字符（刚好大于最大值）→ 无效</li>
</ul>
<h3>边界值分析的优势</h3>
<p>边界值分析法通常能发现以下类型的缺陷：</p>
<ul>
<li>差一错误（off-by-one）</li>
<li>循环条件错误</li>
<li>数组越界</li>
</ul>""",
                "sort_order": 2,
            },
            {
                "title": "判定表与因果图",
                "content": """<h2>判定表</h2>
<p>判定表用于描述多个条件组合与对应动作之间的关系，适合处理复杂的逻辑判断。</p>
<h3>判定表的组成</h3>
<ul>
<li><strong>条件桩</strong>：列出所有条件</li>
<li><strong>动作桩</strong>：列出所有可能的动作</li>
<li><strong>条件项</strong>：条件的取值组合</li>
<li><strong>动作项</strong>：对应条件组合下的动作</li>
</ul>
<h2>因果图</h2>
<p>因果图用于分析输入条件（因）和输出结果（果）之间的逻辑关系。</p>
<h3>基本逻辑关系</h3>
<ul>
<li><strong>恒等</strong>：若因为真，则果为真</li>
<li><strong>非</strong>：若因为真，则果为假</li>
<li><strong>或</strong>：任一因为真，则果为真</li>
<li><strong>与</strong>：所有因为真，果才为真</li>
</ul>
<h2>使用场景</h2>
<p>当功能需求涉及多个条件的组合判断时，使用判定表或因果图可以系统地覆盖所有组合情况。</p>""",
                "sort_order": 3,
            },
            {
                "title": "状态转换测试",
                "content": """<h2>什么是状态转换测试</h2>
<p>状态转换测试用于测试系统在不同状态之间转换的行为，适用于有状态的系统。</p>
<h3>核心概念</h3>
<ul>
<li><strong>状态</strong>：系统在某一时刻的状况</li>
<li><strong>事件</strong>：触发状态转换的条件</li>
<li><strong>转换</strong>：从一个状态到另一个状态的变化</li>
<li><strong>动作</strong>：转换过程中执行的操作</li>
</ul>
<h2>状态转换图</h2>
<p>用圆圈表示状态，用箭头表示转换，箭头上标注事件和动作。</p>
<h2>测试覆盖标准</h2>
<ul>
<li><strong>所有状态覆盖</strong>：至少到达每个状态一次</li>
<li><strong>所有转换覆盖</strong>：至少执行每个转换一次（推荐）</li>
<li><strong>所有路径覆盖</strong>：覆盖所有可能的转换路径</li>
</ul>
<h2>示例：订单状态</h2>
<p>订单状态：待支付 → 已支付 → 已发货 → 已完成 / 已取消</p>
<p>测试需要覆盖每种状态转换及其触发条件。</p>""",
                "sort_order": 4,
            },
        ],
    },
    # ========== 4 ==========
    {
        "title": "HTTP 与接口测试基础",
        "description": "理解 HTTP 协议基础，为接口测试实训打下理论基础。",
        "sort_order": 4,
        "chapters": [
            {
                "title": "HTTP 协议概述",
                "content": """<h2>什么是 HTTP</h2>
<p>HTTP（HyperText Transfer Protocol）是用于传输超文本的应用层协议，是 Web 通信的基础。</p>
<h3>HTTP 的特点</h3>
<ul>
<li><strong>无状态</strong>：每次请求相互独立，服务器不保留之前的请求信息</li>
<li><strong>基于请求/响应</strong>：客户端发送请求，服务器返回响应</li>
<li><strong>可扩展</strong>：通过自定义头部字段扩展功能</li>
</ul>
<h2>HTTP 请求的组成</h2>
<ol>
<li><strong>请求行</strong>：包含请求方法、URL 和协议版本</li>
<li><strong>请求头</strong>：包含元信息（Content-Type、Authorization 等）</li>
<li><strong>请求体</strong>：包含发送的数据（POST/PUT 请求）</li>
</ol>
<h2>HTTP 响应的组成</h2>
<ol>
<li><strong>状态行</strong>：包含协议版本和状态码</li>
<li><strong>响应头</strong>：包含元信息</li>
<li><strong>响应体</strong>：包含返回的数据</li>
</ol>""",
                "sort_order": 1,
            },
            {
                "title": "请求方法与状态码",
                "content": """<h2>常用请求方法</h2>
<ul>
<li><strong>GET</strong>：获取资源，参数在 URL 中</li>
<li><strong>POST</strong>：提交数据，参数在请求体中</li>
<li><strong>PUT</strong>：更新资源（全量替换）</li>
<li><strong>PATCH</strong>：部分更新资源</li>
<li><strong>DELETE</strong>：删除资源</li>
</ul>
<h2>常见状态码</h2>
<h3>2xx 成功</h3>
<ul>
<li><code>200 OK</code>：请求成功</li>
<li><code>201 Created</code>：资源创建成功</li>
<li><code>204 No Content</code>：成功但无返回内容</li>
</ul>
<h3>4xx 客户端错误</h3>
<ul>
<li><code>400 Bad Request</code>：请求参数错误</li>
<li><code>401 Unauthorized</code>：未认证</li>
<li><code>403 Forbidden</code>：无权限</li>
<li><code>404 Not Found</code>：资源不存在</li>
</ul>
<h3>5xx 服务器错误</h3>
<ul>
<li><code>500 Internal Server Error</code>：服务器内部错误</li>
<li><code>503 Service Unavailable</code>：服务不可用</li>
</ul>""",
                "sort_order": 2,
            },
            {
                "title": "请求头与请求体",
                "content": """<h2>请求头（Headers）</h2>
<p>请求头携带请求的元信息，服务器根据请求头决定如何处理请求。</p>
<h3>常用请求头</h3>
<ul>
<li><code>Content-Type</code>：请求体的数据格式（application/json、application/x-www-form-urlencoded）</li>
<li><code>Authorization</code>：认证信息（Bearer Token、Basic Auth）</li>
<li><code>Accept</code>：客户端期望的响应格式</li>
<li><code>User-Agent</code>：客户端信息</li>
<li><code>Cookie</code>：会话信息</li>
</ul>
<h2>请求体（Body）</h2>
<p>POST/PUT/PATCH 请求通常携带请求体。</p>
<h3>常见的请求体格式</h3>
<ul>
<li><strong>JSON</strong>：<code>{"username": "admin", "password": "123456"}</code></li>
<li><strong>表单</strong>：<code>username=admin&password=123456</code></li>
<li><strong>XML</strong>：使用 XML 格式的数据</li>
<li><strong>文件上传</strong>：使用 multipart/form-data</li>
</ul>
<h2>Content-Type 对照</h2>
<table>
<tr><th>场景</th><th>Content-Type</th></tr>
<tr><td>JSON 数据</td><td>application/json</td></tr>
<tr><td>表单提交</td><td>application/x-www-form-urlencoded</td></tr>
<tr><td>文件上传</td><td>multipart/form-data</td></tr>
</table>""",
                "sort_order": 3,
            },
            {
                "title": "接口测试入门",
                "content": """<h2>什么是接口测试</h2>
<p>接口测试是对系统组件之间的接口进行测试，验证接口的功能、性能和安全性。</p>
<h3>接口测试的范围</h3>
<ul>
<li>API 功能正确性</li>
<li>参数验证（必填、类型、范围）</li>
<li>错误处理（异常输入、边界情况）</li>
<li>响应格式和内容</li>
<li>性能和并发</li>
</ul>
<h2>接口测试 vs UI 测试</h2>
<table>
<tr><th>对比项</th><th>接口测试</th><th>UI 测试</th></tr>
<tr><td>执行速度</td><td>快</td><td>慢</td></tr>
<tr><td>维护成本</td><td>低</td><td>高</td></tr>
<tr><td>覆盖范围</td><td>业务逻辑层</td><td>用户界面层</td></tr>
<tr><td>发现问题时机</td><td>较早</td><td>较晚</td></tr>
</table>
<h2>常用接口测试工具</h2>
<ul>
<li><strong>Postman</strong>：图形化接口测试工具</li>
<li><strong>cURL</strong>：命令行 HTTP 工具</li>
<li><strong>Python requests</strong>：Python HTTP 库</li>
<li><strong>JMeter</strong>：性能和接口测试工具</li>
</ul>""",
                "sort_order": 4,
            },
        ],
    },
    # ========== 5 ==========
    {
        "title": "接口断言与验证",
        "description": "学习接口测试中的断言方法，验证响应数据的正确性。",
        "sort_order": 5,
        "chapters": [
            {
                "title": "什么是断言",
                "content": """<h2>断言的概念</h2>
<p>断言是测试中用于验证实际结果是否符合预期的机制。当断言失败时，测试用例标记为失败。</p>
<h3>断言的作用</h3>
<ul>
<li>自动验证测试结果</li>
<li>减少人工判断</li>
<li>提高测试效率</li>
<li>生成明确的测试报告</li>
</ul>
<h2>接口测试中常见的断言类型</h2>
<ol>
<li><strong>状态码断言</strong>：验证 HTTP 状态码</li>
<li><strong>响应时间断言</strong>：验证响应时间在可接受范围内</li>
<li><strong>响应体断言</strong>：验证返回的数据内容</li>
<li><strong>响应头断言</strong>：验证响应头信息</li>
</ol>""",
                "sort_order": 1,
            },
            {
                "title": "JSON 响应断言",
                "content": """<h2>JSON 响应解析</h2>
<p>大多数 API 返回 JSON 格式的数据。断言时需要先解析 JSON，再验证具体字段。</p>
<h3>常见断言场景</h3>
<ul>
<li>验证某个字段的值</li>
<li>验证字段是否存在</li>
<li>验证数组长度</li>
<li>验证嵌套对象的属性</li>
<li>验证数据类型</li>
</ul>
<h2>Python requests + assert 示例</h2>
<pre><code>import requests

resp = requests.get("http://api.example.com/users/1")
assert resp.status_code == 200

data = resp.json()
assert data["name"] == "张三"
assert data["age"] == 25
assert "email" in data</code></pre>
<h3>断言的最佳实践</h3>
<ul>
<li>每个测试用例至少包含一个断言</li>
<li>断言消息要清晰，便于定位问题</li>
<li>避免在一个断言中验证过多条件</li>
<li>优先验证关键业务逻辑</li>
</ul>""",
                "sort_order": 2,
            },
            {
                "title": "响应时间与性能断言",
                "content": """<h2>为什么要验证响应时间</h2>
<p>接口的功能正确并不代表质量达标。响应时间过慢会直接影响用户体验和系统可用性。</p>
<h3>响应时间断言示例</h3>
<pre><code>import requests

resp = requests.get("http://api.example.com/data")
assert resp.elapsed.total_seconds() < 2.0, "响应时间超过2秒"</code></pre>
<h2>常见的性能指标</h2>
<ul>
<li><strong>响应时间</strong>：从发送请求到收到完整响应的时间</li>
<li><strong>吞吐量</strong>：单位时间内处理的请求数</li>
<li><strong>并发数</strong>：同时处理的请求数</li>
<li><strong>错误率</strong>：失败请求占总请求的比例</li>
</ul>
<h3>断言策略</h3>
<p>建议设置合理的阈值，既要满足业务需求，也要避免过于严格导致误报。</p>""",
                "sort_order": 3,
            },
        ],
    },
    # ========== 6 ==========
    {
        "title": "自动化测试实践",
        "description": "了解自动化测试的概念、框架和最佳实践。",
        "sort_order": 6,
        "chapters": [
            {
                "title": "自动化测试概述",
                "content": """<h2>什么是自动化测试</h2>
<p>自动化测试是使用工具和脚本自动执行测试用例、验证结果并生成报告的过程。</p>
<h3>自动化测试的优势</h3>
<ul>
<li>提高测试效率，减少重复劳动</li>
<li>提高测试覆盖率</li>
<li>支持持续集成/持续交付（CI/CD）</li>
<li>减少人为错误</li>
<li>支持回归测试</li>
</ul>
<h3>适合自动化的情况</h3>
<ul>
<li>重复性高的测试</li>
<li>回归测试</li>
<li>数据驱动的测试</li>
<li>性能测试</li>
</ul>
<h3>不适合自动化的情况</h3>
<ul>
<li>需求频繁变化的功能</li>
<li>一次性测试</li>
<li>需要人工判断的测试（如界面美观度）</li>
<li>探索性测试</li>
</ul>""",
                "sort_order": 1,
            },
            {
                "title": "Python 测试框架 pytest",
                "content": """<h2>pytest 简介</h2>
<p>pytest 是 Python 最流行的测试框架，以简洁的语法和强大的功能著称。</p>
<h3>pytest 的特点</h3>
<ul>
<li>使用 <code>assert</code> 语句进行断言，无需记忆复杂的断言方法</li>
<li>自动发现和收集测试用例</li>
<li>丰富的插件生态</li>
<li>支持参数化测试</li>
<li>支持 fixture 机制管理测试资源</li>
</ul>
<h2>基本用法</h2>
<pre><code># test_example.py
def test_addition():
    assert 1 + 1 == 2

def test_string():
    assert "hello".upper() == "HELLO"</code></pre>
<p>运行测试：<code>pytest test_example.py -v</code></p>
<h2>Fixture 机制</h2>
<pre><code>import pytest

@pytest.fixture
def sample_data():
    return {"name": "测试用户", "age": 20}

def test_user_name(sample_data):
    assert sample_data["name"] == "测试用户"</code></pre>""",
                "sort_order": 2,
            },
            {
                "title": "接口自动化测试实践",
                "content": """<h2>接口自动化测试的步骤</h2>
<ol>
<li>分析接口文档，确定测试范围</li>
<li>设计测试用例（正常流程 + 异常流程）</li>
<li>编写自动化测试脚本</li>
<li>执行测试并分析结果</li>
<li>维护和更新测试脚本</li>
</ol>
<h2>使用 pytest + requests 进行接口测试</h2>
<pre><code>import pytest
import requests

BASE_URL = "http://localhost:5000"

def test_health():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_login_success():
    resp = requests.post(f"{BASE_URL}/login", data={
        "username": "testuser",
        "password": "test123456"
    })
    assert resp.status_code == 302</code></pre>
<h3>测试组织建议</h3>
<ul>
<li>按功能模块组织测试文件</li>
<li>使用 conftest.py 管理公共 fixture</li>
<li>使用参数化减少重复代码</li>
<li>生成 HTML 测试报告</li>
</ul>""",
                "sort_order": 3,
            },
        ],
    },
    # ========== 7 ==========
    {
        "title": "缺陷管理与测试报告",
        "description": "学习缺陷的生命周期、报告编写规范和测试度量指标。",
        "sort_order": 7,
        "chapters": [
            {
                "title": "缺陷的生命周期",
                "content": """<h2>缺陷状态流转</h2>
<p>缺陷从发现到关闭经历多个状态，形成完整的生命周期。</p>
<h3>常见缺陷状态</h3>
<ul>
<li><strong>新建（New）</strong>：测试人员发现并提交缺陷</li>
<li><strong>确认（Confirmed）</strong>：开发人员确认缺陷存在</li>
<li><strong>修复中（In Progress）</strong>：开发人员正在修复</li>
<li><strong>已修复（Fixed）</strong>：修复完成，等待验证</li>
<li><strong>验证通过（Verified）</strong>：测试人员确认修复有效</li>
<li><strong>关闭（Closed）</strong>：缺陷生命周期结束</li>
<li><strong>重新打开（Reopened）</strong>：验证未通过，重新激活</li>
</ul>
<h2>缺陷管理工具</h2>
<ul>
<li>Jira</li>
<li>Bugzilla</li>
<li>禅道（ZenTao）</li>
<li>Mantis</li>
</ul>""",
                "sort_order": 1,
            },
            {
                "title": "编写高质量缺陷报告",
                "content": """<h2>好的缺陷报告的标准</h2>
<p>高质量的缺陷报告能帮助开发人员快速定位和修复问题。</p>
<h3>缺陷报告要素</h3>
<ol>
<li><strong>标题</strong>：简洁描述问题（什么 + 在哪里 + 怎么了）</li>
<li><strong>环境信息</strong>：操作系统、浏览器、版本号</li>
<li><strong>重现步骤</strong>：详细的操作步骤，确保可复现</li>
<li><strong>预期结果</strong>：正确的行为应该是什么</li>
<li><strong>实际结果</strong>：实际发生了什么</li>
<li><strong>附件</strong>：截图、录屏、日志</li>
</ol>
<h3>缺陷报告示例</h3>
<p><strong>标题</strong>：登录页面 - 输入正确密码后提示"密码错误"</p>
<p><strong>重现步骤</strong>：</p>
<ol>
<li>打开登录页面</li>
<li>输入用户名 admin</li>
<li>输入密码 123456</li>
<li>点击登录按钮</li>
</ol>
<p><strong>预期结果</strong>：登录成功，跳转到首页</p>
<p><strong>实际结果</strong>：页面提示"用户名或密码错误"</p>""",
                "sort_order": 2,
            },
            {
                "title": "测试度量与报告",
                "content": """<h2>常用的测试度量指标</h2>
<ul>
<li><strong>用例执行率</strong> = 已执行用例数 / 总用例数 × 100%</li>
<li><strong>用例通过率</strong> = 通过用例数 / 已执行用例数 × 100%</li>
<li><strong>缺陷密度</strong> = 缺陷数 / 代码规模（千行）</li>
<li><strong>缺陷修复率</strong> = 已修复缺陷数 / 总缺陷数 × 100%</li>
<li><strong>回归通过率</strong> = 回归通过数 / 回归执行数 × 100%</li>
</ul>
<h2>测试总结报告模板</h2>
<ol>
<li>测试概述（范围、时间、人员）</li>
<li>测试执行情况（用例统计）</li>
<li>缺陷分析（按严重程度、模块分布）</li>
<li>质量评估（是否达到准出标准）</li>
<li>风险说明</li>
<li>改进建议</li>
</ol>""",
                "sort_order": 3,
            },
        ],
    },
    # ========== 8 ==========
    {
        "title": "性能测试基础",
        "description": "了解性能测试的类型、指标和常用工具。",
        "sort_order": 8,
        "chapters": [
            {
                "title": "性能测试概述",
                "content": """<h2>什么是性能测试</h2>
<p>性能测试是验证系统在特定负载条件下的响应时间、吞吐量、资源利用率等性能指标是否满足要求的测试活动。</p>
<h3>性能测试的类型</h3>
<ul>
<li><strong>负载测试（Load Testing）</strong>：逐步增加负载，观察系统行为</li>
<li><strong>压力测试（Stress Testing）</strong>：超过系统承受能力，观察系统极限</li>
<li><strong>并发测试（Concurrency Testing）</strong>：多用户同时操作</li>
<li><strong>稳定性测试（Endurance Testing）</strong>：长时间运行，检查内存泄漏等</li>
</ul>
<h2>关键性能指标</h2>
<ul>
<li><strong>响应时间</strong>：用户发出请求到收到响应的时间</li>
<li><strong>吞吐量（TPS/QPS）</strong>：每秒处理的事务/请求数</li>
<li><strong>并发用户数</strong>：同时在线的用户数量</li>
<li><strong>错误率</strong>：失败请求的比例</li>
<li><strong>资源利用率</strong>：CPU、内存、磁盘、网络的使用率</li>
</ul>""",
                "sort_order": 1,
            },
            {
                "title": "性能测试指标与策略",
                "content": """<h2>如何制定性能目标</h2>
<p>性能测试需要有明确的目标，否则无法判断系统是否达标。</p>
<h3>常见性能目标</h3>
<ul>
<li>页面加载时间 < 3 秒</li>
<li>API 响应时间 < 500ms（P95）</li>
<li>系统支持 1000 并发用户</li>
<li>CPU 使用率 < 80%</li>
<li>错误率 < 0.1%</li>
</ul>
<h2>性能测试策略</h2>
<ol>
<li><strong>基准测试</strong>：记录当前系统的性能基线</li>
<li><strong>逐步加压</strong>：从低负载开始，逐步增加到目标负载</li>
<li><strong>峰值测试</strong>：模拟业务高峰期的流量</li>
<li><strong>稳定性测试</strong>：在目标负载下持续运行数小时</li>
</ol>
<h2>性能瓶颈分析</h2>
<p>当性能不达标时，需要从以下方面排查：</p>
<ul>
<li>数据库慢查询</li>
<li>代码层面的低效算法</li>
<li>内存泄漏</li>
<li>网络延迟</li>
<li>第三方服务响应慢</li>
</ul>""",
                "sort_order": 2,
            },
            {
                "title": "性能测试工具",
                "content": """<h2>常用性能测试工具</h2>
<h3>JMeter</h3>
<p>Apache JMeter 是最流行的开源性能测试工具，支持多种协议。</p>
<ul>
<li>图形化界面设计测试计划</li>
<li>支持参数化和关联</li>
<li>丰富的监听器和报告</li>
<li>支持分布式压测</li>
</ul>
<h3>Locust</h3>
<p>Python 编写的负载测试工具，使用代码定义用户行为。</p>
<pre><code>from locust import HttpUser, task

class WebsiteUser(HttpUser):
    @task
    def index(self):
        self.client.get("/")

    @task
    def login(self):
        self.client.post("/login", data={
            "username": "test",
            "password": "123456"
        })</code></pre>
<h3>其他工具</h3>
<ul>
<li><strong>k6</strong>：JavaScript 编写的现代负载测试工具</li>
<li><strong>wrk</strong>：高性能 HTTP 基准测试工具</li>
<li><strong>Gatling</strong>：基于 Scala 的高性能测试工具</li>
</ul>""",
                "sort_order": 3,
            },
        ],
    },
    # ========== 9 ==========
    {
        "title": "安全测试入门",
        "description": "了解常见的 Web 安全漏洞和安全测试方法。",
        "sort_order": 9,
        "chapters": [
            {
                "title": "常见 Web 安全漏洞",
                "content": """<h2>OWASP Top 10</h2>
<p>OWASP（开放式 Web 应用安全项目）定期发布最严重的 Web 安全风险清单。</p>
<h3>常见漏洞类型</h3>
<ul>
<li><strong>SQL 注入</strong>：通过输入恶意 SQL 语句操纵数据库</li>
<li><strong>XSS（跨站脚本）</strong>：在页面中注入恶意脚本</li>
<li><strong>CSRF（跨站请求伪造）</strong>：伪造用户请求执行非授权操作</li>
<li><strong>越权访问</strong>：访问未授权的资源或功能</li>
<li><strong>敏感信息泄露</strong>：密码、密钥等敏感数据暴露</li>
</ul>
<h2>安全测试的重要性</h2>
<p>安全漏洞可能导致数据泄露、资金损失、声誉受损等严重后果。安全测试应在开发全生命周期中持续进行。</p>""",
                "sort_order": 1,
            },
            {
                "title": "接口安全测试",
                "content": """<h2>接口层面的安全风险</h2>
<ul>
<li><strong>未授权访问</strong>：接口缺少身份认证</li>
<li><strong>参数篡改</strong>：修改请求参数获取非法数据</li>
<li><strong>重放攻击</strong>：截获并重复发送请求</li>
<li><strong>暴力破解</strong>：穷举密码或 token</li>
<li><strong>注入攻击</strong>：通过参数注入恶意代码</li>
</ul>
<h2>接口安全测试要点</h2>
<ol>
<li>验证认证机制（Token、Session）</li>
<li>验证授权控制（角色、权限）</li>
<li>验证参数校验（类型、长度、范围）</li>
<li>验证敏感数据加密传输（HTTPS）</li>
<li>验证频率限制（防暴力破解）</li>
</ol>
<h2>常用安全测试工具</h2>
<ul>
<li><strong>Burp Suite</strong>：Web 安全测试集成平台</li>
<li><strong>OWASP ZAP</strong>：开源安全扫描工具</li>
<li><strong>sqlmap</strong>：自动化 SQL 注入检测工具</li>
</ul>""",
                "sort_order": 2,
            },
            {
                "title": "安全测试实践",
                "content": """<h2>安全测试的层次</h2>
<ul>
<li><strong>代码审计</strong>：审查源代码中的安全问题</li>
<li><strong>漏洞扫描</strong>：使用工具自动扫描已知漏洞</li>
<li><strong>渗透测试</strong>：模拟攻击者尝试突破系统</li>
<li><strong>安全配置检查</strong>：检查服务器和应用的安全配置</li>
</ul>
<h2>安全测试流程</h2>
<ol>
<li>信息收集：了解目标系统的架构和技术栈</li>
<li>漏洞发现：使用工具和手动方法发现潜在漏洞</li>
<li>漏洞验证：确认漏洞的真实性和可利用性</li>
<li>报告编写：记录漏洞详情和修复建议</li>
<li>修复验证：确认漏洞已被正确修复</li>
</ol>
<h2>安全编码建议</h2>
<ul>
<li>对所有输入进行验证和过滤</li>
<li>使用参数化查询防止 SQL 注入</li>
<li>对输出进行编码防止 XSS</li>
<li>使用 CSRF Token 防止 CSRF</li>
<li>敏感数据加密存储和传输</li>
</ul>""",
                "sort_order": 3,
            },
        ],
    },
]


def seed():
    """Insert missing courses and chapters without deleting existing records."""
    with app.app_context():
        inserted_courses = 0
        inserted_chapters = 0
        updated_chapter_orders = 0
        for course_data in COURSES:
            course = Course.query.filter_by(title=course_data["title"]).first()
            if course is None:
                course = Course(
                    title=course_data["title"],
                    description=course_data["description"],
                    sort_order=course_data["sort_order"],
                )
                db.session.add(course)
                db.session.flush()
                inserted_courses += 1

            for ch_data in course_data["chapters"]:
                exists = Chapter.query.filter_by(
                    course_id=course.id, title=ch_data["title"]
                ).first()
                if exists is not None:
                    if exists.sort_order != ch_data["sort_order"]:
                        exists.sort_order = ch_data["sort_order"]
                        updated_chapter_orders += 1
                    continue

                chapter = Chapter(
                    course_id=course.id,
                    title=ch_data["title"],
                    content=ch_data["content"],
                    sort_order=ch_data["sort_order"],
                )
                db.session.add(chapter)
                inserted_chapters += 1

        db.session.commit()
        if inserted_courses or inserted_chapters or updated_chapter_orders:
            print(
                f"已插入 {inserted_courses} 门课程、"
                f"{inserted_chapters} 个章节，"
                f"更新 {updated_chapter_orders} 个章节排序。"
            )
        else:
            print("所有课程和章节数据已存在，跳过插入。")


if __name__ == "__main__":
    seed()
