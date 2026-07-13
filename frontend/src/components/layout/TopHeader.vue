<template>
  <header class="top-header">
    <div class="header-left">
      <button class="menu-toggle" @click="$emit('toggle-sidebar')">☰</button>
      <span class="page-title">{{ title }}</span>
    </div>
    <div class="header-right">
      <span class="company-name" v-if="company">{{ company.name }}</span>
      <span class="user-info" v-if="username">
        <i class="fas fa-user"></i> {{ username }}
      </span>
      <button class="btn-logout" @click="onLogout">Cerrar Sesión</button>
    </div>
  </header>
</template>

<script>
export default {
  name: 'TopHeader',
  props: {
    title: {
      type: String,
      default: ''
    }
  },
  data() {
    return {}
  },
  computed: {
    username() {
      return this.$store.getters['auth/user']?.username || null
    },
    company() {
      return this.$store.getters['company/getCompany'] || null
    }
  },
  methods: {
    async fetchCompanies() {
      try {
        await this.$store.dispatch('company/fetchCompanies')
        const companies = this.$store.getters['company/getCompanies'] || []
        // ponytail: platform-admin has no tenant; don't pollute every request
        // with ?company_id=N (the api.js interceptor would inject it globally).
        const isPlatformAdmin = this.$store.getters['auth/isPlatformAdmin']
        if (isPlatformAdmin) {
          sessionStorage.removeItem('selectedCompanyId')
          this.$store.commit('company/setCompany', null)
        } else if (companies.length > 0) {
          this.$store.commit('company/setCompany', companies[0])
          sessionStorage.setItem('selectedCompanyId', companies[0].id)
        }
      } catch (err) {
        console.error('Error fetching companies:', err)
      }
    },
    onLogout() {
      this.$store.dispatch('auth/logout').then(() => {
        sessionStorage.removeItem('selectedCompanyId')
        this.$router.push('/login')
      })
    }
  },
  mounted() {
    this.fetchCompanies()
  }
}
</script>

<style scoped>
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.menu-toggle {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #333;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.company-name {
  color: #2c3e50;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 4px 12px;
  background: #f0f4f8;
  border-radius: 4px;
}

.user-info {
  color: #666;
  font-size: 0.9rem;
}

.user-info i {
  margin-right: 4px;
}

.btn-logout {
  padding: 0.5rem 1rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-logout:hover {
  background-color: #c82333;
}
</style>