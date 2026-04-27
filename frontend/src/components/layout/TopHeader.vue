<template>
  <header class="top-header">
    <div class="header-left">
      <button class="menu-toggle" @click="$emit('toggle-sidebar')">☰</button>
      <span class="page-title">{{ title }}</span>
    </div>
    <div class="header-right">
      <!-- Selector de empresa -->
      <div class="company-selector" v-if="companies.length > 0">
        <select v-model="selectedCompanyId" @change="onCompanyChange">
          <option value="" disabled>Seleccionar empresa...</option>
          <option v-for="c in companies" :key="c.id" :value="c.id">
            {{ c.name }} ({{ c.nit }})
          </option>
        </select>
      </div>
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
    return {
      selectedCompanyId: null
    }
  },
  computed: {
    username() {
      return this.$store.getters['auth/user']?.username || null
    },
    companies() {
      return this.$store.getters['company/getCompanies'] || []
    }
  },
  methods: {
    async fetchCompanies() {
      try {
        await this.$store.dispatch('company/fetchCompanies')
        // Restaurar empresa seleccionada de sessionStorage después de cargar empresas
        this.$nextTick(() => {
          const savedId = sessionStorage.getItem('selectedCompanyId')
          if (savedId && this.companies.length > 0) {
            const savedCompany = this.companies.find(c => c.id === parseInt(savedId))
            if (savedCompany) {
              this.selectedCompanyId = savedCompany.id
              this.$store.commit('company/setCompany', savedCompany)
            }
          } else if (this.companies.length > 0) {
            this.selectedCompanyId = this.companies[0].id
            this.$store.commit('company/setCompany', this.companies[0])
            sessionStorage.setItem('selectedCompanyId', this.companies[0].id)
          }
        })
      } catch (err) {
        console.error('Error fetching companies:', err)
      }
    },
    onCompanyChange() {
      const company = this.companies.find(c => c.id === this.selectedCompanyId)
      if (company) {
        this.$store.commit('company/setCompany', company)
        sessionStorage.setItem('selectedCompanyId', company.id)
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

.company-selector select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f8f9fa;
  font-size: 0.85rem;
  max-width: 200px;
  cursor: pointer;
}

.company-selector select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
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