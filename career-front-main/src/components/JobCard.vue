<template>
  <div class="job-card">
    <!-- 岗位标题 -->
    <h3 class="job-title">{{ job.jobTitle }}</h3>

    <!-- 核心短板技能 Top2 -->
    <div class="weak-section">
      <span class="weak-label">核心短板</span>
      <div class="weak-tags">
        <el-tag
          v-for="w in job.topWeaknesses"
          :key="w"
          size="small"
          type="danger"
          effect="plain"
          class="weak-tag"
        >{{ w }}</el-tag>
      </div>
    </div>

    <!-- 能力重合度 -->
    <div class="match-section">
      <div class="match-rate" :style="{ color: getMatchColor(job.overlapRate) }">
        {{ job.overlapRate }}%
      </div>
      <div class="match-label">能力重合度</div>
    </div>

    <!-- 行业标签 -->
    <div v-if="job.tags && job.tags.length" class="industry-tags">
      <el-tag
        v-for="t in job.tags"
        :key="t"
        size="mini"
        effect="plain"
        class="industry-tag"
      >{{ t }}</el-tag>
    </div>

    <!-- 操作按钮 -->
    <el-button class="analysis-btn" size="small">
      <el-icon class="btn-icon"><DataLine /></el-icon>
      查看能力模型
    </el-button>
  </div>
</template>

<script setup>
const props = defineProps({
  job: {
    type: Object,
    required: true,
    default: () => ({
      jobTitle: '未知岗位',
      overlapRate: 0,
      studyWeeks: 0,
      topWeaknesses: [],
      tags: []
    })
  }
})

// 辅助函数：根据能力重合度返回颜色
const getMatchColor = (rate) => {
  if (rate >= 90) return '#67C23A'
  if (rate >= 75) return '#E6A23C'
  return '#F56C6C'
}
</script>

<style scoped>
.job-card {
  position: relative;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px 18px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: auto;
  min-height: 150px;
}

.job-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-color: #409EFF;
}

.job-title {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.weak-section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.weak-label {
  font-size: 12px;
  color: #f56c6c;
  font-weight: 600;
  flex-shrink: 0;
}

.weak-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.weak-tag {
  border-radius: 4px;
}

.match-section {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.match-rate {
  font-size: 24px;
  font-weight: 800;
  line-height: 1;
}

.match-label {
  font-size: 11px;
  color: #909399;
}

.industry-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.industry-tag {
  font-size: 11px;
  border-radius: 4px;
}

.analysis-btn {
  width: 100%;
  margin-top: 8px;
  height: 32px;
  border-radius: 16px !important;
  border: 1px solid rgba(64, 158, 255, 0.3) !important;
  background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%) !important;
  color: #409eff !important;
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;

  .btn-icon {
    font-size: 14px;
    transition: transform 0.3s;
  }

  &:hover {
    background: linear-gradient(135deg, #e1f0ff 0%, #f0f7ff 100%) !important;
    border-color: #409eff !important;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2) !important;
    transform: translateY(-1px);

    .btn-icon {
      transform: scale(1.2) rotate(5deg);
    }
  }

  &:active {
    transform: translateY(1px);
    box-shadow: 0 2px 6px rgba(64, 158, 255, 0.1) !important;
  }
}
</style>