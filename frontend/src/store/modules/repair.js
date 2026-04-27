import api from '@/services/api'

const state = {
  orders: [],
  currentOrder: null,
  warranties: [],
  technicians: [],
  loading: false,
  error: null
}

const getters = {
  allOrders: state => state.orders,
  currentOrder: state => state.currentOrder,
  warranties: state => state.warranties,
  technicians: state => state.technicians,
  loading: state => state.loading
}

const actions = {
  async fetchOrders({ commit }, { company_id, skip = 0, limit = 100 }) {
    commit('set_loading', true)
    try {
      const res = await api.get('/api/v1/repair/', {
        params: { company_id, skip, limit }
      })
      commit('set_orders', res.data)
      return res
    } catch (err) {
      commit('set_error', err.message)
      throw err
    } finally {
      commit('set_loading', false)
    }
  },
  async createOrder({ commit }, { orderData, company_id }) {
    commit('set_loading', true)
    try {
      const res = await api.post('/api/v1/repair/simple/', orderData, {
        params: { company_id }
      })
      commit('add_order', res.data)
      return res
    } catch (err) {
      commit('set_error', err.message)
      throw err
    } finally {
      commit('set_loading', false)
    }
  },
  async updateStatus({ commit }, { orderId, status, company_id }) {
    try {
      const res = await api.put(`/api/v1/repair/${orderId}/status/`, { status }, {
        params: { company_id }
      })
      commit('update_order_status', { id: orderId, status: res.data.status })
      return res
    } catch (err) {
      throw err
    }
  },
  async generateInvoice({ commit }, { orderId, company_id, paymentData = null }) {
    try {
      // The backend now accepts paymentData in the request body
      const res = await api.post(`/api/v1/repair/${orderId}/generate-invoice/`, paymentData || {}, {
        params: { company_id }
      })
      return res
    } catch (err) {
      throw err
    }
  },
  async fetchWarranties({ commit }, { company_id, status }) {
    try {
      const params = { company_id }
      if (status) params.status = status
      const res = await api.get('/api/v1/repair/warranties/', { params })
      commit('set_warranties', res.data)
      return res
    } catch (err) {
      throw err
    }
  },
  async fileWarrantyClaim({ commit }, { warrantyId, claimData, company_id }) {
    try {
      const res = await api.post(`/api/v1/repair/warranties/${warrantyId}/claim/`, claimData, {
        params: { company_id }
      })
      return res
    } catch (err) {
      throw err
    }
  },
  async fetchTechnicians({ commit }, { company_id }) {
    try {
      const res = await api.get('/api/v1/repair/technicians/', {
        params: { company_id }
      })
      commit('set_technicians', res.data)
      return res
    } catch (err) {
      throw err
    }
  }
}

const mutations = {
  set_orders(state, orders) {
    state.orders = orders
  },
  add_order(state, order) {
    state.orders.unshift(order)
  },
  update_order_status(state, { id, status }) {
    const order = state.orders.find(o => o.id === id)
    if (order) order.status = status
  },
  set_warranties(state, warranties) {
    state.warranties = warranties
  },
  set_technicians(state, technicians) {
    state.technicians = technicians
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