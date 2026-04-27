<template>
  <div class="partners-view">
    <div class="view-header">
      <h2>Gestión de Socios</h2>
      <button class="btn btn-primary" @click="router.push('/partners/new')">+ Nuevo Socio</button>
    </div>

    <div v-if="loading" class="loading">Cargando...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <table class="data-table" v-if="partners.length">
        <thead>
          <tr>
            <th>NIT</th>
            <th>Nombre</th>
            <th>Tipo</th>
            <th>Responsabilidad Fiscal</th>
            <th>Email</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="partner in partners" :key="partner.id">
            <td>{{ partner.nit }}</td>
            <td>{{ partner.name }}</td>
            <td>{{ partner.partner_type }}</td>
            <td>{{ partner.responsibility_fiscal }}</td>
            <td>{{ partner.email || '-' }}</td>
            <td>
              <button class="btn btn-sm" @click="editPartner(partner)">Editar</button>
              <button class="btn btn-sm btn-danger" @click="deletePartner(partner.id)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">No hay socios registrados.</p>
    </div>

  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'PartnersView',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      // Los datos locales de formulario ahora se manejan en PartnerFormView.vue
    }
  },
  computed: {
    partners() {
      return this.$store.getters['partners/getPartners']
    },
    loading() {
      return this.$store.getters['partners/isLoading']
    },
    error() {
      return this.$store.getters['partners/hasError']
        ? this.$store.state.partners.error
        : null
    },
    companyId() {
      return this.$store.getters['company/getCompany']?.id || 1
    }
  },
  async mounted() {
    await this.$store.dispatch('partners/fetchPartners', { companyId: this.companyId })
  },
  methods: {
    editPartner(partner) {
      this.router.push(`/partners/edit/${partner.id}`)
    },
    async deletePartner(id) {
      if (confirm('¿Está seguro de eliminar este socio?')) {
        await this.$store.dispatch('partners/deletePartner', {
          partnerId: id,
          companyId: this.companyId
        })
        await this.$store.dispatch('partners/fetchPartners', { companyId: this.companyId })
      }
    },
    resetForm() {
      // Not needed anymore
    }
  }
}
</script>

<style scoped>
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.data-table th, .data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  margin-right: 0.25rem;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.loading, .error, .empty {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #dc3545;
}
</style>
