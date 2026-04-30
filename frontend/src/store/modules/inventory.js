import api from '@/services/api'

const state = {
  products: [],
  product: null,
  loading: false,
  error: null
}

const getters = {
  getProducts: state => state.products,
  getProduct: state => state.product,
  isLoading: state => state.loading,
  hasError: state => state.error !== null
}

const actions = {
  async fetchProducts({ commit }, { companyId, skip = 0, limit = 100 } = {}) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get('/api/v1/inventory/', {
        params: { company_id: companyId, skip, limit }
      })
      commit('setProducts', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener los productos')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchProductById({ commit }, { productId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(`/api/v1/inventory/${productId}`, {
        params: { company_id: companyId }
      })
      commit('setProduct', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener el producto')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async fetchProductByBarcode({ commit }, { barcode, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get(`/api/v1/inventory/barcode/${barcode}`, {
        params: { company_id: companyId }
      })
      commit('setProduct', res.data)
      return res
    } catch (err) {
      if (err.response && err.response.status === 404) {
        commit('setProduct', null)
        return { data: null }
      }
      commit('setError', err.response?.data?.detail || 'Error al buscar producto por código de barras')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async createProduct({ commit }, { productData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post('/api/v1/inventory/', productData, {
        params: { company_id: companyId }
      })
      commit('setProduct', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear el producto')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async bulkCreateProducts({ commit }, { bulkData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.post('/api/v1/inventory/bulk', bulkData, {
        params: { company_id: companyId }
      })
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al crear los productos en masa')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async updateProduct({ commit }, { productId, productData, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.put(`/api/v1/inventory/${productId}`, productData, {
        params: { company_id: companyId }
      })
      commit('setProduct', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al actualizar el producto')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async deleteProduct({ commit }, { productId, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      await api.delete(`/api/v1/inventory/${productId}`, {
        params: { company_id: companyId }
      })
      commit('setProduct', null)
      return { status: 'success' }
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al eliminar el producto')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async adjustStock({ commit }, { productId, adjustment, companyId }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.patch(`/api/v1/inventory/${productId}/stock`, null, {
        params: { adjustment, company_id: companyId }
      })
      commit('setProduct', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al ajustar el inventario')
      throw err
    } finally {
      commit('setLoading', false)
    }
  },
  async getLowStockProducts({ commit }, { companyId, skip = 0, limit = 100 }) {
    commit('setLoading', true)
    commit('clearError')
    try {
      const res = await api.get('/api/v1/inventory/low-stock/', {
        params: { company_id: companyId, skip, limit }
      })
      commit('setProducts', res.data)
      return res
    } catch (err) {
      commit('setError', err.response?.data?.detail || 'Error al obtener productos con bajo stock')
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
  setProducts(state, payload) {
    state.products = payload
  },
  setProduct(state, payload) {
    state.product = payload
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
