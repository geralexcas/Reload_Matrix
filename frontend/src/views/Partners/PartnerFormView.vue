<template>
  <div class="partner-form-view">
    <div class="view-header mb-4">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <i class="fas fa-arrow-left"></i>
        </button>
        <div>
          <h2>{{ isEditing ? 'Editar Cliente/Socio' : 'Nuevo Cliente/Socio' }}</h2>
          <p class="text-muted">{{ isEditing ? 'Actualice la información del registro' : 'Ingrese los datos para registrar un nuevo cliente o socio' }}</p>
        </div>
      </div>
    </div>

    <div class="form-container">
      <form @submit.prevent="savePartner" class="premium-card">
        <div class="card-section">
          <h3 class="section-title"><i class="fas fa-user-circle"></i> Información Básica</h3>
          <div class="form-grid">
            <div class="form-group full-width">
              <label>Nombre Completo / Razón Social *</label>
              <input v-model="form.name" type="text" required placeholder="Nombre del cliente o empresa" class="premium-input" />
            </div>

            <div class="form-group">
              <label>Tipo de Documento *</label>
              <select v-model="form.document_type" required class="premium-input">
                <option value="CC">Cédula de Ciudadanía</option>
                <option value="NIT">NIT</option>
                <option value="CE">Cédula de Extranjería</option>
                <option value="PASAPORTE">Pasaporte</option>
              </select>
            </div>

            <div class="form-group">
              <label>Número de Documento / NIT *</label>
              <div class="nit-group">
                <input v-model="form.document_number" type="text" required placeholder="123456789" class="premium-input" />
                <span v-if="form.document_type === 'NIT'" class="dv-separator">-</span>
                <input v-if="form.document_type === 'NIT'" v-model="form.dv" type="text" maxlength="1" placeholder="DV" class="premium-input dv-input" />
              </div>
            </div>

            <div class="form-group">
              <label>Tipo de Socio *</label>
              <select v-model="form.partner_type" required class="premium-input">
                <option value="CUSTOMER">Cliente</option>
                <option value="SUPPLIER">Proveedor</option>
                <option value="BOTH">Ambos</option>
              </select>
            </div>

            <div class="form-group">
              <label>Responsabilidad Fiscal *</label>
              <select v-model="form.responsibility_fiscal" required class="premium-input">
                <option value="NO RESPONSABLE">No Responsable</option>
                <option value="RESPONSABLE IVA">Responsable de IVA</option>
                <option value="AGENTE RETENEDOR">Agente Retenedor</option>
              </select>
            </div>
          </div>
        </div>

        <div class="card-section mt-4">
          <h3 class="section-title"><i class="fas fa-address-book"></i> Información de Contacto</h3>
          <div class="form-grid">
            <div class="form-group">
              <label>Teléfono</label>
              <input v-model="form.phone" type="text" placeholder="Ej: +57 300 123 4567" class="premium-input" />
            </div>

            <div class="form-group">
              <label>Email</label>
              <input v-model="form.email" type="email" placeholder="correo@ejemplo.com" class="premium-input" />
            </div>

            <div class="form-group full-width">
              <label>Dirección</label>
              <input v-model="form.address" type="text" placeholder="Dirección completa" class="premium-input" />
            </div>
          </div>
        </div>

        <div class="form-actions mt-5">
          <button type="button" class="btn btn-secondary-outline" @click="goBack">Cancelar</button>
          <button type="submit" class="btn btn-primary-gradient" :disabled="loading">
            <span v-if="loading"><i class="fas fa-spinner fa-spin mr-2"></i> Guardando...</span>
            <span v-else><i class="fas fa-save mr-2"></i> {{ isEditing ? 'Actualizar Registro' : 'Registrar Cliente' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'PartnerFormView',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    const companyId = computed(() => store.getters['company/selectedCompanyId'])
    
    const isEditing = computed(() => !!route.params.id)
    const loading = ref(false)

    const form = ref({
      name: '',
      document_type: 'CC',
      document_number: '',
      dv: '',
      partner_type: 'CUSTOMER',
      responsibility_fiscal: 'NO RESPONSABLE',
      email: '',
      phone: '',
      address: '',
      is_active: true
    })

    const goBack = () => {
      const redirect = route.query.redirect
      if (redirect) {
        router.push(redirect)
      } else {
        router.back()
      }
    }

    const fetchPartner = async () => {
      if (!isEditing.value) return
      loading.value = true
      try {
        // Assume there's a fetchPartner action or we find it in the list
        const partners = store.getters['partners/getPartners']
        const partner = partners.find(p => p.id === parseInt(route.params.id))
        if (partner) {
          form.value = { ...partner }
          // If nit contains DV in document_number, split it or handle it
          // Based on PartnersView.vue, nit and dv are separate
          form.value.document_number = partner.nit || partner.document_number
          form.value.dv = partner.dv || ''
        } else {
          // Fetch from API if not in store
          const res = await store.dispatch('partners/fetchPartner', { 
            partnerId: route.params.id,
            companyId: companyId.value 
          })
          const p = res.data || res
          form.value = { ...p }
          form.value.document_number = p.nit || p.document_number
        }
      } catch (err) {
        console.error('Error fetching partner:', err)
        alert('No se pudo cargar la información del socio')
        router.push('/partners')
      } finally {
        loading.value = false
      }
    }

    const savePartner = async () => {
      if (!form.value.name || !form.value.document_number) {
        alert('Por favor complete los campos obligatorios')
        return
      }

      if (form.value.document_type === 'NIT' && !form.value.dv) {
        alert('Para NIT debe ingresar el Dígito de Verificación (DV)')
        return
      }

      loading.value = true
      try {
        const payload = {
          name: form.value.name,
          partner_type: form.value.partner_type,
          responsibility_fiscal: form.value.responsibility_fiscal,
          nit: form.value.document_number,
          dv: form.value.dv || null,
          email: form.value.email || null,
          phone: form.value.phone || null,
          address: form.value.address || null,
          is_active: form.value.is_active
        }

        if (isEditing.value) {
          await store.dispatch('partners/updatePartner', {
            partnerId: route.params.id,
            partnerData: payload,
            companyId: companyId.value
          })
        } else {
          const res = await store.dispatch('partners/createPartner', {
            partnerData: payload,
            companyId: companyId.value
          })
          
          // If we came from repair or invoicing, we might want to store the new ID to select it
          if (route.query.redirect === '/repair' || route.query.redirect === '/invoicing') {
            sessionStorage.setItem('lastCreatedPartnerId', res.data.id)
          }
        }
        
        goBack()
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al guardar el registro')
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchPartner()
      
      if (route.query.fromPdf) {
        const draft = sessionStorage.getItem('draftPdfPartnerData')
        if (draft) {
          try {
            const parsed = JSON.parse(draft)
            form.value.name = parsed.name || ''
            form.value.document_number = parsed.nit || ''
            form.value.document_type = 'NIT'
            form.value.partner_type = 'SUPPLIER'
            if (parsed.email && parsed.email !== 'null') form.value.email = parsed.email
            if (parsed.phone && parsed.phone !== 'null') form.value.phone = parsed.phone
            if (parsed.address && parsed.address !== 'null') form.value.address = parsed.address
          } catch(e) {
            console.error('Error parsing draftPdfPartnerData', e)
          }
          sessionStorage.removeItem('draftPdfPartnerData')
        }
      }
    })

    return {
      form,
      isEditing,
      loading,
      goBack,
      savePartner
    }
  }
}
</script>

<style scoped>
.partner-form-view {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.btn-back {
  background: white;
  border: 1px solid #e2e8f0;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: #64748b;
}

.btn-back:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #0f172a;
  transform: translateX(-3px);
}

.premium-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  padding: 2.5rem;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-title i {
  color: #3b82f6;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group.full-width {
  grid-column: span 2;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.premium-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.2s;
  background: #f8fafc;
}

.premium-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.nit-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dv-separator {
  color: #94a3b8;
  font-weight: bold;
}

.dv-input {
  width: 60px;
  text-align: center;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 2rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-secondary-outline {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #64748b;
}

.btn-secondary-outline:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.btn-primary-gradient {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.btn-primary-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.btn-primary-gradient:active {
  transform: translateY(0);
}

.btn-primary-gradient:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .form-group.full-width {
    grid-column: span 1;
  }
  .premium-card {
    padding: 1.5rem;
  }
}
</style>
