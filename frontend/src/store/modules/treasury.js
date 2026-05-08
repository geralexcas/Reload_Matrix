import api from '@/services/api'

const state = {
  bankAccounts: [],
  cashAccounts: [],
  transactions: [],
  treasurySummary: null,
  cashFlow: null,
  checks: [],
  reconciliations: [],
  currentReconciliation: null,
  loading: false,
  error: null
}

const getters = {
  getBankAccounts: state => state.bankAccounts,
  getCashAccounts: state => state.cashAccounts,
  getTransactions: state => state.transactions,
  getTreasurySummary: state => state.treasurySummary,
  getCashFlow: state => state.cashFlow,
  getChecks: state => state.checks,
  getReconciliations: state => state.reconciliations,
  getCurrentReconciliation: state => state.currentReconciliation,
  isLoading: state => state.loading,
  hasError: state => state.error !== null
}

const actions = {
  async fetchBankAccounts({ commit }, { skip = 0, limit = 100 } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `/api/v1/treasury/bank-accounts/`,
        { params: { skip, limit } }
      )
      commit('setBankAccounts', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener cuentas bancarias')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async createBankAccount({ commit }, accountData) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `/api/v1/treasury/bank-accounts/`,
        accountData
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear cuenta bancaria')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async updateBankAccount({ commit }, { accountId, data }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.put(
        `/api/v1/treasury/bank-accounts/${accountId}`,
        data
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al actualizar cuenta bancaria')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async deleteBankAccount({ commit }, accountId) {
    commit('setLoading', true)
    commit('clearError')
    try {
      await api.delete(
        `/api/v1/treasury/bank-accounts/${accountId}`
      )
      return { status: 'success' }
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al desactivar cuenta bancaria')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async fetchCashAccounts({ commit }, { skip = 0, limit = 100 } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `/api/v1/treasury/cash-accounts/`,
        { params: { skip, limit } }
      )
      commit('setCashAccounts', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener cuentas de caja')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async createCashAccount({ commit }, accountData) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `/api/v1/treasury/cash-accounts/`,
        accountData
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear cuenta de caja')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async updateCashAccount({ commit }, { accountId, data }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.put(
        `/api/v1/treasury/cash-accounts/${accountId}`,
        data
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al actualizar cuenta de caja')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async deleteCashAccount({ commit }, accountId) {
    commit('setLoading', true)
    commit('clearError')
    try {
      await api.delete(
        `/api/v1/treasury/cash-accounts/${accountId}`
      )
      return { status: 'success' }
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al desactivar cuenta de caja')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async deposit({ commit }, data) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `/api/v1/treasury/deposit/`,
        data
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al realizar deposito')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async withdraw({ commit }, data) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `/api/v1/treasury/withdraw/`,
        data
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al realizar retiro')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async transfer({ commit }, data) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `/api/v1/treasury/transfer/`,
        data
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al realizar transferencia')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async fetchTransactions({ commit }, { accountType, transactionType, dateFrom, dateTo, skip = 0, limit = 100 } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `/api/v1/treasury/transactions/`,
        { params: { account_type: accountType, transaction_type: transactionType, date_from: dateFrom, date_to: dateTo, skip, limit } }
      )
      commit('setTransactions', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener transacciones')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async fetchTreasurySummary({ commit }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `/api/v1/treasury/summary/`
      )
      commit('setTreasurySummary', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener resumen de tesoreria')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async fetchCashFlow({ commit }, { dateFrom, dateTo } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `/api/v1/treasury/cash-flow/`,
        { params: { date_from: dateFrom, date_to: dateTo } }
      )
      commit('setCashFlow', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener flujo de caja')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async fetchChecks({ commit }, { bankAccountId, status, skip = 0, limit = 100 } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `/api/v1/treasury/checks/`,
        { params: { bank_account_id: bankAccountId, status, skip, limit } }
      )
      commit('setChecks', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener cheques')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async issueCheck({ commit }, data) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `/api/v1/treasury/checks/`,
        data
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al emitir cheque')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async updateCheckStatus({ commit }, { checkId, status }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.put(
        `/api/v1/treasury/checks/${checkId}/status/`,
        { status }
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al actualizar estado del cheque')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async createReconciliation({ commit }, data) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `/api/v1/treasury/reconciliations/`,
        data
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear conciliacion')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async fetchReconciliations({ commit }, { bankAccountId, skip = 0, limit = 100 } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `/api/v1/treasury/reconciliations/`,
        { params: { bank_account_id: bankAccountId, skip, limit } }
      )
      commit('setReconciliations', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener conciliaciones')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async fetchReconciliationById({ commit }, reconId) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `/api/v1/treasury/reconciliations/${reconId}/`
      )
      commit('setCurrentReconciliation', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener conciliacion')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async matchTransaction({ commit }, { reconId, data }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `/api/v1/treasury/reconciliations/${reconId}/match/`,
        data
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al conciliar transaccion')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },

  async completeReconciliation({ commit }, reconId) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `/api/v1/treasury/reconciliations/${reconId}/complete/`
      )
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al completar conciliacion')
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
  setBankAccounts(state, payload) {
    state.bankAccounts = payload
  },
  setCashAccounts(state, payload) {
    state.cashAccounts = payload
  },
  setTransactions(state, payload) {
    state.transactions = payload
  },
  setTreasurySummary(state, payload) {
    state.treasurySummary = payload
  },
  setCashFlow(state, payload) {
    state.cashFlow = payload
  },
  setChecks(state, payload) {
    state.checks = payload
  },
  setReconciliations(state, payload) {
    state.reconciliations = payload
  },
  setCurrentReconciliation(state, payload) {
    state.currentReconciliation = payload
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
