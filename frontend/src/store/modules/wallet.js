import api from '@/services/api'

const state = {
  wallets: [],
  wallet: null,
  transactions: [],
  loading: false,
  error: null
}

const getters = {
  getWallets: state => state.wallets,
  getWallet: state => state.wallet,
  getTransactions: state => state.transactions,
  isLoading: state => state.loading,
  hasError: state => state.error !== null
}

const actions = {
  async fetchWallets({ commit }, { companyId, skip = 0, limit = 100 } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get('/api/v1/wallet/', {
        params: { company_id: companyId, skip, limit }
      })
      commit('setWallets', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener monederos')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchWalletById({ commit }, { walletId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(`/api/v1/wallet/${walletId}`, {
        params: { company_id: companyId }
      })
      commit('setWallet', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el monedero')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async createWallet({ commit }, { walletData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post('/api/v1/wallet/', walletData, {
        params: { company_id: companyId }
      })
      commit('setWallet', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear el monedero')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async deposit({ commit }, { walletId, amount, description, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(`/api/v1/wallet/${walletId}/deposit`, null, {
        params: { amount, description, company_id: companyId }
      })
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al depositar')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async withdraw({ commit }, { walletId, amount, description, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(`/api/v1/wallet/${walletId}/withdraw`, null, {
        params: { amount, description, company_id: companyId }
      })
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al retirar')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchTransactions({ commit }, { walletId, companyId, skip = 0, limit = 100 }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(`/api/v1/wallet/${walletId}/transactions`, {
        params: { company_id: companyId, skip, limit }
      })
      commit('setTransactions', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener transacciones')
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
  setWallets(state, payload) {
    state.wallets = payload
  },
  setWallet(state, payload) {
    state.wallet = payload
  },
  setTransactions(state, payload) {
    state.transactions = payload
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
