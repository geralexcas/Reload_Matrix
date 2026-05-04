import api from '@/services/api'

const state = {
  purchases: [],
  purchase: null,
  statistics: null,
  loading: false,
  error: null
}

const getters = {
  getPurchases: state => state.purchases,
  getPurchase: state => state.purchase,
  getStatistics: state => state.statistics,
  isLoading: state => state.loading,
  hasError: state => state.error !== null
}

const actions = {
  async fetchPurchases({ commit }, { companyId, skip = 0, limit = 100, status = null, partnerId = null } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get('/api/v1/purchases/', {
        params: { company_id: companyId, skip, limit, status, partner_id: partnerId }
      })
      commit('setPurchases', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener las compras')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchPurchaseById({ commit }, { purchaseId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(`/api/v1/purchases/${purchaseId}`, {
        params: { company_id: companyId }
      })
      commit('setPurchase', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener la compra')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async createPurchase({ commit }, { purchaseData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post('/api/v1/purchases/', purchaseData, {
        params: { company_id: companyId }
      })
      commit('setPurchase', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear la compra')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async extractFromPdf({ commit }, { formData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post('/api/v1/purchases/extract-from-pdf', formData, {
        params: { company_id: companyId },
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al procesar el PDF')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async updatePurchase({ commit }, { purchaseId, purchaseData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.put(`/api/v1/purchases/${purchaseId}`, purchaseData, {
        params: { company_id: companyId }
      })
      commit('setPurchase', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al actualizar la compra')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async deletePurchase({ commit }, { purchaseId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      await api.delete(`/api/v1/purchases/${purchaseId}`, {
        params: { company_id: companyId }
      })
      commit('setPurchase', null)
      return { status: 'success' }
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al eliminar la compra')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async cancelPurchase({ commit }, { purchaseId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(`/api/v1/purchases/${purchaseId}/cancel`, null, {
        params: { company_id: companyId }
      })
      commit('setPurchase', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al anular la compra')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async registerPayment({ commit }, { purchaseId, paymentData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(`/api/v1/purchases/${purchaseId}/pay`, paymentData, {
        params: { company_id: companyId }
      })
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al registrar el pago')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchPurchaseBalance({ commit }, { purchaseId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(`/api/v1/purchases/${purchaseId}/balance`, {
        params: { company_id: companyId }
      })
      return res.data
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el saldo')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchStatistics({ commit }, { companyId, startDate = null, endDate = null } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get('/api/v1/purchases/statistics', {
        params: { company_id: companyId, start_date: startDate, end_date: endDate }
      })
      commit('setStatistics', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener estadísticas')
      throw err
    } finally {
      commit('setLoading', false)
    }
  }
}

const mutations = {
  setLoading(state, payload) {
    state.loading = payload
  },
  clearError(state) {
    state.error = null
  },
  setError(state, payload) {
    state.error = payload
  },
  setPurchases(state, payload) {
    state.purchases = payload
  },
  setPurchase(state, payload) {
    state.purchase = payload
  },
  setStatistics(state, payload) {
    state.statistics = payload
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}