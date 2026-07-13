<template>
  <div class="create-tenant-view">
    <div class="view-header">
      <h2>Crear Nueva Empresa</h2>
      <button class="btn btn-secondary" @click="$router.back()">← Volver</button>
    </div>

    <form @submit.prevent="submitForm" class="tenant-form">
      <h3>Datos de la Empresa</h3>
      <div class="form-group">
        <label>Nombre *</label>
        <input type="text" v-model="form.name" required placeholder="Nombre de la empresa" />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>NIT *</label>
          <input type="text" v-model="form.nit" required placeholder="900123456" />
        </div>
        <div class="form-group">
          <label>Dígito de Verificación *</label>
          <input type="text" v-model="form.dv" required maxlength="1" placeholder="7" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Representante Legal *</label>
          <input type="text" v-model="form.legal_representative" required placeholder="Nombre del representante" />
        </div>
        <div class="form-group">
          <label>Régimen *</label>
          <select v-model="form.regimen" required>
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
          <input type="text" v-model="form.address" placeholder="Calle 123 #45-67" />
        </div>
        <div class="form-group">
          <label>Teléfono</label>
          <input type="text" v-model="form.phone" placeholder="3001234567" />
        </div>
      </div>
      <div class="form-group">
        <label>Email</label>
        <input type="email" v-model="form.email" placeholder="empresa@correo.com" />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Fecha de Inicio de Actividades *</label>
          <input type="date" v-model="form.fecha_inicio_actividades" required />
        </div>
        <div class="form-group">
          <label>Resolución de Facturación</label>
          <input type="text" v-model="form.resolucion_facturacion" placeholder="187600000001" />
        </div>
      </div>

      <h3>Usuario Administrador Inicial</h3>
      <div class="form-group">
        <label>Nombre Completo *</label>
        <input type="text" v-model="adminForm.full_name" required placeholder="Nombre del administrador" />
      </div>
      <div class="form-group">
        <label>Email *</label>
        <input type="email" v-model="adminForm.email" required placeholder="admin@empresa.com" />
        <small class="hint">Se usará como identificador de acceso del administrador del tenant.</small>
      </div>
      <div class="form-group">
        <label>Contraseña *</label>
        <input type="password" v-model="adminForm.password" required placeholder="Mínimo 8 caracteres" />
        <small class="hint">Debe incluir: mayúscula, minúscula, número y carácter especial</small>
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="$router.back()">Cancelar</button>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Creando...' : 'Crear Empresa' }}
        </button>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="success" class="success-message">{{ success }}</div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'CreateTenantView',
  data() {
    return {
      loading: false,
      error: null,
      success: null,
      form: {
        name: '',
        nit: '',
        dv: '',
        legal_representative: '',
        regimen: 'COMUN',
        address: '',
        phone: '',
        email: '',
        fecha_inicio_actividades: '',
        resolucion_facturacion: ''
      },
      adminForm: {
        full_name: '',
        email: '',
        username: '',
        password: ''
      }
    }
  },
  methods: {
    async submitForm() {
      this.loading = true
      this.error = null
      this.success = null
      try {
        const payload = { ...this.form, admin_user: { ...this.adminForm } }
        await this.$store.dispatch('admin/createTenant', payload)
        this.success = 'Empresa creada exitosamente'
        setTimeout(() => {
          this.$router.push('/platform/tenants')
        }, 1500)
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al crear empresa'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.create-tenant-view {
  max-width: 800px;
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
}
.tenant-form h3 {
  margin-top: 25px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}
.tenant-form h3:first-child {
  margin-top: 0;
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
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}
.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
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