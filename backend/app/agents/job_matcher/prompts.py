# ---- Weight Determination Prompt ----

WEIGHT_PROMPT = """你是一个岗位匹配专家。请根据岗位信息，确定以下7个维度在匹配中的权重：

岗位信息：{job_info}

7个维度：
1. 专业技能 — 与岗位技术栈的匹配程度
2. 证书资质 — 行业认证和资格
3. 创新能力 — 创新能力匹配
4. 学习能力 — 学习新技术栈的能力
5. 抗压能力 — 工作强度适应性
6. 沟通能力 — 团队协作匹配
7. 实习/项目经验 — 实战经验匹配

输出JSON，7个权重值（0-1之间，总和为1）：
{{"专业技能": 0.35, "证书资质": 0.05, ...}}"""

# ---- Match Scoring Prompt ----

MATCH_PROMPT = """你是一个岗位匹配评估员。请评估用户画像与岗位需求的匹配程度。

用户画像：
{user_profile}

岗位需求：
{job_requirement}

维度权重：
{weights}

对每个维度进行0-100评分，并给出匹配差距分析。
输出JSON格式：
{{
  "scores": {{
    "专业技能": {{"score": 85, "gap": "需要补充XX技术"}},
    ...
  }},
  "total_score": 加权总分(0-100),
  "summary": "一句话总结匹配度",
  "recommendations": ["改进建议1", "改进建议2"]
}}"""

# ---- Merge Prompt ----

MERGE_PROMPT = """合并两个匹配评估结果：

MySQL详情匹配：{detail_result}
Neo4j画像匹配：{profile_result}

取各维度评分的平均值，综合生成最终匹配报告。输出JSON格式。"""

# ---- Batch Match Prompt (LLM scores all 10 positions at once) ----

BATCH_MATCH_PROMPT = """你是一个职业匹配专家。根据用户的七维能力画像，对以下 {job_count} 个岗位逐一进行匹配度打分。

# 用户画像（七维能力数据）
{user_profile_text}

# 七维评估标准
1. 专业技能 — 技术栈、框架、工具的掌握程度
2. 证书资质 — 行业认证和专业资格
3. 创新能力 — 技术改进、架构优化等创新潜力
4. 学习能力 — 新技术学习速度、知识迁移能力
5. 抗压能力 — 高强度工作下的表现和应对能力
6. 沟通能力 — 技术表达、跨部门协作、文档撰写
7. 实习/项目经验 — 实际工程经验和项目落地能力

# 岗位库（每个岗位包含七维要求）
{job_profiles_text}

# 打分规则
- 每个维度 0-100 分，加权计算总分
- 权重：专业技能 25%、实习/项目经验 20%、学习能力 15%、创新能力 12%、沟通能力 11%、证书资质 10%、抗压能力 7%
- gap 字段：当用户分数低于岗位期望时写"需提升至XX+（当前YY）"；超出时代写"超出岗位要求"
- summary：一句话总结匹配度（引用具体技能名和维度名）
- recommendations：2-3 条具体改进建议

# 输出格式
请严格输出一个 JSON 数组，不要包含 markdown 代码块标记：
[
  {{
    "job_id": 1,
    "job_title": "岗位名",
    "total_score": 85,
    "scores": {{
      "专业技能": 85, "证书资质": 70, "创新能力": 75,
      "学习能力": 80, "抗压能力": 90, "沟通能力": 85, "实习/项目经验": 80
    }},
    "summary": "综合85分，与XX岗位高度契合。Java、Spring Boot等技术栈匹配度高。",
    "recommendations": ["建议补充Redis集群经验", "建议考取OCP认证"]
  }},
  ...
]"""


def build_batch_match_prompt(user_profile: dict, jobs: list[dict]) -> str:
    """Build LLM prompt with user profile and all 10 positions' 7-dim requirements."""
    import json

    # Format user profile
    radar = user_profile.get("radar_data", [])
    dim_details = user_profile.get("dimension_details", {})

    dim_names = ["专业技能", "创新能力", "学习能力", "实习能力", "抗压能力", "沟通能力", "证书"]
    profile_lines = []
    for i, name in enumerate(dim_names):
        score = radar[i] if i < len(radar) else 0
        detail = dim_details.get(name, {})
        desc = detail.get("desc", "") if isinstance(detail, dict) else ""
        profile_lines.append(f"- {name}: {score}/100" + (f"（{desc}）" if desc else ""))
    user_profile_text = "\n".join(profile_lines)

    # Format job profiles (7-dim requirements)
    job_lines = []
    for j in jobs:
        pd = j.get("profile_data", {})
        dims = pd.get("dimensions", {})
        job_lines.append(f"\n## {j.get('job_title', '未知')} (ID: {j.get('id', '?')})")
        job_lines.append(f"公司: {j.get('company', '')} | 城市: {j.get('city', '')} | 薪资: {j.get('salary_range', '')}")
        for name in ["专业技能", "证书要求", "创新能力", "学习能力", "抗压能力", "沟通能力", "实习能力"]:
            items = dims.get(name, [])
            if items:
                job_lines.append(f"- {name}: {' | '.join(items[:3])}")

    job_profiles_text = "\n".join(job_lines)

    return BATCH_MATCH_PROMPT.format(
        job_count=len(jobs),
        user_profile_text=user_profile_text,
        job_profiles_text=job_profiles_text,
    )
