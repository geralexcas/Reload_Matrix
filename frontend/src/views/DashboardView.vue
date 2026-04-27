<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Socios</h3>
        <p class="stat-value">{{ stats.partners }}</p>
      </div>
      <div class="stat-card">
        <h3>Productos</h3>
        <p class="stat-value">{{ stats.products }}</p>
      </div>
      <div class="stat-card">
        <h3>Facturas</h3>
        <p class="stat-value">{{ stats.invoices }}</p>
      </div>
      <div class="stat-card">
        <h3>Órdenes de Reparación</h3>
        <p class="stat-value">{{ stats.repairs }}</p>
      </div>
    </div>
    <div class="quick-links">
      <router-link to="/partners" class="quick-link">Gestionar Socios</router-link>
      <router-link to="/inventory" class="quick-link">Gestionar Inventario</router-link>
      <router-link to="/invoicing" class="quick-link">Crear Factura</router-link>
      <router-link to="/repair" class="quick-link">Nueva Reparación</router-link>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'DashboardView',
  data() {
    return {
      stats: {
        partners: 0,
        products: 0,
        invoices: 0,
        repairs: 0
      }
    }
  },
  computed: {
    companyId() {
      return this.$store.getters['company/selectedCompanyId']
    }
  },
  watch: {
    companyId: {
      handler: 'fetchStats',
      immediate: true
    }
  },
  methods: {
    async fetchStats() {
      if (!this.companyId) return
      try {
        const res = await api.get('/api/v1/dashboard/stats', {
          params: { company_id: this.companyId }
        })
        this.stats = res.data
      } catch (err) {
        console.error('Error fetching dashboard stats:', err)
      }
    }
  }
}
</script>

<style scoped>
.dashboard h1 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.quick-links {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.quick-link {
  padding: 0.75rem 1.5rem;
  background: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
}

.quick-link:hover {
  background: #0056b3;
}
</style>
