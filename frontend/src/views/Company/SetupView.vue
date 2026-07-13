<template>
  <div class="setup-container">
    <div class="setup-card">
      <h2>{{ isEditing ? 'Gestión de la Empresa' : 'Configuración Inicial de la Empresa' }}</h2>
      
      <!-- Logo Section -->
      <div class="logo-section" v-if="isEditing">
        <div class="logo-preview">
          <img v-if="logoPreviewUrl" :src="logoPreviewUrl" alt="Logo de la empresa" />
          <div v-else class="no-logo">Sin Logo</div>
        </div>
        <div class="logo-upload">
          <label for="logo_input" class="btn btn-secondary">
            {{ company.logo_url ? 'Cambiar Logo' : 'Subir Logo' }}
          </label>
          <input 
            type="file" 
            id="logo_input" 
            @change="onFileChange" 
            accept="image/*" 
            style="display: none"
          />
          <small v-if="logoFile">{{ logoFile.name }}</small>
          <button 
            v-if="logoFile" 
            @click="uploadLogo" 
            class="btn btn-success btn-small"
            :disabled="isLoading"
          >
            Confirmar Logo
          </button>
        </div>
      </div>

      <form @submit.prevent="onSubmit">
        <div class="form-group">
          <label for="company_name">Nombre de la Empresa:</label>
          <input 
            type="text" 
            id="company_name" 
            v-model="company.name" 
            required
            maxlength="255"
            placeholder="Ingrese el nombre de su empresa"
          />
        </div>
        
        <div class="form-group">
          <label for="company_nit">NIT:</label>
          <input 
            type="text" 
            id="company_nit" 
            v-model="company.nit" 
            required
            maxlength="20"
            placeholder="Ej: 123456789-0"
          />
          <small class="form-text">Formato: números y guiones únicamente (ej: 123456789-0)</small>
        </div>
        
        <div class="form-group">
          <label for="company_dv">Dígito de Verificación (DV):</label>
          <input 
            type="text" 
            id="company_dv" 
            v-model="company.dv" 
            required
            maxlength="1"
            placeholder="Ej: 0 o K"
          />
          <small class="form-text">Un solo carácter (número o letra)</small>
        </div>
        
        <div class="form-group">
          <label for="company_representative">Representante Legal:</label>
          <input 
            type="text" 
            id="company_representative" 
            v-model="company.legal_representative" 
            required
            maxlength="255"
            placeholder="Nombre del representante legal"
          />
        </div>
        
        <div class="form-group">
          <label for="company_address">Dirección:</label>
          <input 
            type="text" 
            id="company_address" 
            v-model="company.address" 
            maxlength="500"
            placeholder="Dirección de la empresa"
          />
        </div>
        
        <div class="form-group">
          <label for="company_phone">Teléfono:</label>
          <input 
            type="tel" 
            id="company_phone" 
            v-model="company.phone" 
            maxlength="50"
            placeholder="Número de contacto"
          />
        </div>
        
        <div class="form-group">
          <label for="company_email">Email:</label>
          <input 
            type="email" 
            id="company_email" 
            v-model="company.email" 
            maxlength="255"
            placeholder="correo@empresa.com"
          />
        </div>
        
        <div class="form-group">
          <label for="company_regimen">Régimen Tributario:</label>
          <select 
            id="company_regimen" 
            v-model="company.regimen" 
            required
          >
            <option value="">Seleccione un régimen</option>
            <option value="COMUN">Régimen Común</option>
            <option value="SIMPLE">Régimen Simple de Tributación</option>
            <option value="ESPECIAL">Régimen Especial</option>
            <option value="NO_RESPONSABLE">No Responsable de IVA (Régimen Simplificado)</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="company_start_date">Fecha de Inicio de Actividades:</label>
          <input 
            type="date" 
            id="company_start_date" 
            v-model="company.fecha_inicio_actividades" 
            required
          />
        </div>
        
        <div class="form-group">
          <label for="company_resolution">Resolución de Facturación (DIAN):</label>
          <input
            type="text"
            id="company_resolution"
            v-model="company.resolucion_facturacion"
            maxlength="100"
            placeholder="Número de resolución de la DIAN (opcional)"
          />
          <small class="form-text">Resolución que autoriza la facturación electrónica</small>
        </div>

        <h3 class="section-divider">Personalización de Documentos</h3>

        <div class="form-group">
          <label for="company_slogan">Slogan (línea bajo el logo en facturas):</label>
          <input
            type="text"
            id="company_slogan"
            v-model="company.slogan"
            maxlength="255"
            placeholder="Ej: Computadores y Reparación al Mejor Precio"
          />
        </div>

        <div class="form-group">
          <label for="company_website">Sitio Web:</label>
          <input
            type="url"
            id="company_website"
            v-model="company.website"
            maxlength="255"
            placeholder="www.miempresa.com"
          />
        </div>

        <div class="form-group">
          <label for="company_invoice_footer">Nota Legal para Facturas y Recibos:</label>
          <textarea
            id="company_invoice_footer"
            v-model="company.invoice_footer_note"
            rows="6"
            placeholder="Texto legal que aparece al pie de facturas y recibos de caja. Ej: Nota de garantía, responsabilidad, ley 1231 de 2008, etc."
          ></textarea>
          <small class="form-text">Se imprime al pie de la factura de venta y el recibo de caja.</small>
        </div>

        <div class="form-group">
          <label for="company_repair_footer">Nota Legal para Órdenes de Reparación:</label>
          <textarea
            id="company_repair_footer"
            v-model="company.repair_footer_note"
            rows="6"
            placeholder="Texto legal que aparece al pie de la orden de servicio. Ej: Condiciones de bodegaje, garantía de reparación, responsabilidad de datos, habeas data, etc."
          ></textarea>
          <small class="form-text">Se imprime al pie de la orden de servicio técnico.</small>
        </div>

        <div class="form-group">
          <button type="submit" class="btn btn-primary btn-large" :disabled="isLoading">
            {{ isEditing ? 'Actualizar Empresa' : 'Crear Empresa y Continuar' }}
          </button>
        </div>
        
        <div class="form-group" v-if="error">
          <p class="error-message">{{ error }}</p>
        </div>
        
        <div class="form-group" v-if="success">
          <p class="success-message">{{ success }}</p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'SetupView',
  data() {
    return {
      company: {
        id: null,
        name: '',
        nit: '',
        dv: '',
        legal_representative: '',
        address: '',
        phone: '',
        email: '',
        regimen: 'COMUN',
        fecha_inicio_actividades: '',
        resolucion_facturacion: '',
        slogan: '',
        website: '',
        invoice_footer_note: '',
        repair_footer_note: '',
        logo_url: null
      },
      logoFile: null,
      error: null,
      success: null,
      isLoading: false
    }
  },
  computed: {
    isLoggedIn() {
      return this.$store.getters['auth/isLoggedIn']
    },
    isEditing() {
      return !!this.company.id || !!this.$store.getters['company/selectedCompanyId']
    },
    logoPreviewUrl() {
      if (this.company.logo_url) {
        return `${api.defaults.baseURL}${this.company.logo_url}`
      }
      return null
    }
  },
  async mounted() {
    const selectedId = this.$store.getters['company/selectedCompanyId']
    if (selectedId) {
      await this.loadCompany(selectedId)
    }
  },
  methods: {
    async loadCompany(id) {
      this.isLoading = true
      try {
        const res = await this.$store.dispatch('company/fetchCompany', id)
        this.company = { ...res.data }
        // Format date for input type="date"
        if (this.company.fecha_inicio_actividades) {
          this.company.fecha_inicio_actividades = this.company.fecha_inicio_actividades.split('T')[0]
        }
      } catch (err) {
        this.error = 'Error al cargar los datos de la empresa'
      } finally {
        this.isLoading = false
      }
    },
    onFileChange(e) {
      const file = e.target.files[0]
      if (file) {
        this.logoFile = file
      }
    },
    async uploadLogo() {
      if (!this.logoFile) return
      this.isLoading = true
      this.error = null
      this.success = null
      try {
        await this.$store.dispatch('company/uploadLogo', {
          companyId: this.company.id,
          file: this.logoFile
        })
        this.success = 'Logo actualizado exitosamente'
        this.logoFile = null
        // Reload company to get new logo_url
        await this.loadCompany(this.company.id)
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al subir el logo'
      } finally {
        this.isLoading = false
      }
    },
    async onSubmit() {
      this.error = null
      this.success = null
      this.isLoading = true
      
      try {
        if (!this.isLoggedIn) {
          this.$router.push('/login')
          return
        }
        
        if (this.isEditing) {
          const companyId = this.company.id || this.$store.getters['company/selectedCompanyId']
          // Clone and remove fields that should not be updated via general PUT
          const updateData = { ...this.company }
          delete updateData.id
          delete updateData.logo_url
          delete updateData.is_active
          delete updateData.created_at
          delete updateData.updated_at
          
          await this.$store.dispatch('company/updateCompany', {
            companyId,
            companyData: updateData
          })
          this.success = 'Empresa actualizada exitosamente'
        } else {
          await this.$store.dispatch('company/createCompany', this.company)
          this.success = 'Empresa creada exitosamente.'
          setTimeout(() => {
            this.$router.push('/')
          }, 1500)
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al procesar la solicitud'
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.setup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 100px);
  background-color: #f8f9fa;
  padding: 20px;
}

.setup-card {
  background: white;
  padding: 2.5rem;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 600px;
}

.setup-card h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #2c3e50;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f1f3f5;
  border-radius: 8px;
}

.logo-preview {
  width: 150px;
  height: 150px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 2px solid #dee2e6;
}

.logo-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.no-logo {
  color: #adb5bd;
  font-weight: 600;
}

.logo-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.875rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 3px rgba(0,123,255,0.25);
}

.form-group .form-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.section-divider {
  margin-top: 2rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e9ecef;
  font-size: 1.1rem;
  color: #003366;
}

.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.9rem;
  resize: vertical;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #218838;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-large {
  padding: 1rem;
  font-size: 1.125rem;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #f5c6cb;
  margin-top: 1rem;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #c3e6cb;
  margin-top: 1rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .setup-card {
    padding: 1.5rem;
  }
  
  .setup-card h2 {
    font-size: 1.5rem;
  }
}
</style>