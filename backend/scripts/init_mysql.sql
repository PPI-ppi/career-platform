-- Career Platform - MySQL Schema

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    city VARCHAR(100),
    salary_range VARCHAR(100),
    company_scale VARCHAR(50),
    job_description TEXT,
    requirements TEXT,
    company_description TEXT,
    job_details TEXT,
    publish_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    profile_data JSON NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    match_score DECIMAL(5,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_favorite_user_job (user_id, job_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS career_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    target_position VARCHAR(255),
    target_company VARCHAR(255),
    timeline_months INT,
    status VARCHAR(50) DEFAULT 'active',
    plan_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS job_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    profile_data JSON,
    summary VARCHAR(1024),
    core_skills JSON,
    career_path JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS promotion_transition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT,
    current_role VARCHAR(255) NOT NULL,
    next_role VARCHAR(255) NOT NULL,
    required_skills JSON,
    years_exp INT,
    transition_type VARCHAR(50) DEFAULT 'promotion',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS matching_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_name VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    city VARCHAR(100),
    match_score DECIMAL(5,2),
    report_data JSON,
    publish_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS learning_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    target_job VARCHAR(255),
    plan_type VARCHAR(50) DEFAULT '长期',
    phases JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS daily_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    phase_index INT DEFAULT 0,
    task_date DATE,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1024),
    duration VARCHAR(50),
    resources JSON,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_selected_job (
    user_id INT NOT NULL PRIMARY KEY,
    job_data JSON NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS agent_runs (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    status ENUM('pending','running','success','failed','cancelled') DEFAULT 'pending',
    input_hash VARCHAR(64) NOT NULL,
    input_data JSON NOT NULL,
    output_data JSON,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    duration_ms INT,
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agent_runs_agent_user (agent_id, user_id),
    INDEX idx_agent_runs_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    report_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_reports_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed: test user (password = "password123")
INSERT IGNORE INTO users (id, username, email, password_hash) VALUES
(1, 'testuser', 'test@example.com', '$2b$12$LJ3m4ys3uz0Gv0gMOsYmNe8JI8k/.dRgRv0cOx5vGJy0fkKzJKHpy');

-- Seed: sample jobs
INSERT IGNORE INTO jobs (id, job_title, company, industry, city, salary_range, job_description, requirements, company_scale, publish_date) VALUES
(1, 'Python后端开发工程师', '字节跳动', '互联网', '北京', '25k-50k', '负责后端服务的设计与开发，构建高可用、高并发的分布式系统。', '熟悉Python、Django/FastAPI、MySQL、Redis、分布式系统。3年以上后端开发经验。', '10000人以上', CURDATE()),
(2, '前端开发工程师', '阿里巴巴', '互联网', '杭州', '20k-45k', '负责Web前端开发，与设计师和后端紧密协作，实现优秀的用户体验。', '熟悉Vue.js/React、TypeScript、CSS3、前端工程化。', '10000人以上', CURDATE()),
(3, '数据分析师', '腾讯', '互联网', '深圳', '18k-35k', '负责数据收集、清洗、分析与可视化，为业务决策提供数据支持。', '熟悉Python/SQL、统计分析、机器学习基础、数据可视化工具。', '10000人以上', CURDATE()),
(4, '产品经理', '美团', '互联网', '上海', '22k-40k', '负责产品规划、需求分析与项目管理，推动产品从概念到上线。', '熟悉产品设计方法论、数据分析、项目管理、优秀的沟通能力。', '10000人以上', CURDATE());
