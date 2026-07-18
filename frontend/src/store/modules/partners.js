import api from '@/services/api'

const state = {
  partners: [],
  partner: null,
  loading: false,
  error: null
}

const getters = {
  getPartners: state => state.partners,
  getPartner: state => state.partner,
  isLoading: state => state.loading,
  hasError: state => state.error !== null
}

const actions = {
  async fetchPartners({ commit }, { companyId, skip = 0, limit = 1000 } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get('/api/v1/partners/', {
        params: { company_id: companyId, skip, limit }
      })
      commit('setPartners', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener los socios')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchPartnerById({ commit }, { partnerId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(`/api/v1/partners/${partnerId}`, {
        params: { company_id: companyId }
      })
      commit('setPartner', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el socio')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async createPartner({ commit }, { partnerData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post('/api/v1/partners/', partnerData, {
        params: { company_id: companyId }
      })
      commit('setPartner', res.data)
      // ponytail: append to list so callers reading state.partners see the new entry
      // without needing a full fetchPartners roundtrip.
      commit('addPartnerToList', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear el socio')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async updatePartner({ commit }, { partnerId, partnerData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.put(`/api/v1/partners/${partnerId}`, partnerData, {
        params: { company_id: companyId }
      })
      commit('setPartner', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al actualizar el socio')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async deletePartner({ commit }, { partnerId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      await api.delete(`/api/v1/partners/${partnerId}`, {
        params: { company_id: companyId }
      })
      commit('setPartner', null)
      return { status: 'success' }
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al eliminar el socio')
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
  setPartners(state, payload) {
    state.partners = payload
  },
  setPartner(state, payload) {
    state.partner = payload
  },
  addPartnerToList(state, payload) {
    if (payload && Array.isArray(state.partners)) {
      state.partners.push(payload)
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
