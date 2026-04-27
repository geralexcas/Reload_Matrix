<template>
  <div class="users-view">
    <div class="view-header">
      <h2>Gestión de Usuarios</h2>
      <button class="btn btn-primary" @click="showForm = true">
        <i class="fas fa-plus"></i> Crear Usuario
      </button>
    </div>

    <!-- Modal para crear usuario -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Crear Nuevo Usuario</h3>
          <button class="close-btn" @click="showForm = false">&times;</button>
        </div>
        <form @submit.prevent="createUser">
          <div class="form-group">
            <label>Nombre Completo *</label>
            <input type="text" v-model="form.full_name" required placeholder="Nombre completo" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Email *</label>
              <input type="email" v-model="form.email" required placeholder="email@empresa.com" />
            </div>
            <div class="form-group">
              <label>Usuario *</label>
              <input type="text" v-model="form.username" required placeholder="usuario" />
            </div>
          </div>
          <div class="form-group">
            <label>Contraseña *</label>
            <input type="password" v-model="form.password" required placeholder="Mínimo 8 caracteres" />
            <small class="hint">Debe incluir: mayúscula, minúscula, número y carácter especial</small>
          </div>
          <div class="form-group">
            <label>Rol *</label>
            <select v-model="form.role" required>
              <option value="">Seleccionar rol...</option>
              <option value="ADMINISTRADOR">Administrador</option>
              <option value="CONTADOR">Contador</option>
              <option value="FACTURADOR">Facturador</option>
              <option value="VENDEDOR">Vendedor</option>
              <option value="TECNICO">Técnico</option>
              <option value="BODEGUERO">Bodeguero</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="showForm = false">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Creando...' : 'Crear Usuario' }}
            </button>
          </div>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
        </form>
      </div>
    </div>

    <!-- Lista de usuarios -->
    <div v-if="loadingUsers" class="loading">Cargando usuarios...</div>
    <div v-else>
      <table class="data-table" v-if="users.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Usuario</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.full_name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.username }}</td>
            <td>
              <span :class="['badge', `badge-${getRoleBadge(user.role)}`]">
                {{ user.role }}
              </span>
            </td>
            <td>
              <span :class="['badge', user.is_active ? 'badge-success' : 'badge-danger']">
                {{ user.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>
              <button class="btn btn-sm" @click="toggleUserStatus(user)" :title="user.is_active ? 'Desactivar' : 'Activar'">
                <i :class="['fas', user.is_active ? 'fa-ban' : 'fa-check']"></i>
              </button>
              <button class="btn btn-sm btn-danger" @click="resetPassword(user)" title="Resetear contraseña">
                <i class="fas fa-key"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">No hay usuarios registrados.</p>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'UsersView',
  data() {
    return {
      users: [],
      showForm: false,
      loading: false,
      loadingUsers: true,
      error: null,
      success: null,
      form: {
        full_name: '',
        email: '',
        username: '',
        password: '',
        role: ''
      }
    }
  },
  computed: {
    companyId() {
      return this.$store.getters['company/getCompany']?.id || null
    }
  },
  methods: {
    async fetchUsers() {
      this.loadingUsers = true
      try {
        const res = await api.get('/api/v1/admin/users/')
        this.users = res.data
      } catch (err) {
        console.error('Error fetching users:', err)
      } finally {
        this.loadingUsers = false
      }
    },
    async createUser() {
      this.loading = true
      this.error = null
      this.success = null
      try {
        const payload = {
          email: this.form.email,
          username: this.form.username,
          password: this.form.password,
          full_name: this.form.full_name,
          role: this.form.role
        }
        // Only add company_id if admin has a company
        if (this.companyId) {
          payload.company_id = this.companyId
        }
        await api.post('/api/v1/admin/users/', payload)
        this.success = 'Usuario creado exitosamente'
        this.resetForm()
        this.fetchUsers()
        setTimeout(() => {
          this.showForm = false
          this.success = null
        }, 2000)
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al crear usuario'
      } finally {
        this.loading = false
      }
    },
    async toggleUserStatus(user) {
      try {
        await api.patch(`/api/v1/admin/users/${user.id}/toggle-active`)
        user.is_active = !user.is_active
      } catch (err) {
        console.error('Error toggling user status:', err)
      }
    },
    async resetPassword(user) {
      const newPassword = prompt('Ingrese la nueva contraseña:')
      if (!newPassword) return
      try {
        await api.post(`/api/v1/admin/users/${user.id}/reset-password/`, {
          new_password: newPassword
        })
        alert('Contraseña actualizada exitosamente')
      } catch (err) {
        alert('Error: ' + (err.response?.data?.detail || 'Error al resetear contraseña'))
      }
    },
    resetForm() {
      this.form = {
        full_name: '',
        email: '',
        username: '',
        password: '',
        role: ''
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
    }
  },
  mounted() {
    this.fetchUsers()
  }
}
</script>

<style scoped>
.users-view {
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 25px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.hint {
  color: #666;
  font-size: 0.85rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
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

.badge-primary { background: #007bff; color: white; }
.badge-info { background: #17a2b8; color: white; }
.badge-warning { background: #ffc107; color: #212529; }
.badge-success { background: #28a745; color: white; }
.badge-secondary { background: #6c757d; color: white; }
.badge-dark { background: #343a40; color: white; }
.badge-danger { background: #dc3545; color: white; }

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-danger { background: #dc3545; color: white; }
.btn-sm { padding: 5px 10px; }

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

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}
</style>