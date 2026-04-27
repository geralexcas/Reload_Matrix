import api from '@/services/api'

const state = {
  company: null,
  companies: [],
  loading: false,
  error: null
}

const getters = {
  getCompany: state => state.company,
  getCompanies: state => state.companies,
  isLoading: state => state.loading,
  hasCompany: state => !!state.company,
  selectedCompanyId: (state) => {
    if (state.company && state.company.id) return state.company.id;
    const savedId = sessionStorage.getItem('selectedCompanyId');
    return savedId ? parseInt(savedId) : null;
  }
}

const actions = {
  async createCompany({ commit }, companyData) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post('/api/v1/companies/', companyData)
      commit('setCompany', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear la empresa')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchCompanies({ commit }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get('/api/v1/companies/')
      commit('setCompanies', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener las empresas')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchCompany({ commit }, companyId) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(`/api/v1/companies/${companyId}`)
      commit('setCompany', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener la empresa')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async updateCompany({ commit }, { companyId, companyData }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.put(`/api/v1/companies/${companyId}`, companyData)
      commit('setCompany', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al actualizar la empresa')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async uploadLogo({ commit }, { companyId, file }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post(`/api/v1/companies/${companyId}/logo`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      // Refetch company to get updated logo_url
      const compRes = await api.get(`/api/v1/companies/${companyId}`)
      commit('setCompany', compRes.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al subir el logo')
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
  setCompany(state, payload) {
    state.company = payload
  },
  setCompanies(state, payload) {
    state.companies = payload
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
