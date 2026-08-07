import api from './client'

export const diagnosisApi = {
  generate(data) {
    return api.post('/diagnosis/generate', data, { timeout: 120000 })
  },
  getReport() {
    return api.get('/diagnosis/report')
  },
}
