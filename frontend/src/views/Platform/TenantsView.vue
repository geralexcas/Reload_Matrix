<template>
  <div class="tenants-view">
    <div class="view-header">
      <h2>Gestión de Empresas</h2>
      <button class="btn btn-primary" @click="$router.push('/platform/tenants/create')">
        <i class="fas fa-plus"></i> Crear Empresa
      </button>
    </div>

    <div v-if="loading" class="loading">Cargando empresas...</div>
    <div v-else>
      <table class="data-table" v-if="tenants.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>NIT</th>
            <th>Régimen</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tenants" :key="t.id">
            <td>{{ t.id }}</td>
            <td>{{ t.name }}</td>
            <td>{{ t.nit }}-{{ t.dv }}</td>
            <td>{{ t.regimen }}</td>
            <td>
              <span :class="['badge', t.is_active ? 'badge-success' : 'badge-danger']">
                {{ t.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>
              <button class="btn btn-sm" @click="$router.push(`/platform/tenants/${t.id}`)" title="Ver detalle">
                <i class="fas fa-eye"></i>
              </button>
              <button class="btn btn-sm" @click="toggleActive(t)" :title="t.is_active ? 'Desactivar' : 'Activar'">
                <i :class="['fas', t.is_active ? 'fa-ban' : 'fa-check']"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">No hay empresas registradas.</p>
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script>
export default {
  name: 'TenantsView',
  data() {
    return {
      loading: true,
      error: null
    }
  },
  computed: {
    tenants() {
      return this.$store.getters['admin/getTenants'] || []
    }
  },
  methods: {
    async fetchTenants() {
      this.loading = true
      try {
        await this.$store.dispatch('admin/fetchTenants')
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al cargar empresas'
      } finally {
        this.loading = false
      }
    },
    async toggleActive(tenant) {
      const action = tenant.is_active ? 'desactivar' : 'activar'
      if (!confirm(`¿Seguro que desea ${action} la empresa "${tenant.name}"?`)) return
      try {
        await this.$store.dispatch('admin/toggleTenantActive', tenant.id)
        tenant.is_active = !tenant.is_active
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al cambiar estado'
      }
    }
  },
  mounted() {
    this.fetchTenants()
  }
}
</script>

<style scoped>
.tenants-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.data-table th,
.data-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}
.data-table th {
  background: #f8f9fa;
  font-weight: 600;
}
.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}
.badge-success { background: #28a745; color: white; }
.badge-danger { background: #dc3545; color: white; }
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}
.btn-primary { background: #007bff; color: white; }
.btn-sm { padding: 5px 10px; margin-right: 5px; }
.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #666;
}
.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}
</style>