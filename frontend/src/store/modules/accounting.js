import api from '@/services/api'

const state = {
  chartOfAccounts: [],
  chartOfAccount: null,
  journalEntries: [],
  journalEntry: null,
  libroMayor: null,
  libroVentas: null,
  libroCompras: null,
  declaracionIVA: null,
  retenciones: null,
  ingresos: null,
  patrimonio: null,
  estadoResultados: null,
  balanceGeneral: null,
  loading: false,
  error: null
}

const getters = {
  getChartOfAccounts: state => state.chartOfAccounts,
  getChartOfAccount: state => state.chartOfAccount,
  getJournalEntries: state => state.journalEntries,
  getJournalEntry: state => state.journalEntry,
  getLibroMayor: state => state.libroMayor,
  getLibroVentas: state => state.libroVentas,
  getLibroCompras: state => state.libroCompras,
  getDeclaracionIVA: state => state.declaracionIVA,
  getRetenciones: state => state.retenciones,
  getIngresos: state => state.ingresos,
  getPatrimonio: state => state.patrimonio,
  getEstadoResultados: state => state.estadoResultados,
  getBalanceGeneral: state => state.balanceGeneral,
  isLoading: state => state.loading,
  hasError: state => state.error !== null
}

const actions = {
  async fetchChartOfAccounts({ commit }, { companyId, skip = 0, limit = 100 } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/chart-of-accounts/`,
        {
          params: { company_id: companyId, skip, limit }
        }
      )
      commit('setChartOfAccounts', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el plan de cuentas')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchChartOfAccountById({ commit }, { accountId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/chart-of-accounts/${accountId}`,
        { params: { company_id: companyId } }
      )
      commit('setChartOfAccount', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener la cuenta contable')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async createChartOfAccount({ commit }, { accountData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/chart-of-accounts/`,
        { ...accountData, company_id: companyId }
      )
      commit('setChartOfAccount', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear la cuenta contable')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async updateChartOfAccount({ commit }, { accountId, accountData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.put(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/chart-of-accounts/${accountId}`,
        { ...accountData, company_id: companyId }
      )
      commit('setChartOfAccount', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al actualizar la cuenta contable')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async deleteChartOfAccount({ commit }, { accountId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      await api.delete(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/chart-of-accounts/${accountId}`,
        { params: { company_id: companyId } }
      )
      commit('setChartOfAccount', null)
      return { status: 'success' }
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al eliminar la cuenta contable')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async deleteJournalEntry({ commit }, { entryId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      await api.delete(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/journal-entries/${entryId}`,
        { params: { company_id: companyId } }
      )
      commit('setJournalEntry', null)
      return { status: 'success' }
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al eliminar el asiento contable')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchJournalEntries({ commit }, { companyId, skip = 0, limit = 100 } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/journal-entries/`,
        {
          params: { company_id: companyId, skip, limit }
        }
      )
      commit('setJournalEntries', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener los asientos contables')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchJournalEntryById({ commit }, { entryId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/journal-entries/${entryId}`,
        { params: { company_id: companyId } }
      )
      commit('setJournalEntry', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el asiento contable')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async createJournalEntry({ commit }, { entryData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/journal-entries/`,
        { ...entryData, company_id: companyId }
      )
      commit('setJournalEntry', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear el asiento contable')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async createJournalEntryWithLines({ commit }, { entryData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/journal-entries/with-lines/`,
        { ...entryData, company_id: companyId }
      )
      commit('setJournalEntry', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear el asiento contable con líneas')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async postJournalEntry({ commit }, { entryId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/journal-entries/${entryId}/post/`,
        {},
        { params: { company_id: companyId } }
      )
      commit('setJournalEntry', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al publicar el asiento contable')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchLibroMayor({ commit }, { companyId, dateFrom, dateTo, accountCode }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/libro-mayor/`,
        { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo, account_code: accountCode } }
      )
      commit('setLibroMayor', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el Libro Mayor')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchLibroVentas({ commit }, { companyId, dateFrom, dateTo }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/libro-ventas/`,
        { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }
      )
      commit('setLibroVentas', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el Libro de Ventas')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchLibroCompras({ commit }, { companyId, dateFrom, dateTo }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/libro-compras/`,
        { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }
      )
      commit('setLibroCompras', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el Libro de Compras')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchDeclaracionIVA({ commit }, { companyId, dateFrom, dateTo }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/declaracion-iva/`,
        { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }
      )
      commit('setDeclaracionIVA', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener la Declaración de IVA')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchRetenciones({ commit }, { companyId, dateFrom, dateTo }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/reporte-retenciones/`,
        { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }
      )
      commit('setRetenciones', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el Reporte de Retenciones')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchIngresos({ commit }, { companyId, dateFrom, dateTo }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/reporte-ingresos/`,
        { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }
      )
      commit('setIngresos', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el Reporte de Ingresos')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchPatrimonio({ commit }, { companyId, dateFrom, dateTo }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/reporte-patrimonio/`,
        { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }
      )
      commit('setPatrimonio', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el Reporte de Patrimonio')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchEstadoResultados({ commit }, { companyId, dateFrom, dateTo }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/estado-resultados/`,
        { params: { company_id: companyId, date_from: dateFrom, date_to: dateTo } }
      )
      commit('setEstadoResultados', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el Estado de Resultados')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchBalanceGeneral({ commit }, { companyId, cutDate }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(
        `${process.env.VUE_APP_API_URL}/api/v1/accounting/balance-general/`,
        { params: { company_id: companyId, cut_date: cutDate } }
      )
      commit('setBalanceGeneral', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el Balance General')
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
  setChartOfAccounts(state, payload) {
    state.chartOfAccounts = payload
  },
  setChartOfAccount(state, payload) {
    state.chartOfAccount = payload
  },
  setJournalEntries(state, payload) {
    state.journalEntries = payload
  },
  setJournalEntry(state, payload) {
    state.journalEntry = payload
  },
  setLibroMayor(state, payload) {
    state.libroMayor = payload
  },
  setLibroVentas(state, payload) {
    state.libroVentas = payload
  },
  setLibroCompras(state, payload) {
    state.libroCompras = payload
  },
  setDeclaracionIVA(state, payload) {
    state.declaracionIVA = payload
  },
  setRetenciones(state, payload) {
    state.retenciones = payload
  },
  setIngresos(state, payload) {
    state.ingresos = payload
  },
  setPatrimonio(state, payload) {
    state.patrimonio = payload
  },
  setEstadoResultados(state, payload) {
    state.estadoResultados = payload
  },
  setBalanceGeneral(state, payload) {
    state.balanceGeneral = payload
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}