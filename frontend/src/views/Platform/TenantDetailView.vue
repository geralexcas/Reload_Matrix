<template>
  <div class="tenant-detail-view">
    <div class="view-header">
      <h2 v-if="tenant">{{ tenant.name }}</h2>
      <button class="btn btn-secondary" @click="$router.push('/platform/tenants')">← Volver</button>
    </div>

    <div v-if="loading" class="loading">Cargando...</div>

    <div v-if="tenant">
      <!-- Edit form -->
      <form @submit.prevent="saveTenant" class="tenant-form">
        <div class="form-row">
          <div class="form-group">
            <label>Nombre *</label>
            <input type="text" v-model="editForm.name" required />
          </div>
          <div class="form-group">
            <label>NIT</label>
            <input type="text" :value="`${tenant.nit}-${tenant.dv}`" readonly class="readonly" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Representante Legal *</label>
            <input type="text" v-model="editForm.legal_representative" required />
          </div>
          <div class="form-group">
            <label>Régimen *</label>
            <select v-model="editForm.regimen">
              <option value="COMUN">Común</option>
              <option value="SIMPLE">Simple</option>
              <option value="ESPECIAL">Especial</option>
              <option value="NO_RESPONSABLE">No Responsable</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Dirección</label>
            <input type="text" v-model="editForm.address" />
          </div>
          <div class="form-group">
            <label>Teléfono</label>
            <input type="text" v-model="editForm.phone" />
          </div>
        </div>
        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="editForm.email" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Fecha Inicio Actividades</label>
            <input type="date" v-model="editForm.fecha_inicio_actividades" />
          </div>
          <div class="form-group">
            <label>Resolución Facturación</label>
            <input type="text" v-model="editForm.resolucion_facturacion" />
          </div>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
          <button type="button" class="btn" :class="tenant.is_active ? 'btn-danger' : 'btn-success'" @click="toggleActive">
            {{ tenant.is_active ? 'Desactivar' : 'Activar' }}
          </button>
        </div>
        <div v-if="saveError" class="error-message">{{ saveError }}</div>
        <div v-if="saveSuccess" class="success-message">Cambios guardados</div>
      </form>

      <!-- Users section -->
      <div class="users-section">
        <div class="users-header">
          <h3>Usuarios de la Empresa ({{ users.length }})</h3>
          <button class="btn btn-primary" @click="showCreateUser = !showCreateUser">
            {{ showCreateUser ? 'Cancelar' : '+ Crear Usuario' }}
          </button>
        </div>

        <!-- Create user form -->
        <form v-if="showCreateUser" @submit.prevent="createUser" class="tenant-form create-user-form">
          <div class="form-row">
            <div class="form-group">
              <label>Usuario *</label>
              <input type="text" v-model="createForm.username" required />
            </div>
            <div class="form-group">
              <label>Email *</label>
              <input type="email" v-model="createForm.email" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Nombre completo *</label>
              <input type="text" v-model="createForm.full_name" required />
            </div>
            <div class="form-group">
              <label>Contraseña *</label>
              <input type="password" v-model="createForm.password" required placeholder="Mín 8, mayúscula, minúscula, número, especial" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Rol *</label>
              <select v-model="createForm.role">
                <option value="ADMINISTRADOR">ADMINISTRADOR</option>
                <option value="CONTADOR">CONTADOR</option>
                <option value="TECNICO">TECNICO</option>
                <option value="VENDEDOR">VENDEDOR</option>
                <option value="BODEGUERO">BODEGUERO</option>
                <option value="FACTURADOR">FACTURADOR</option>
              </select>
            </div>
            <div class="form-group">
              <label>
                <input type="checkbox" v-model="createForm.is_superuser" />
                Es administrador de la empresa (tenant-superuser)
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="creatingUser">
              {{ creatingUser ? 'Creando...' : 'Crear Usuario' }}
            </button>
          </div>
          <div v-if="createError" class="error-message">{{ createError }}</div>
        </form>

        <div v-if="loadingUsers" class="loading">Cargando usuarios...</div>
        <div v-else>
          <table class="data-table" v-if="users.length">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Nombre</th>
                <th>Email</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.username }}</td>
                <td>{{ u.full_name }}</td>
                <td>{{ u.email }}</td>
                <td>
                  <span :class="['badge', `badge-${getRoleBadge(u.role)}`]">{{ u.role }}</span>
                </td>
                <td>
                  <span :class="['badge', u.is_active ? 'badge-success' : 'badge-danger']">
                    {{ u.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm" @click="toggleUserStatus(u)" :title="u.is_active ? 'Desactivar' : 'Activar'">
                    <i :class="['fas', u.is_active ? 'fa-ban' : 'fa-check']"></i>
                  </button>
                  <button class="btn btn-sm btn-danger" @click="resetPassword(u)" title="Resetear contraseña">
                    <i class="fas fa-key"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="empty">Esta empresa no tiene usuarios.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TenantDetailView',
  data() {
    return {
      loading: true,
      saving: false,
      loadingUsers: true,
      saveError: null,
      saveSuccess: false,
      editForm: {
        name: '',
        legal_representative: '',
        regimen: 'COMUN',
        address: '',
        phone: '',
        email: '',
        fecha_inicio_actividades: '',
        resolucion_facturacion: ''
      },
      showCreateUser: false,
      createForm: {
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: 'VENDEDOR',
        is_superuser: false
      },
      creatingUser: false,
      createError: null
    }
  },
  computed: {
    tenantId() {
      return this.$route.params.id
    },
    tenant() {
      return this.$store.getters['admin/getCurrentTenant']
    },
    users() {
      return this.$store.getters['admin/getUsers'] || []
    }
  },
  methods: {
    async fetchTenant() {
      this.loading = true
      try {
        await this.$store.dispatch('admin/fetchTenant', this.tenantId)
        this.populateForm()
      } catch (err) {
        console.error('Error fetching tenant:', err)
      } finally {
        this.loading = false
      }
    },
    async fetchUsers() {
      this.loadingUsers = true
      try {
        await this.$store.dispatch('admin/fetchUsers', this.tenantId)
      } catch (err) {
        console.error('Error fetching users:', err)
      } finally {
        this.loadingUsers = false
      }
    },
    populateForm() {
      if (this.tenant) {
        this.editForm.name = this.tenant.name
        this.editForm.legal_representative = this.tenant.legal_representative
        this.editForm.regimen = this.tenant.regimen
        this.editForm.address = this.tenant.address || ''
        this.editForm.phone = this.tenant.phone || ''
        this.editForm.email = this.tenant.email || ''
        this.editForm.fecha_inicio_actividades = this.tenant.fecha_inicio_actividades
        this.editForm.resolucion_facturacion = this.tenant.resolucion_facturacion || ''
      }
    },
    async saveTenant() {
      this.saving = true
      this.saveError = null
      this.saveSuccess = false
      try {
        await this.$store.dispatch('admin/updateTenant', {
          tenantId: this.tenantId,
          tenantData: { ...this.editForm }
        })
        this.saveSuccess = true
        setTimeout(() => { this.saveSuccess = false }, 2000)
      } catch (err) {
        this.saveError = err.response?.data?.detail || 'Error al guardar'
      } finally {
        this.saving = false
      }
    },
    async toggleActive() {
      const action = this.tenant.is_active ? 'desactivar' : 'activar'
      if (!confirm(`¿Seguro que desea ${action} esta empresa?`)) return
      try {
        await this.$store.dispatch('admin/toggleTenantActive', this.tenantId)
        this.tenant.is_active = !this.tenant.is_active
      } catch (err) {
        this.saveError = err.response?.data?.detail || 'Error al cambiar estado'
      }
    },
    async toggleUserStatus(user) {
      try {
        await this.$store.dispatch('admin/toggleUserActive', user.id)
        user.is_active = !user.is_active
      } catch (err) {
        console.error('Error toggling user:', err)
      }
    },
    async resetPassword(user) {
      const newPassword = prompt('Ingrese la nueva contraseña:')
      if (!newPassword) return
      try {
        await this.$store.dispatch('admin/resetUserPassword', {
          userId: user.id,
          newPassword
        })
        alert('Contraseña actualizada')
      } catch (err) {
        alert('Error: ' + (err.response?.data?.detail || 'Error al resetear'))
      }
    },
    getRoleBadge(role) {
      const badges = {
        ADMINISTRADOR: 'primary',
        CONTADOR: 'info',
        FACTURADOR: 'warning',
        VENDEDOR: 'success',
        TECNICO: 'secondary',
        BODEGUERO: 'dark'
      }
      return badges[role] || 'secondary'
    },
    resetCreateForm() {
      this.createForm = {
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: 'VENDEDOR',
        is_superuser: false
      }
      this.createError = null
    },
    async createUser() {
      this.creatingUser = true
      this.createError = null
      try {
        await this.$store.dispatch('admin/createUser', {
          ...this.createForm,
          company_id: Number(this.tenantId)
        })
        this.resetCreateForm()
        this.showCreateUser = false
        await this.fetchUsers()
      } catch (err) {
        this.createError = err.response?.data?.detail || 'Error al crear usuario'
      } finally {
        this.creatingUser = false
      }
    }
  },
  mounted() {
    this.fetchTenant()
    this.fetchUsers()
  }
}
</script>

<style scoped>
.tenant-detail-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.tenant-form {
  background: white;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}
.users-section {
  background: white;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.users-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}
.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}
.users-header h3 {
  margin: 0;
  padding: 0;
  border: none;
}
.create-user-form {
  margin-bottom: 20px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
}
.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.readonly {
  background: #f8f9fa;
  color: #666;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}
.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
}
.data-table th,
.data-table td {
  padding: 10px 12px;
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
.badge-primary { background: #007bff; color: white; }
.badge-info { background: #17a2b8; color: white; }
.badge-warning { background: #ffc107; color: #212529; }
.badge-success { background: #28a745; color: white; }
.badge-secondary { background: #6c757d; color: white; }
.badge-dark { background: #343a40; color: white; }
.badge-danger { background: #dc3545; color: white; }
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}
.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-success { background: #28a745; color: white; }
.btn-danger { background: #dc3545; color: white; }
.btn-sm { padding: 5px 10px; margin-right: 5px; }
.loading, .empty {
  text-align: center;
  padding: 30px;
  color: #666;
}
.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}
.success-message {
  background: #d4edda;
  color: #155724;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}
</style>