# Career Platform — 数据库表结构

> 数据库类型: SQLite (本地开发) / MySQL 8.0 (生产)
> 初始化脚本: `backend/scripts/init_db.sql`

---

## 1. users — 用户表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 用户 ID |
| username | VARCHAR(50) | NOT NULL, UNIQUE | 用户名 |
| email | VARCHAR(100) | NOT NULL, UNIQUE | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 密码哈希 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引:** 无显式索引（username/email 自带 UNIQUE）

---

## 2. jobs — 岗位表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 岗位 ID |
| job_title | VARCHAR(255) | NOT NULL | 岗位名称 |
| company | VARCHAR(255) | NOT NULL | 公司名称 |
| industry | VARCHAR(255) | | 行业 |
| city | VARCHAR(100) | | 城市 |
| salary_range | VARCHAR(100) | | 薪资范围 |
| company_scale | VARCHAR(50) | | 公司规模 |
| job_description | TEXT | | 岗位描述 |
| requirements | TEXT | | 任职要求 |
| company_description | TEXT | | 公司介绍 |
| job_details | TEXT | | 岗位详情 |
| publish_date | DATE | | 发布日期 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

## 3. user_profiles — 用户画像表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 记录 ID |
| user_id | INTEGER | NOT NULL, UNIQUE, FK → users.id | 用户 ID (一对一) |
| profile_data | JSON | NOT NULL | 画像数据 (7维雷达图等) |
| status | VARCHAR(50) | DEFAULT 'active' | 状态 |
| match_score | DECIMAL(5,2) | | 匹配分数 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

---

## 4. favorites — 收藏表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 记录 ID |
| user_id | INTEGER | NOT NULL, FK → users.id | 用户 ID |
| job_id | INTEGER | NOT NULL, FK → jobs.id | 岗位 ID |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 收藏时间 |

**索引/约束:** UNIQUE(user_id, job_id)

---

## 5. career_plans — 职业规划表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 规划 ID |
| user_id | INTEGER | NOT NULL, FK → users.id | 用户 ID |
| target_position | VARCHAR(255) | | 目标岗位 |
| target_company | VARCHAR(255) | | 目标公司 |
| timeline_months | INTEGER | | 时间线 (月) |
| status | VARCHAR(50) | DEFAULT 'active' | 状态 |
| plan_data | JSON | | 规划详情 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

---

## 6. job_profiles — 岗位画像表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 记录 ID |
| job_id | INTEGER | NOT NULL, FK → jobs.id | 岗位 ID |
| profile_data | JSON | | 岗位画像数据 |
| summary | VARCHAR(1024) | | 岗位摘要 |
| core_skills | JSON | | 核心技能列表 |
| career_path | JSON | | 职业发展路径 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

---

## 7. promotion_transition — 晋升/转型路径表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 记录 ID |
| job_id | INTEGER | FK → jobs.id | 关联岗位 |
| current_role | VARCHAR(255) | NOT NULL | 当前角色 |
| next_role | VARCHAR(255) | NOT NULL | 下一级角色 |
| required_skills | JSON | | 所需技能 |
| years_exp | INTEGER | | 所需年限 |
| transition_type | VARCHAR(50) | DEFAULT 'promotion' | 类型 (promotion/lateral) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

## 8. matching_report — 岗位匹配报告表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 报告 ID |
| user_id | INTEGER | NOT NULL, FK → users.id | 用户 ID |
| job_name | VARCHAR(255) | NOT NULL | 匹配岗位名称 |
| industry | VARCHAR(255) | | 行业 |
| city | VARCHAR(100) | | 城市 |
| match_score | DECIMAL(5,2) | | 匹配度评分 |
| report_data | JSON | | 报告详细数据 |
| publish_date | DATE | | 发布日期 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

## 9. learning_plans — 学习计划表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 计划 ID |
| user_id | INTEGER | NOT NULL, UNIQUE, FK → users.id | 用户 ID (一对一) |
| target_job | VARCHAR(255) | | 目标岗位 |
| plan_type | VARCHAR(50) | DEFAULT '长期' | 计划类型 (长期/短期) |
| phases | JSON | | 学习阶段详情 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

---

## 10. daily_tasks — 每日任务表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 任务 ID |
| user_id | INTEGER | NOT NULL, FK → users.id | 用户 ID |
| phase_index | INTEGER | DEFAULT 0 | 阶段索引 |
| task_date | DATE | | 任务日期 |
| title | VARCHAR(255) | NOT NULL | 任务标题 |
| description | VARCHAR(1024) | | 任务描述 |
| duration | VARCHAR(50) | | 预计时长 |
| resources | JSON | | 学习资源 |
| status | VARCHAR(20) | DEFAULT 'pending' | 状态 (pending/completed) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引:** `idx_user_status` ON (user_id, status)

---

## 11. user_selected_job — 用户选定岗位表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | INTEGER | PK, FK → users.id | 用户 ID (一对一) |
| job_data | JSON | NOT NULL | 选定的岗位数据 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

---

## 12. agent_runs — 智能体运行记录表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | VARCHAR(36) | PK (UUID) | 运行 ID |
| agent_id | VARCHAR(50) | NOT NULL, INDEX | 智能体标识 |
| user_id | INTEGER | NOT NULL, INDEX | 用户 ID |
| status | ENUM | DEFAULT 'pending' | pending/running/success/failed/cancelled |
| input_hash | VARCHAR(64) | NOT NULL | 输入 SHA-256 哈希 (去重缓存) |
| input_data | JSON | NOT NULL | 输入数据 |
| output_data | JSON | | 输出数据 |
| error_message | TEXT | | 错误信息 |
| retry_count | INTEGER | DEFAULT 0 | 重试次数 |
| duration_ms | INTEGER | | 执行耗时 (毫秒) |
| started_at | DATETIME | | 开始时间 |
| completed_at | DATETIME | | 完成时间 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引:**
- `idx_agent_runs_agent_user` ON (agent_id, user_id)
- `idx_agent_runs_status` ON (status)

---

## 13. user_reports — 用户报告表

| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 报告 ID |
| user_id | INTEGER | NOT NULL, UNIQUE, FK → users.id | 用户 ID (一对一) |
| report_text | TEXT | NOT NULL | 报告文本内容 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引:** `idx_user_reports_user` ON (user_id)

---

## 14. favorites (约束补充)

唯一约束名: `uq_favorite_user_job` ON (user_id, job_id)

---

## ER 关系概览

```
users (1) ────< (N) favorites >──── (1) jobs
users (1) ──── (1) user_profiles
users (1) ────< (N) career_plans
users (1) ──── (1) learning_plans
users (1) ────< (N) daily_tasks
users (1) ──── (1) user_selected_job
users (1) ────< (N) matching_report
users (1) ──── (1) user_reports
users (1) ────< (N) agent_runs
jobs  (1) ──── (1) job_profiles
jobs  (1) ────< (N) promotion_transition
```

---

## 预置种子数据

### users
| username | email | password (明文) |
|----------|-------|----------------|
| testuser | test@example.com | password123 |

### jobs
| 岗位 | 公司 | 行业 | 城市 | 薪资 |
|------|------|------|------|------|
| Python后端开发工程师 | 字节跳动 | 互联网 | 北京 | 25k-50k |
| 前端开发工程师 | 阿里巴巴 | 互联网 | 杭州 | 20k-45k |
| 数据分析师 | 腾讯 | 互联网 | 深圳 | 18k-35k |
| 产品经理 | 美团 | 互联网 | 上海 | 22k-40k |

### promotion_transition
预置 6 条晋升路径，覆盖 Python 开发 (初级→中级→高级)、前端开发 (初级→中级→高级)、数据分析 (初级→高级)、产品 (助理→经理)。
