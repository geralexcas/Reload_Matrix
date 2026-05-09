<template>
  <div class="repair-detail-view">
    <div class="view-header">
      <div class="header-left">
        <button class="btn btn-secondary" @click="goBack">← Volver</button>
        <h2>Orden de Reparación: {{ order?.order_number }}</h2>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="toggleEdit" v-if="!editing">
          ✏️ Editar
        </button>
        <button class="btn btn-primary" @click="saveOrder" v-if="editing" :disabled="saving">
          {{ saving ? 'Guardando...' : '💾 Guardar' }}
        </button>
        <button class="btn btn-success" @click="generateInvoice" v-if="!editing && canGenerateInvoice" :disabled="generating">
          {{ generating ? 'Generando...' : '📄 Generar Factura' }}
        </button>
        <button class="btn btn-primary" @click="showPrintModal = true" v-if="!editing && order">
          🖨️ Imprimir Orden
        </button>
        <button class="btn btn-danger" @click="confirmCancelOrder" v-if="!editing && order?.status !== 'CANCELLED'">
          🚫 Anular Orden
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">Cargando orden...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="detail-content">
      <div class="status-bar">
        <span :class="['badge', `badge-${order?.status?.toLowerCase().replace('_', '')}`]">
          {{ order?.status }}
        </span>
        <span class="warranty-badge" :class="{ active: order?.warranty_applied }">
          {{ order?.warranty_applied ? '🎧 Garantía Aplicada' : 'Sin Garantía' }}
        </span>
      </div>

      <div class="detail-grid">
        <div class="card customer-card">
          <div class="card-header-icon">
            <h3><i class="icon">👤</i> Información del Cliente</h3>
          </div>
          
          <div class="info-group main-info">
            <label>Nombre completo</label>
            <div v-if="!editing" class="info-value name-value">
              {{ displayPartner?.name || `Cliente #${order?.partner_id}` }}
            </div>
            <select v-else v-model="editForm.partner_id" class="edit-select">
              <option v-for="p in partners" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>

          <div class="customer-sub-grid">
            <div class="info-group">
              <label>🆔 Documento / NIT</label>
              <div class="info-value">
                {{ displayPartner?.nit || 'N/A' }}{{ displayPartner?.dv ? `-${displayPartner.dv}` : '' }}
              </div>
            </div>
            <div class="info-group">
              <label>📞 Teléfono</label>
              <div class="info-value">
                {{ displayPartner?.phone || 'N/A' }}
              </div>
            </div>
            <div class="info-group full-width">
              <label>📧 Correo Electrónico</label>
              <div class="info-value email-value">
                {{ displayPartner?.email || 'N/A' }}
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <h3>🔧 Técnico Asignado</h3>
          <div class="info-group">
            <label>Nombre:</label>
            <span v-if="!editing">{{ technicianName }}</span>
            <select v-else v-model="editForm.technician_id">
              <option :value="null">Sin asignar</option>
              <option v-for="t in technicians" :key="t.id" :value="t.id">
                {{ t.first_name }} {{ t.last_name }}
              </option>
            </select>
          </div>
        </div>

        <div class="card">
          <h3>📅 Fechas</h3>
          <div class="info-group">
            <label>Fecha de Ingreso:</label>
            <span>{{ formatDate(order?.issue_date) }}</span>
          </div>
          <div class="info-group">
            <label>Fecha Esperada:</label>
            <span v-if="!editing">{{ formatDate(order?.expected_delivery_date) || 'No definida' }}</span>
            <input v-else type="datetime-local" v-model="editForm.expected_delivery_date" />
          </div>
        </div>

        <div class="card full-width">
          <h3>📝 Descripción del Problema</h3>
          <div class="info-group">
            <span v-if="!editing">{{ order?.problem_description || 'N/A' }}</span>
            <textarea v-else v-model="editForm.problem_description" rows="4"></textarea>
          </div>
        </div>

        <div class="card full-width">
          <h3>📋 Notas de Servicio</h3>
          <div class="info-group">
            <span v-if="!editing">{{ order?.service_notes || 'Sin notas' }}</span>
            <textarea v-else v-model="editForm.service_notes" rows="3"></textarea>
          </div>
        </div>

        <div class="card full-width">
          <div class="card-header">
            <h3>🛠️ Servicios y Repuestos</h3>
            <button class="btn btn-primary btn-sm" @click="showAddItemModal = true" v-if="canAddItems">
              + Agregar
            </button>
          </div>
          <table class="items-table" v-if="order?.items?.length">
            <thead>
              <tr>
                <th>Descripción</th>
                <th>Marca/Modelo</th>
                <th>Serie</th>
                <th>Cant.</th>
                <th>Unitario</th>
                <th>Total</th>
                <th>Garantía</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in order.items" :key="item.id">
                <td>{{ item.description }}</td>
                <td>{{ item.brand }} {{ item.model }}</td>
                <td>{{ item.serial_number || 'N/A' }}</td>
                <td>{{ item.quantity }}</td>
                <td>${{ Number(item.unit_cost).toLocaleString() }}</td>
                <td>${{ Number(item.line_total).toLocaleString() }}</td>
                <td>{{ formatWarranty(item.warranty_days) }}</td>
                <td>
                  <button class="btn btn-sm btn-danger" @click="deleteItem(item.id)" title="Eliminar">🗑️</button>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="5" class="text-right"><strong>Total:</strong></td>
                <td><strong>${{ Number(calculatedTotal).toLocaleString() }}</strong></td>
                <td colspan="2"></td>
              </tr>
            </tfoot>
          </table>
          <p v-else class="empty">No hay servicios o repuestos registrados.</p>
        </div>

        <div class="card">
          <h3>💰 Costos</h3>
          <div class="info-group">
            <label>Mano de Obra:</label>
            <span>${{ Number(totalLabor).toLocaleString() }}</span>
          </div>
          <div class="info-group">
            <label>Repuestos:</label>
            <span>${{ Number(totalParts).toLocaleString() }}</span>
          </div>
          <div class="info-group total">
            <label>Total:</label>
            <span>${{ Number(calculatedTotal).toLocaleString() }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAddItemModal" class="modal-overlay">
      <div class="modal-content modal-lg">
        <div class="modal-header">
          <h3>Agregar Servicio o Repuesto</h3>
          <button class="close-btn" @click="showAddItemModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Tipo de Item</label>
            <select v-model="newItem.type">
              <option value="service">Servicio</option>
              <option value="product">Producto (Repuesto)</option>
            </select>
          </div>
          
          <div v-if="newItem.type === 'product'" class="form-group">
            <label>Producto</label>
            <select v-model="newItem.product_id" @change="onProductSelect">
              <option value="">Seleccionar producto</option>
                <option v-for="p in products" :key="p.id" :value="p.id">
                  {{ p.name }} - ${{ Number(p.sale_price || p.price).toLocaleString() }} (Stock: {{ p.stock_level }})
                </option>
            </select>
          </div>

          <div v-if="newItem.type === 'service'" class="form-group">
            <label>Nombre del Servicio *</label>
            <input v-model="newItem.description" type="text" placeholder="Ej: Cambio de batería" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Marca (opcional)</label>
              <input v-model="newItem.brand" type="text" placeholder="Se autocompletará al seleccionar" />
            </div>
            <div class="form-group">
              <label>Modelo (opcional)</label>
              <input v-model="newItem.model" type="text" placeholder="Se填充ará automáticamente" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Número de Serie (opcional)</label>
              <input v-model="newItem.serial_number" type="text" placeholder="Ingrese si aplica" />
            </div>
            <div class="form-group">
              <label>Cantidad</label>
              <input v-model.number="newItem.quantity" type="number" min="1" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Precio Unitario *</label>
              <input v-model.number="newItem.unit_cost" type="number" min="0" />
            </div>
            <div class="form-group">
              <label>Garantía (días)</label>
              <input v-model.number="newItem.warranty_days" type="number" min="0" placeholder="Dejar vacío sin garantía" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAddItemModal = false">Cancelar</button>
          <button class="btn btn-primary" @click="addItem" :disabled="!canAddItem">Agregar</button>
        </div>
      </div>
    </div>
    
    <!-- POS Payment Modal -->
    <POSPaymentModal
      v-if="showPOS"
      :totalAmount="calculatedTotal"
      @confirm="onPOSConfirm"
      @cancel="showPOS = false"
    />

    <!-- Repair Print Modal -->
    <RepairPrintModal
      v-if="showPrintModal"
      :show="showPrintModal"
      :order="order"
      :partner="displayPartner"
      :company="currentCompany"
      :technicians="technicians"
      @close="showPrintModal = false"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import POSPaymentModal from '@/components/POSPaymentModal.vue'
import RepairPrintModal from '@/components/Repair/RepairPrintModal.vue'

export default {
  name: 'RepairDetailView',
  components: {
    POSPaymentModal,
    RepairPrintModal
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()

    const order = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const editing = ref(false)
    const saving = ref(false)
    const generating = ref(false)
    const partners = ref([])
    const technicians = ref([])
    const products = ref([])
    const showAddItemModal = ref(false)
    const showPOS = ref(false)
    const showPrintModal = ref(false)

    const currentCompany = computed(() => store.getters['company/getCompany'] || {})
    const companyId = computed(() => store.getters['company/selectedCompanyId'])
    const orderId = computed(() => route.params.id)

    const editForm = ref({
      partner_id: null,
      technician_id: null,
      problem_description: '',
      service_notes: '',
      expected_delivery_date: '',
      actual_delivery_date: ''
    })

    const newItem = ref({
      type: 'service',
      product_id: '',
      description: '',
      brand: '',
      model: '',
      serial_number: '',
      quantity: 1,
      unit_cost: 0,
      warranty_days: null,
      issue_reported: ''
    })

    const technicianName = computed(() => {
      if (!order.value?.technician_id || !technicians.value.length) return 'Sin asignar'
      const tech = technicians.value.find(t => t.id === order.value.technician_id)
      return tech ? `${tech.first_name} ${tech.last_name}` : 'Sin asignar'
    })

    const displayPartner = computed(() => {
      const targetId = editing.value ? editForm.value.partner_id : order.value?.partner_id
      if (!targetId) return null
      return partners.value.find(p => Number(p.id) === Number(targetId)) || order.value?.partner
    })

    const canGenerateInvoice = computed(() => {
      // Allow generating invoice as long as the order is not cancelled, has items, and hasn't been invoiced yet
      return order.value && order.value.status !== 'CANCELLED' && order.value.items?.length > 0 && !order.value.invoice_id
    })

    const canAddItems = computed(() => {
      return order.value && !['DELIVERED', 'CANCELLED'].includes(order.value.status)
    })

    const canAddItem = computed(() => {
      if (newItem.value.type === 'service') {
        return newItem.value.description && newItem.value.unit_cost >= 0
      }
      return newItem.value.product_id && newItem.value.unit_cost >= 0
    })

    const totalLabor = computed(() => {
      if (!order.value?.items?.length) return 0
      return order.value.items
        .filter(item => !item.product_id)
        .reduce((sum, item) => sum + (Number(item.line_total) || 0), 0)
    })

    const totalParts = computed(() => {
      if (!order.value?.items?.length) return 0
      return order.value.items
        .filter(item => !!item.product_id)
        .reduce((sum, item) => sum + (Number(item.line_total) || 0), 0)
    })

    const calculatedTotal = computed(() => {
      if (!order.value?.items?.length) return 0
      return order.value.items.reduce((sum, item) => {
        return sum + (Number(item.line_total) || 0)
      }, 0)
    })

    const formatDate = (date) => {
      if (!date) return null
      return new Date(date).toLocaleString()
    }

    const formatWarranty = (days) => {
      if (days && days > 0) return `${days} días`
      return 'Sin Garantía'
    }

    const goBack = () => {
      router.push('/repair')
    }

    const fetchOrder = async () => {
      loading.value = true
      error.value = null
      try {
        const res = await api.get(`/api/v1/repair/${orderId.value}`, {
          params: { company_id: companyId.value }
        })
        order.value = res.data
      } catch (err) {
        error.value = 'Error al cargar la orden'
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    const fetchPartners = async () => {
      try {
        const res = await store.dispatch('partners/fetchPartners', {
          companyId: companyId.value
        })
        partners.value = res.data || res
      } catch (err) {
        console.error('Error loading partners:', err)
      }
    }

    const fetchTechnicians = async () => {
      try {
        const res = await api.get('/api/v1/admin/users/', {
          params: { company_id: companyId.value }
        })
        const techUsers = (res.data || res).filter(u => u.role === 'TECNICO')
        technicians.value = techUsers.map(u => ({
          id: u.id,
          employee_id: `USR${u.id}`,
          first_name: u.full_name?.split(' ')[0] || '',
          last_name: u.full_name?.split(' ').slice(1).join(' ') || '',
          specialty: 'Técnico',
          is_active: u.is_active,
          user_id: u.id
        }))
      } catch (err) {
        console.error('Error loading technicians:', err)
      }
    }

    const fetchProducts = async () => {
      try {
        const res = await api.get('/api/v1/inventory/', {
          params: { company_id: companyId.value, skip: 0, limit: 1000 }
        })
        products.value = res.data || res
      } catch (err) {
        console.error('Error loading products:', err)
      }
    }

    const toggleEdit = async () => {
      if (editing.value) {
        editing.value = false
      } else {
        await fetchTechnicians()
        editForm.value = {
          partner_id: order.value.partner_id,
          technician_id: order.value.technician_id,
          problem_description: order.value.problem_description || '',
          service_notes: order.value.service_notes || '',
          expected_delivery_date: order.value.expected_delivery_date ? new Date(order.value.expected_delivery_date).toISOString().slice(0, 16) : '',
          actual_delivery_date: order.value.actual_delivery_date ? new Date(order.value.actual_delivery_date).toISOString().slice(0, 16) : ''
        }
        editing.value = true
      }
    }

    const saveOrder = async () => {
      saving.value = true
      try {
        const data = {
          ...editForm.value,
          issue_date: order.value.issue_date,
          status: order.value.status,
          warranty_applied: order.value.warranty_applied,
          total_amount: order.value.total_amount,
          total_labor_cost: order.value.total_labor_cost,
          total_parts_cost: order.value.total_parts_cost
        }
        
        if (editForm.value.expected_delivery_date) {
          data.expected_delivery_date = new Date(editForm.value.expected_delivery_date).toISOString()
        }
        if (editForm.value.actual_delivery_date) {
          data.actual_delivery_date = new Date(editForm.value.actual_delivery_date).toISOString()
        }

        await api.put(`/api/v1/repair/${orderId.value}`, data, {
          params: { company_id: companyId.value }
        })
        
        await fetchOrder()
        editing.value = false
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al guardar')
      } finally {
        saving.value = false
      }
    }

    const generateInvoice = () => {
      showPOS.value = true
    }

    const onPOSConfirm = async (paymentData) => {
      generating.value = true
      try {
        await store.dispatch('repair/generateInvoice', {
          orderId: orderId.value,
          company_id: companyId.value,
          paymentData: {
             is_paid: paymentData.is_paid,
             payment_method: paymentData.payment_method,
             amount_paid: paymentData.amount_paid,
             payment_account_type: paymentData.payment_account_type,
             payment_account_id: paymentData.payment_account_id,
             reference: paymentData.reference
          }
        })
        showPOS.value = false
        await fetchOrder()
        alert('Factura y pago generados exitosamente')
      } catch (err) {
        showPOS.value = false
        alert(err.response?.data?.detail || 'Error al generar factura')
      } finally {
        generating.value = false
      }
    }

    const onProductSelect = () => {
      const product = products.value.find(p => p.id === newItem.value.product_id)
      if (product) {
        newItem.value.description = product.name
        newItem.value.brand = product.brand || ''
        newItem.value.model = product.model || ''
        newItem.value.unit_cost = product.sale_price || product.price || 0
      }
    }

    const addItem = async () => {
      try {
        const unitCost = Number(newItem.value.unit_cost) || 0
        const qty = Number(newItem.value.quantity) || 1
        const warrantyDays = newItem.value.warranty_days ? Number(newItem.value.warranty_days) : null
        
        const itemData = {
          description: newItem.value.description,
          brand: newItem.value.brand || '',
          model: newItem.value.model || '',
          serial_number: newItem.value.serial_number || '',
          quantity: qty,
          unit_cost: unitCost,
          discount: 0,
          tax_rate: 0,
          tax_amount: 0,
          line_total: qty * unitCost,
          warranty_status: warrantyDays ? 'IN_WARRANTY' : 'NO_WARRANTY',
          warranty_days: warrantyDays,
          issue_reported: newItem.value.issue_reported || '',
          product_id: newItem.value.type === 'product' ? newItem.value.product_id : null
        }

        await api.post(`/api/v1/repair/${orderId.value}/items/`, itemData, {
          params: { company_id: companyId.value }
        })

        await fetchOrder()
        showAddItemModal.value = false
        newItem.value = {
          type: 'service',
          product_id: '',
          description: '',
          brand: '',
          model: '',
          serial_number: '',
          quantity: 1,
          unit_cost: 0,
          warranty_days: null,
          issue_reported: ''
        }
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al agregar item')
      }
    }

    const deleteItem = async (itemId) => {
      if (!confirm('¿Está seguro de eliminar este servicio?')) return
      try {
        await api.delete(`/api/v1/repair/${orderId.value}/items/${itemId}`, {
          params: { company_id: companyId.value }
        })
        await fetchOrder()
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al eliminar item')
      }
    }

    const confirmCancelOrder = async () => {
      const message = order.value.invoice_id 
        ? `¡ADVERTENCIA! Esta orden ya tiene una factura (#${order.value.invoice_id}). Anular la orden también ANULARÁ la factura, revertirá el inventario y generará reversiones contables. ¿Desea continuar?`
        : '¿Está seguro de anular esta orden de reparación?'
      
      if (!confirm(message)) return

      try {
        await api.post(`/api/v1/repair/${orderId.value}/cancel`, null, {
          params: { company_id: companyId.value }
        })
        alert('Orden anulada con éxito')
        await fetchOrder()
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al anular la orden')
      }
    }

    onMounted(async () => {
      await Promise.all([
        fetchOrder(),
        fetchPartners(),
        fetchTechnicians(),
        fetchProducts(),
        store.dispatch('company/fetchCompany', companyId.value)
      ])
    })

    return {
      order,
      loading,
      error,
      editing,
      saving,
      generating,
      editForm,
      partners,
      technicians,
      products,
      showAddItemModal,
      newItem,
      technicianName,
      displayPartner,
      totalLabor,
      totalParts,
      canGenerateInvoice,
      canAddItems,
      canAddItem,
      calculatedTotal,
      formatDate,
      formatWarranty,
      goBack,
      toggleEdit,
      saveOrder,
      generateInvoice,
      onPOSConfirm,
      showPOS,
      onProductSelect,
      addItem,
      deleteItem,
      confirmCancelOrder,
      showPrintModal,
      currentCompany
    }
  }
}
</script>

<style scoped>
.repair-detail-view { padding: 20px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 16px; }
.header-left h2 { margin: 0; color: #2c3e50; }
.header-actions { display: flex; gap: 12px; }
.status-bar { display: flex; gap: 12px; margin-bottom: 20px; }
.warranty-badge { padding: 4px 12px; border-radius: 4px; background: #f8f9fa; color: #666; font-size: 14px; }
.warranty-badge.active { background: #d4edda; color: #155724; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.card.full-width { grid-column: 1 / -1; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.card h3 { margin: 0 0 16px 0; color: #2c3e50; font-size: 16px; }
.info-group { margin-bottom: 12px; }
.info-group label { display: block; font-size: 12px; color: #7f8c8d; margin-bottom: 4px; }
.info-group span { color: #2c3e50; }
.info-group.total { margin-top: 16px; padding-top: 12px; border-top: 1px solid #eee; }
.info-group.total span { font-size: 18px; font-weight: bold; color: #007bff; }
.info-group input, .info-group select, .info-group textarea { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.items-table { width: 100%; border-collapse: collapse; }
.items-table th, .items-table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
.items-table th { background: #f8f9fa; font-weight: 600; }
.items-table .text-right { text-align: right; }
.items-table tfoot td { font-weight: bold; background: #f8f9fa; }
.empty { text-align: center; color: #666; padding: 20px; }
.btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-success { background: #28a745; color: white; }
.btn-danger { background: #dc3545; color: white; }
.btn-sm { padding: 4px 12px; font-size: 12px; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.loading, .error { text-align: center; padding: 40px; color: #666; }
.error { color: #dc3545; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; border-radius: 8px; width: 90%; max-width: 600px; max-height: 90vh; overflow: auto; }
.modal-lg { max-width: 700px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #ecf0f1; }
.modal-header h3 { margin: 0; }
.close-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #7f8c8d; }
.modal-body { padding: 20px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; padding: 16px 20px; border-top: 1px solid #ecf0f1; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 12px; color: #7f8c8d; margin-bottom: 4px; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.badge { padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 500; text-transform: uppercase; }
.badge-received { background: #cce5ff; color: #004085; }
.badge-diagnosis { background: #fff3cd; color: #856404; }
.badge-approved { background: #d4edda; color: #155724; }
.badge-in_repair { background: #e2e3ff; color: #383d7d; }
.badge-waiting_parts { background: #f8d7da; color: #721c24; }
.badge-ready { background: #d1ecf1; color: #0c5460; }
.badge-delivered { background: #d4edda; color: #155724; }
.badge-cancelled { background: #f5f5f5; color: #666; }

/* Enhanced Customer Card Styles */
.customer-card {
  border-top: 4px solid #3498db;
  transition: all 0.3s ease;
}
.customer-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.card-header-icon h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2c3e50;
  font-weight: 700;
  margin-bottom: 20px;
}
.main-info {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid #3498db;
  margin-bottom: 16px;
}
.name-value {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}
.customer-sub-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.full-width {
  grid-column: 1 / -1;
}
.info-value {
  font-size: 14px;
  color: #34495e;
  font-weight: 500;
  padding: 4px 0;
}
.email-value {
  color: #3498db;
  text-decoration: none;
}
.edit-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background-color: #fff;
  transition: border-color 0.2s;
  font-size: 15px;
}
.edit-select:focus {
  border-color: #3498db;
  outline: none;
}
</style>
