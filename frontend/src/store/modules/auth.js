import api from '@/services/api'

const state = {
  token: sessionStorage.getItem('token') || '',
  refreshToken: sessionStorage.getItem('refreshToken') || '',
  user: null,
  status: '',
  hasLoadedOnce: false
}

const getters = {
  isLoggedIn: state => !!state.token,
  authState: state => state.status,
  user: state => state.user,
  isPlatformAdmin: state => state.user?.is_superuser && !state.user?.company_id,
  hasCompany: state => !!state.user?.company_id
}

const actions = {
  async login({ dispatch, commit }, credentials) {
    commit('auth_request')
    try {
      const params = new URLSearchParams()
      params.append('username', credentials.username)
      params.append('password', credentials.password)

      const res = await api.post('/api/v1/auth/token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      const token = res.data.access_token
      const refreshToken = res.data.refresh_token

      sessionStorage.setItem('token', token)
      if (refreshToken) {
        sessionStorage.setItem('refreshToken', refreshToken)
      }
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`

      // Fetch full profile
      const profile = await dispatch('fetchProfile')

      // Fetch company data if user belongs to one
      if (profile?.company_id) {
        await dispatch('company/fetchCompany', profile.company_id, { root: true })
      }

      commit('auth_success', { token, user: state.user })
      return res
    } catch (err) {
      commit('auth_error')
      sessionStorage.removeItem('token')
      throw err
    }
  },
  async fetchProfile({ commit }) {
    try {
      const res = await api.get('/api/v1/users/me')
      commit('set_user', res.data)
      return res.data
    } catch (err) {
      console.error('Error fetching profile:', err)
      throw err
    }
  },
  async register({ commit }, userData) {
    commit('auth_request')
    try {
      const res = await api.post('/api/v1/auth/register', userData)
      commit('auth_success', { token: '', user: userData })
      return res
    } catch (err) {
      commit('auth_error')
      sessionStorage.removeItem('token')
      throw err
    }
  },
  async logout({ commit }) {
    const refreshToken = sessionStorage.getItem('refreshToken')
    const accessToken = sessionStorage.getItem('token')
    if (refreshToken || accessToken) {
      try {
        await api.post('/api/v1/auth/logout', {
          refresh_token: refreshToken || '',
          access_token: accessToken || ''
        })
      } catch (e) {
        // Ignore errors during logout
      }
    }
    commit('auth_logout')
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('refreshToken')
    sessionStorage.removeItem('selectedCompanyId')
    delete api.defaults.headers.common['Authorization']
  }
}

const mutations = {
  auth_request(state) {
    state.status = 'loading'
  },
  auth_success(state, { token, user }) {
    state.status = 'success'
    state.token = token
    state.user = user
  },
  set_user(state, user) {
    state.user = user
  },
  auth_error(state) {
    state.status = 'error'
  },
  auth_logout(state) {
    state.token = ''
    state.refreshToken = ''
    state.user = null
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
