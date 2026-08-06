import client from './client'

export const trainingApi = {
  preview(params = {}) {
    return client.get('/training/tasks/preview', { params })
  }
}