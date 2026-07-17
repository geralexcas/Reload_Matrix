<template>
  <div class="repair-view">
    <!-- View A: Historial de Reparaciones -->
    <div v-if="!showCreateModal">
      <div class="view-header">
        <h2>Módulo de Reparación</h2>
        <button class="btn btn-primary" @click="openCreateModal">+ Nueva Orden</button>
      </div>

      <!-- Barra de búsqueda -->
      <div class="search-bar-wrapper">
        <div class="search-input-group">
          <i class="fas fa-search search-icon"></i>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="Buscar por nombre de cliente o número de serie..."
          />
          <button v-if="searchQuery" class="search-clear-btn" @click="searchQuery = ''" title="Limpiar búsqueda">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <span v-if="searchQuery" class="search-results-info">
          {{ filteredOrders.length }} resultado{{ filteredOrders.length !== 1 ? 's' : '' }} encontrado{{ filteredOrders.length !== 1 ? 's' : '' }}
        </span>
      </div>

      <div v-if="loading" class="loading">
        <i class="fas fa-spinner fa-spin mr-1"></i> Cargando órdenes...
      </div>
      <div v-else>
        <table class="data-table" v-if="filteredOrders.length">
          <thead>
            <tr>
              <th>Orden</th>
              <th>Cliente</th>
              <th>Serial</th>
              <th>Estado</th>
              <th class="text-right">Total</th>
              <th class="text-center">Garantía</th>
              <th>Fecha</th>
              <th class="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in filteredOrders" :key="order.id">
              <td class="font-weight-bold">{{ order.order_number }}</td>
              <td>
                <span v-html="highlightMatch(order.partner?.name || `Cliente #${order.partner_id}`, searchQuery)"></span>
              </td>
              <td class="serial-cell">
                <span v-if="order.items?.[0]?.serial_number" v-html="highlightMatch(order.items[0].serial_number, searchQuery)"></span>
                <span v-else class="text-muted">—</span>
              </td>
              <td>
                <span :class="['badge', `badge-${(order.status || 'received').toLowerCase().replace(' ', '_')}`]">
                  {{ order.status || 'RECIBIDO' }}
                </span>
              </td>
              <td class="text-right">${{ Number(order.total_amount || 0).toLocaleString() }}</td>
              <td class="text-center">
                <span v-if="order.warranty_applied" class="text-success"><i class="fas fa-check-circle"></i> Sí</span>
                <span v-else class="text-muted">No</span>
              </td>
              <td>{{ new Date(order.issue_date).toLocaleDateString() }}</td>
              <td class="text-center">
                <button class="btn btn-sm btn-outline-secondary" @click="viewOrder(order)">
                  <i class="fas fa-eye"></i> Ver
                </button>
                <button v-if="order.status !== 'CANCELLED'" class="btn btn-sm btn-outline-danger ml-1" @click="confirmCancelOrder(order)">
                  <i class="fas fa-ban"></i> Anular
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <!-- Back to top button - appears when list is long -->
        <button v-if="filteredOrders.length > 10" @click="scrollToTop" class="btn-back-to-top" title="Volver arriba">
          <i class="fas fa-arrow-up"></i>
          <span class="btn-tooltip">Volver arriba</span>
        </button>
        <div v-else class="empty-state">
          <i class="fas fa-search fa-2x mb-3"></i>
          <p v-if="searchQuery">No se encontraron órdenes para <strong>"{{ searchQuery }}"</strong>.</p>
          <p v-else>No hay órdenes de reparación.</p>
        </div>
      </div>
    </div>

    <!-- View B: Crear Orden -->
    <div v-else class="repair-create-view">
      <div class="view-header mb-4">
        <h2>Nueva Orden de Reparación</h2>
        <button class="btn btn-secondary" @click="closeCreateModal">
          <i class="fas fa-arrow-left mr-1"></i> Volver al Historial
        </button>
      </div>

      <form @submit.prevent="createOrder" class="repair-grid">
        <!-- Tarjeta: Datos del Cliente y Técnico -->
        <div class="card p-4 mb-4">
          <h3 class="card-title">Información del Cliente y Técnico</h3>
          <div class="form-row align-items-end">
            <div class="form-group mb-0 flex-grow-1">
              <label>Cliente *</label>
              <div class="d-flex align-items-center">
                <select v-model="form.partner_id" required class="form-control form-control-lg">
                  <option value="">Buscar cliente...</option>
                  <option v-for="partner in partners" :key="partner.id" :value="partner.id">
                    {{ partner.name }}
                  </option>
                </select>
                <div class="ml-3">
                  <button type="button" class="btn btn-outline-primary pt-2 pb-2 pl-4 pr-4" @click="goToNewPartner">
                    <i class="fas fa-user-plus"></i> + Nuevo
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="form-row mt-3">
            <div class="form-group mb-0 flex-grow-1" style="max-width: 400px;">
              <label>Técnico Asignado:</label>
              <select v-model="form.technician_id" class="form-control">
                <option value="">Sin asignar</option>
                <option v-for="tech in technicians" :key="tech.id" :value="tech.id">
                  {{ tech.first_name }} {{ tech.last_name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Tarjeta: Información del Dispositivo -->
        <div class="card p-4 mb-4 bg-light">
          <h3 class="card-title">Información del Dispositivo</h3>
          <div class="form-row-grid">
            <div class="form-group mb-0">
              <label>Tipo de Dispositivo:</label>
              <div class="d-flex align-items-center">
                <select v-model="form.device_type" class="form-control">
                  <option v-for="type in deviceTypes" :key="type" :value="type">{{ type }}</option>
                </select>
                <button type="button" class="btn btn-sm btn-outline-primary ml-2" @click="showDeviceTypeModal = true">
                  <i class="fas fa-plus"></i>
                </button>
              </div>
            </div>
            <div class="form-group mb-0">
              <label>Marca:</label>
              <input v-model="form.brand" type="text" class="form-control" placeholder="Ej: Samsung, Apple" />
            </div>
          </div>
          <div class="form-row-grid mt-3">
            <div class="form-group mb-0">
              <label>Modelo:</label>
              <input v-model="form.model" type="text" class="form-control" placeholder="Modelo del dispositivo" />
            </div>
            <div class="form-group mb-0">
              <label>Número de Serie / IMEI:</label>
              <input v-model="form.serial_number" type="text" class="form-control" placeholder="IMEI o SN" />
            </div>
          </div>
        </div>

        <!-- Tarjeta: Detalles de la Reparación -->
        <div class="card p-4 mb-4">
          <h3 class="card-title">Detalles de la Reparación</h3>

          <div class="form-group">
            <label>
              Descripción del Problema *
              <span class="field-badge print-badge">🖨️ Se imprime</span>
            </label>
            <textarea v-model="form.description" rows="3" required class="form-control" placeholder="Describa el problema del dispositivo reportado por el cliente"></textarea>
          </div>

          <div class="form-row-grid">
            <div class="form-group mb-0">
              <label>
                Accesorios Recibidos
                <span class="field-badge print-badge">🖨️ Se imprime</span>
              </label>
              <textarea v-model="form.accessories" rows="2" class="form-control" placeholder="Ej: Cargador, cable USB, estuche, memoria..."></textarea>
            </div>
            <div class="form-group mb-0">
              <label>
                Estado Físico del Equipo
                <span class="field-badge print-badge">🖨️ Se imprime</span>
              </label>
              <textarea v-model="form.physical_condition" rows="2" class="form-control" placeholder="Ej: Pantalla rayada, tapa trasera rota..."></textarea>
            </div>
          </div>

          <div class="form-group mt-3">
            <label>
              Diagnóstico Técnico Inicial
              <span class="field-badge internal-badge">🔒 Uso interno</span>
            </label>
            <textarea v-model="form.notes" rows="2" class="form-control" placeholder="Observaciones iniciales del técnico (no se imprime en la orden del cliente)"></textarea>
          </div>

          <div class="mt-3">
            <label class="checkbox-label p-2 bg-light rounded" style="cursor: pointer; border: 1px solid #eee; display: inline-flex; align-items: center; gap: 8px;">
              <input type="checkbox" v-model="form.warranty_applied" />
              <span>✅ Aplicar garantía</span>
            </label>
          </div>
        </div>

        <!-- Botones Finales -->
        <div class="action-buttons mt-4 text-right">
          <button type="button" class="btn btn-secondary mr-2" @click="closeCreateModal">Cancelar</button>
          <button type="submit" class="btn btn-success btn-lg px-5 shadow-sm" :disabled="creating">
            <span v-if="creating">
              <i class="fas fa-spinner fa-spin mr-1"></i> Procesando...
            </span>
            <span v-else>
              <i class="fas fa-save mr-1"></i> Crear Orden de Reparación
            </span>
          </button>
        </div>
      </form>
    </div>


    <!-- Create Device Type Modal -->
    <div v-if="showDeviceTypeModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Nuevo Tipo de Dispositivo</h3>
          <button class="close-btn" @click="showDeviceTypeModal = false">×</button>
        </div>
        <form @submit.prevent="addDeviceType" class="modal-body">
          <div class="form-group">
            <label>Nombre del Tipo *</label>
            <input v-model="newDeviceType" type="text" required placeholder="Ej: Impresora, Consola, etc." />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeviceTypeModal = false">Cancelar</button>
            <button type="submit" class="btn btn-primary">Agregar</button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Order Modal -->
    <div v-if="showOrderModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Orden de Reparación</h3>
          <button class="close-btn" @click="closeOrderModal">×</button>
        </div>
        <div class="modal-body" v-if="selectedOrder">
          <div class="detail-row">
            <span class="detail-label">Orden:</span>
            <span class="detail-value">{{ selectedOrder.order_number }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Estado:</span>
            <span :class="['badge', `badge-${selectedOrder.status?.toLowerCase().replace('_', '')}`]">
              {{ selectedOrder.status }}
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Cliente:</span>
            <span class="detail-value">{{ selectedOrder.partner?.name || `Cliente #${selectedOrder.partner_id}` }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Técnico:</span>
            <span class="detail-value">{{ selectedOrder.technician_id || 'Sin asignar' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Fecha de ingreso:</span>
            <span class="detail-value">{{ new Date(selectedOrder.issue_date).toLocaleString() }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Problema:</span>
            <span class="detail-value">{{ selectedOrder.problem_description || selectedOrder.description || 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Notas de servicio:</span>
            <span class="detail-value">{{ selectedOrder.service_notes || 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Garantía:</span>
            <span class="detail-value">{{ selectedOrder.warranty_applied ? 'Aplicada' : 'No aplicada' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Total:</span>
            <span class="detail-value">${{ Number(selectedOrder.total_amount || 0).toLocaleString() }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeOrderModal">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'RepairView',
  setup() {
    const store = useStore()
    const router = useRouter()
    const companyId = computed(() => store.getters['company/selectedCompanyId'])

    const orders = ref([])
    const partners = ref([])
    const loading = ref(true)
    const creating = ref(false)
    const showCreateModal = ref(false)
    const showOrderModal = ref(false)
    const selectedOrder = ref(null)
    const showDeviceTypeModal = ref(false)
    const newDeviceType = ref('')
    const searchQuery = ref('')

    const filteredOrders = computed(() => {
      const q = (searchQuery.value || '').trim().toLowerCase()
      const safeOrders = Array.isArray(orders.value) ? orders.value : []
      if (!q) return safeOrders
      return safeOrders.filter(order => {
        const clientName = (order.partner?.name || '').toLowerCase()
        const serial = (order.items?.[0]?.serial_number || '').toLowerCase()
        return clientName.includes(q) || serial.includes(q)
      })
    })

    const highlightMatch = (text, query) => {
      if (!text || typeof query !== 'string' || !query.trim()) return text
      const escaped = query.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const regex = new RegExp(`(${escaped})`, 'gi')
      return String(text).replace(regex, '<mark class="search-highlight">$1</mark>')
    }
    const technicians = computed(() => store.getters['repair/technicians'])

    const deviceTypes = ref([
      'CELULAR', 'TABLET', 'LAPTOP', 'ESCRITORIO', 'IMPRESORA', 'AUDIO', 'RELOJ', 'CAMARA', 'OTRO'
    ])

    const form = ref({
      order_number: '',
      issue_date: new Date().toISOString(),
      partner_id: '',
      technician_id: '',
      description: '',
      device_type: 'CELULAR',
      brand: '',
      model: '',
      serial_number: '',
      accessories: '',
      physical_condition: '',
      warranty_applied: false,
      notes: ''
    })

    const fetchOrders = async () => {
      if (!companyId.value) return
      loading.value = true
      try {
        const res = await store.dispatch('repair/fetchOrders', {
          company_id: companyId.value
        })
        orders.value = Array.isArray(res.data) ? res.data : (Array.isArray(res) ? res : [])
      } catch (err) {
        console.error('Error loading orders:', err)
      } finally {
        loading.value = false
      }
    }

    const fetchPartners = async () => {
      if (!companyId.value) {
        console.warn('No company ID available')
        return
      }
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
      const cid = companyId.value
      if (!cid) return
      try {
        await store.dispatch('repair/fetchTechnicians', {
          company_id: cid
        })
      } catch (err) {
        console.error('Error loading technicians:', err)
      }
    }

    const openCreateModal = () => {
      showCreateModal.value = true
      fetchPartners()
      fetchTechnicians()

      // Recover form if exists
      const savedForm = sessionStorage.getItem('repairFormCache')
      if (savedForm) {
        form.value = JSON.parse(savedForm)
        sessionStorage.removeItem('repairFormCache')
      }

      // Select last created partner if return from new partner page
      const lastPartnerId = sessionStorage.getItem('lastCreatedPartnerId')
      if (lastPartnerId) {
        form.value.partner_id = parseInt(lastPartnerId)
        sessionStorage.removeItem('lastCreatedPartnerId')
      }
    }

    const closeCreateModal = () => {
      showCreateModal.value = false
      form.value = {
        order_number: '',
        issue_date: new Date().toISOString(),
        partner_id: '',
        technician_id: '',
        description: '',
        device_type: 'CELULAR',
        brand: '',
        model: '',
        serial_number: '',
        accessories: '',
        physical_condition: '',
        warranty_applied: false,
        notes: ''
      }
    }

    const goToNewPartner = () => {
      // Save current form state
      sessionStorage.setItem('repairFormCache', JSON.stringify(form.value))
      router.push({
        name: 'partner-new',
        query: { redirect: '/repair' }
      })
    }

    const addDeviceType = () => {
      if (!newDeviceType.value) return
      const upperType = newDeviceType.value.toUpperCase()
      if (!deviceTypes.value.includes(upperType)) {
        deviceTypes.value.push(upperType)
      }
      form.value.device_type = upperType
      newDeviceType.value = ''
      showDeviceTypeModal.value = false
    }

    const createOrder = async () => {
      if (!form.value.partner_id || !form.value.description) {
        alert('Por favor complete los campos requeridos')
        return
      }

      const orderData = {
        order_number: form.value.order_number || `REP-${Date.now()}`,
        partner_id: form.value.partner_id,
        technician_id: form.value.technician_id || null,
        issue_date: form.value.issue_date || new Date().toISOString(),
        problem_description: form.value.description,
        service_notes: form.value.accessories || '',
        diagnosis: form.value.physical_condition || form.value.notes || '',
        warranty_applied: form.value.warranty_applied,
        status: 'RECEIVED',
        total_amount: 0,
        total_labor_cost: 0,
        total_parts_cost: 0,
        device_type: form.value.device_type,
        brand: form.value.brand,
        model: form.value.model,
        serial_number: form.value.serial_number
      }

      creating.value = true
      try {
        await store.dispatch('repair/createOrder', {
          orderData,
          company_id: companyId.value
        })
        closeCreateModal()
        fetchOrders()
      } catch (err) {
        console.error('Error creating order:', err)
        alert(err.response?.data?.detail || 'Error al crear la orden')
      } finally {
        creating.value = false
      }
    }

    const viewOrder = (order) => {
      router.push(`/repair/${order.id}`)
    }

    const confirmCancelOrder = async (order) => {
      const message = order.invoice_id 
        ? `¡ADVERTENCIA! Esta orden ya tiene una factura (#${order.invoice_id}). Anular la orden también ANULARÁ la factura, revertirá el inventario y generará reversiones contables. ¿Desea continuar?`
        : '¿Está seguro de anular esta orden de reparación?'
      
      if (!confirm(message)) return

      try {
        await api.post(`/api/v1/repair/${order.id}/cancel`, null, {
          params: { company_id: companyId.value }
        })
        alert('Orden anulada con éxito')
        await fetchOrders()
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al anular la orden')
      }
    }

    const closeOrderModal = () => {
      showOrderModal.value = false
      selectedOrder.value = null
    }

    const scrollToTop = () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    }

    onMounted(() => {
      fetchOrders()
    })

    return {
      orders,
      partners,
      loading,
      creating,
      showCreateModal,
      showDeviceTypeModal,
      showOrderModal,
      selectedOrder,
      deviceTypes,
      form,
      newDeviceType,
      technicians,
      searchQuery,
      filteredOrders,
      highlightMatch,
      scrollToTop,
      openCreateModal,
      closeCreateModal,
      closeOrderModal,
      goToNewPartner,
      addDeviceType,
      createOrder,
      viewOrder,
      confirmCancelOrder
    }
  }
}
</script>

<style scoped>
.repair-view {
  padding: 20px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.view-header h2 {
  margin: 0;
  color: #2c3e50;
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
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.badge-received { background: #cce5ff; color: #004085; }
.badge-diagnosis { background: #fff3cd; color: #856404; }
.badge-approved { background: #d4edda; color: #155724; }
.badge-in_repair { background: #e2e3ff; color: #383d7d; }
.badge-waiting_parts { background: #f8d7da; color: #721c24; }
.badge-ready { background: #d1ecf1; color: #0c5460; }
.badge-delivered { background: #d4edda; color: #155724; }
.badge-cancelled { background: #f5f5f5; color: #666; }

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary { background: #007bff; color: white; }
.btn-primary:hover { background: #0056b3; }

.btn-secondary { background: #6c757d; color: white; }

.btn-outline-danger {
  border: 1px solid #f5222d;
  color: #f5222d;
  background: transparent;
}

.btn-outline-danger:hover {
  background: #f5222d;
  color: white;
}

.btn-small {
  padding: 0.25rem 0.5rem;
  font-size: 12px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.btn-add-small {
  padding: 4px 8px;
  font-size: 14px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 4px;
}

.btn-add-small:hover {
  background: #219a52;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: #666;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow: auto;
}

.modal-lg {
  max-width: 800px;
}

.select-with-add {
  display: flex;
  align-items: center;
}

.select-with-add select {
  flex: 1;
}

.form-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ecf0f1;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 16px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ecf0f1;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 500;
  margin-bottom: 4px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ecf0f1;
  margin-top: 16px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #ecf0f1;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  color: #7f8c8d;
}

.detail-value {
  color: #2c3e50;
  text-align: right;
}

/* Card & Grid Layout Additions */
.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border: 1px solid #eaeaea;
}
.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 1.25rem;
  color: #333;
}
.bg-light { background-color: #f8f9fa !important; }
.mb-0 { margin-bottom: 0 !important; }
.mb-4 { margin-bottom: 1.5rem !important; }
.mt-3 { margin-top: 1rem !important; }
.mt-4 { margin-top: 1.5rem !important; }
.p-4 { padding: 1.5rem !important; }
.mr-2 { margin-right: 0.5rem !important; }
.ml-3 { margin-left: 1rem !important; }
.pr-4 { padding-right: 1.5rem; }
.pl-4 { padding-left: 1.5rem; }
.pr-3 { padding-right: 1rem; }
.pl-3 { padding-left: 1rem; }
.pt-1 { padding-top: 0.25rem; }
.pb-1 { padding-bottom: 0.25rem; }
.pt-2 { padding-top: 0.5rem; }
.pb-2 { padding-bottom: 0.5rem; }
.text-right { text-align: right; }

.form-row-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
  transition: border-color 0.15s;
}
.form-control:focus {
  border-color: #80bdff;
  outline: 0;
}
.form-control-lg {
  padding: 0.75rem 1rem;
  font-size: 1.1rem;
}

.btn-outline-primary {
  color: #007bff;
  border: 1px solid #007bff;
  background: white;
  border-radius: 4px;
}
.btn-outline-primary:hover {
  background: #007bff;
  color: white;
}

.btn-success { background: #28a745; color: white; border: 1px solid #28a745; }
.btn-success:hover { background: #218838; }
.btn-lg { padding: 0.75rem 1.5rem; font-size: 1.1rem; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.8rem; }
.font-weight-bold { font-weight: bold; }
.px-5 { padding-left: 3rem !important; padding-right: 3rem !important; }
.d-flex { display: flex; }
.align-items-center { align-items: center; }
.mr-1 { margin-right: 0.25rem !important; }
.ml-2 { margin-left: 0.5rem !important; }
.flex-grow-1 { flex-grow: 1; }
.shadow-sm { box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075) !important; }

.btn-outline-secondary {
  color: #6c757d;
  border-color: #6c757d;
  background-color: transparent;
}
.btn-outline-secondary:hover {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

/* ---- Búsqueda ---- */
.search-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.search-input-group {
  position: relative;
  flex: 1;
  max-width: 480px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #aab;
  font-size: 14px;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.55rem 2.5rem 0.55rem 2.25rem;
  border: 1.5px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9rem;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0,123,255,0.12);
}

.search-clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1;
}
.search-clear-btn:hover {
  color: #333;
  background: #f0f0f0;
}

.search-results-info {
  font-size: 0.82rem;
  color: #6c757d;
  white-space: nowrap;
}

:deep(.search-highlight) {
  background-color: #fff176;
  color: #333;
  border-radius: 2px;
  padding: 0 2px;
  font-weight: 600;
}

.serial-cell {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  color: #555;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #aaa;
}
.empty-state i {
  display: block;
  margin-bottom: 0.75rem;
}

/* Field badge indicators */
.field-badge {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 20px;
  margin-left: 8px;
  vertical-align: middle;
  letter-spacing: 0.3px;
}
.print-badge {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #a5d6a7;
}
.internal-badge {
  background-color: #fff8e1;
  color: #f57f17;
  border: 1px solid #ffe082;
}

/* Back to top button */
.btn-back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  z-index: 100;
  transition: all 0.3s ease;
  position: relative;
}

.btn-back-to-top:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.btn-back-to-top .btn-tooltip {
  position: absolute;
  left: 100%;
  margin-left: 10px;
  background-color: #333;
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.btn-back-to-top:hover .btn-tooltip {
  opacity: 1;
  visibility: visible;
}
</style>