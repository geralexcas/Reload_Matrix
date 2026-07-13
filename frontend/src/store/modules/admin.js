import api from '@/services/api'

const state = {
  tenants: [],
  currentTenant: null,
  users: [],
  loading: false,
  error: null
}

const getters = {
  getTenants: state => state.tenants,
  getCurrentTenant: state => state.currentTenant,
  getUsers: state => state.users,
  isLoading: state => state.loading,
  error: state => state.error
}

const actions = {
  async fetchTenants({ commit }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get('/api/v1/companies/')
      commit('setTenants', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener empresas')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async fetchTenant({ commit }, tenantId) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(`/api/v1/companies/${tenantId}`)
      commit('setCurrentTenant', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener empresa')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async createTenant({ commit }, tenantData) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post('/api/v1/companies/', tenantData)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear empresa')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async updateTenant({ commit }, { tenantId, tenantData }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.put(`/api/v1/companies/${tenantId}`, tenantData)
      commit('setCurrentTenant', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al actualizar empresa')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async toggleTenantActive({ commit }, tenantId) {
    commit('clearError')
    try {
      const res = await api.patch(`/api/v1/companies/${tenantId}/toggle-active`)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al cambiar estado')
      throw err
    }
  },

  async fetchUsers({ commit }, companyId) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const params = {}
      if (companyId) params.company_id = companyId
      const res = await api.get('/api/v1/admin/users/', { params })
      commit('setUsers', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener usuarios')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async createUser({ commit }, userData) {
    commit('clearError')
    try {
      const res = await api.post('/api/v1/admin/users/', userData)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear usuario')
      throw err
    }
  },

  async toggleUserActive({ commit }, userId) {
    commit('clearError')
    try {
      const res = await api.patch(`/api/v1/admin/users/${userId}/toggle-active`)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al cambiar estado')
      throw err
    }
  },

  async resetUserPassword({ commit }, { userId, newPassword }) {
    commit('clearError')
    try {
      const res = await api.post(`/api/v1/admin/users/${userId}/reset-password/`, {
        new_password: newPassword
      })
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al resetear contraseña')
      throw err
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
  setTenants(state, payload) {
    state.tenants = payload
  },
  setCurrentTenant(state, payload) {
    state.currentTenant = payload
  },
  setUsers(state, payload) {
    state.users = payload
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}