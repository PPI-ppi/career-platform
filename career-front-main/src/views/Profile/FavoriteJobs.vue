<template>
  <div class="favorite-jobs">
    <div v-if="favoriteList.length === 0" class="empty-state">
      <el-empty description="暂无收藏岗位，快去探索吧！">
        <el-button type="primary" @click="goToExplore">去探索岗位</el-button>
      </el-empty>
    </div>

    <div v-else class="job-list">
      <div
        v-for="job in favoriteList"
        :key="job.id"
        :class="['job-card', { 'is-target': isLearningTarget(job) }]"
        @click="goToDetail(job.id)"
      >
        <div class="target-badge" v-if="isLearningTarget(job)">
          <el-icon><Aim /></el-icon>
          当前学习目标
        </div>

        <div class="company-logo">
          {{ job.company ? job.company.charAt(0) : '岗' }}
        </div>

        <div class="job-info">
          <div class="info-top">
            <span class="job-title">{{ job.title }}</span>
            <span class="job-salary">{{ job.salary }}</span>
          </div>

          <div class="job-company-row">
            <span class="company-name">{{ job.company }}</span>
            <span class="divider">|</span>
            <span class="job-city">{{ job.city }}</span>
            <span class="divider">|</span>
            <span class="job-experience">{{ job.experience }}</span>
          </div>

          <div class="job-tags">
            <el-tag
              v-for="tag in job.tags"
              :key="tag"
              size="small"
              effect="plain"
              class="custom-tag"
            >
              {{ tag }}
            </el-tag>
          </div>

          <div class="job-actions">
            <el-button
              :type="isLearningTarget(job) ? 'primary' : 'default'"
              :icon="isLearningTarget(job) ? Lock : Aim"
              size="small"
              :class="['target-btn', { 'is-target': isLearningTarget(job) }]"
              @click.stop="toggleLearningTarget(job)"
            >
              {{ isLearningTarget(job) ? '已设为学习目标' : '设为学习目标' }}
            </el-button>
            <el-button
              size="small"
              class="remove-btn"
              icon="Delete"
              @click.stop="removeFavorite(job.id)"
            >
              移除收藏
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Aim, Lock } from '@element-plus/icons-vue'
import { favoritesApi } from '@/api/favorites'
import { matchingApi } from '@/api/matching'

const router = useRouter()
const favoriteList = ref([])
const lockedJobKey = ref('')

const loadFavorites = async () => {
  try {
    const { data } = await favoritesApi.list()
    favoriteList.value = (data.favorites || []).map((f) => ({
      id: f.job_id,
      job_id: f.job_id,
      title: f.job_title,
      job_title: f.job_title,
      company: f.company,
      salary: f.salary_range || '面议',
      city: f.city || '--',
      experience: f.experience || '--',
      industry: f.industry || '',
      tags: f.industry ? f.industry.split(',').slice(0, 2) : [],
    }))
  } catch {
    favoriteList.value = []
  }
}

const getJobKey = (job = {}) => {
  if (!job || !job.id && !job.job_id) return ''
  return String(job.id ?? job.job_id)
}

const isLearningTarget = (job) => !!lockedJobKey.value && lockedJobKey.value === getJobKey(job)

// 恢复当前锁定（学习目标）状态
const loadLockedJob = async () => {
  try {
    const { data } = await matchingApi.getSelectedJob()
    if (data.success && data.data) {
      lockedJobKey.value = getJobKey(data.data)
    }
  } catch { /* ignore */ }
}

const toggleLearningTarget = async (job) => {
  const key = getJobKey(job)
  if (!key || !job) return
  try {
    if (isLearningTarget(job)) {
      await matchingApi.clearSelectedJob()
      lockedJobKey.value = ''
      ElMessage.info(`已取消「${job.title}」学习目标`)
    } else {
      await matchingApi.selectJob({
        job_id: job.job_id || job.id,
        job_title: job.title || job.job_title,
        company: job.company || '',
        industry: job.industry || '',
        city: job.city || '',
        salary_range: job.salary || '',
      })
      lockedJobKey.value = key
      ElMessage.success(`已设为学习目标「${job.title}」`)
    }
  } catch (err) {
    console.error('[FavoriteJobs] toggleLearningTarget failed:', err)
    ElMessage.error(isLearningTarget(job) ? '取消学习目标失败，请重试' : '设置学习目标失败，请重试')
  }
}

onMounted(() => {
  loadFavorites()
  loadLockedJob()
})

const goToExplore = () => {
  router.push('/jobs')
}

const goToDetail = (id) => {
  router.push({ name: 'JobDetail', params: { id } })
}

const removeFavorite = async (jobId) => {
  try {
    await favoritesApi.remove(jobId)
    favoriteList.value = favoriteList.value.filter((j) => j.id !== jobId)
    if (lockedJobKey.value === String(jobId)) {
      lockedJobKey.value = ''
    }
  } catch {
    // ignore
  }
}
</script>

<style scoped lang="scss">
.favorite-jobs {
  height: 100%;
  padding: 10px;
  overflow-y: auto;

  &::-webkit-scrollbar { width: 5px; }
  &::-webkit-scrollbar-track { background: transparent; }
  &::-webkit-scrollbar-thumb { background: rgba(0, 0, 0, 0.1); border-radius: 10px; }
}

.job-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.job-explorer {
  background: transparent;
  min-height: 100vh;
}

.job-card {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(16px) saturate(1.1);
  -webkit-backdrop-filter: blur(16px) saturate(1.1);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;

  &.is-target {
    background: rgba(80, 152, 249, 0.08);
    border-color: rgba(80, 152, 249, 0.35);
    box-shadow: 0 8px 24px rgba(80, 152, 249, 0.15);
  }

  .target-badge {
    position: absolute;
    top: 0;
    right: 0;
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    background: linear-gradient(135deg, #a1c4fd 0%, #5098f9 100%);
    color: #fff;
    font-size: 12px;
    font-weight: 600;
    border-radius: 0 16px 0 12px;
    .el-icon { font-size: 13px; }
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
    background: rgba(255, 255, 255, 0.5);
  }

  /* 左侧 Logo 占位：同步图三样式 */
  .company-logo {
    flex-shrink: 0;
    width: 54px;
    height: 54px;
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    color: #3b82f6;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: bold;
    border: 1px solid #e0e7ff;
  }

  .job-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;

    .info-top {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .job-title {
        font-size: 17px;
        font-weight: 700;
        color: #1e293b;
      }

      .job-salary {
        font-size: 16px;
        font-weight: 700;
        color: #ef4444; /* 醒目的红色薪资 */
      }
    }

    .job-company-row {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: #64748b;

      .divider {
        color: #e2e8f0;
      }
      .company-name {
        color: #475569;
        font-weight: 500;
      }
    }

    .job-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;

      .custom-tag {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        color: #64748b !important;
        border-radius: 6px;
        font-weight: 400;
      }
    }

    .job-actions {
      display: flex;
      gap: 8px;
      margin-top: 12px;

      .target-btn {
        flex-shrink: 0;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;

        &.is-target {
          box-shadow: 0 4px 12px rgba(80, 152, 249, 0.22);
        }
      }

      .remove-btn {
        flex-shrink: 0;
        border-radius: 8px;
        font-weight: 500;
        color: #94a3b8;
        transition: all 0.2s;

        &:hover {
          color: #f56c6c;
        }
      }
    }
  }
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}
</style>