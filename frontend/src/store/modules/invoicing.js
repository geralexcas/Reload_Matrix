import api from '@/services/api'

const state = {
  invoices: [],
  currentInvoice: null,
  notes: [],
  loading: false,
  error: null
}

const getters = {
  allInvoices: state => state.invoices,
  currentInvoice: state => state.currentInvoice,
  notes: state => state.notes,
  loading: state => state.loading
}

const actions = {
  async fetchInvoices({ commit }, { company_id, skip = 0, limit = 100 }) {
    commit('set_loading', true)
    try {
      const res = await api.get('/api/v1/invoicing/', {
        params: { company_id, skip, limit }
      })
      commit('set_invoices', res.data)
    } catch (err) {
      commit('set_error', err.message)
      throw err
    } finally {
      commit('set_loading', false)
    }
  },
  async createInvoice({ commit }, { invoiceData, company_id }) {
    commit('set_loading', true)
    try {
      const res = await api.post(`/api/v1/invoicing/?company_id=${company_id}`, invoiceData)
      commit('add_invoice', res.data)
      return res
    } catch (err) {
      commit('set_error', err.message)
      throw err
    } finally {
      commit('set_loading', false)
    }
  },
  async createInvoiceWithItems({ commit }, { invoiceData, company_id }) {
    commit('set_loading', true)
    try {
      const res = await api.post(`/api/v1/invoicing/with-items/?company_id=${company_id}`, invoiceData)
      commit('add_invoice', res.data)
      return res
    } catch (err) {
      commit('set_error', err.message)
      throw err
    } finally {
      commit('set_loading', false)
    }
  },
  async sendToDian({ commit }, { invoiceId, company_id }) {
    try {
      const res = await api.post(`/api/v1/invoicing/${invoiceId}/send-to-dian/`, null, {
        params: { company_id }
      })
      commit('update_invoice_dian_status', { id: invoiceId, status: res.data.estado_dian })
      return res
    } catch (err) {
      throw err
    }
  },
  async fetchNotes({ commit }, { company_id }) {
    try {
      const res = await api.get('/api/v1/invoicing/credit-debit-notes/', {
        params: { company_id }
      })
      commit('set_notes', res.data)
    } catch (err) {
      throw err
    }
  },
  async createNote({ commit }, { noteData, company_id }) {
    try {
      const res = await api.post(`/api/v1/invoicing/credit-debit-notes/?company_id=${company_id}`, noteData)
      commit('add_note', res.data)
      return res
    } catch (err) {
      throw err
    }
  }
}

const mutations = {
  set_invoices(state, invoices) {
    state.invoices = invoices
  },
  add_invoice(state, invoice) {
    state.invoices.unshift(invoice)
  },
  update_invoice_dian_status(state, { id, status }) {
    const invoice = state.invoices.find(i => i.id === id)
    if (invoice) invoice.estado_dian = status
  },
  set_notes(state, notes) {
    state.notes = notes
  },
  add_note(state, note) {
    state.notes.unshift(note)
  },
  set_loading(state, loading) {
    state.loading = loading
  },
  set_error(state, error) {
    state.error = error
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
