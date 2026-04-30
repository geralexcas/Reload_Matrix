<template>
  <div class="purchases-container">
    <div class="page-header">
      <h1 class="page-title">Compras</h1>
      <button class="btn btn-primary" @click="$router.push('/purchases/new')">
        <span class="btn-icon">+</span>
        Nueva Compra
      </button>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total Compras</div>
        <div class="stat-value">{{ statistics?.total_purchases || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Monto Total</div>
        <div class="stat-value">${{ formatNumber(statistics?.total_amount || 0) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Pagado</div>
        <div class="stat-value">${{ formatNumber(statistics?.paid_amount || 0) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Pendiente</div>
        <div class="stat-value">${{ formatNumber(statistics?.pending_amount || 0) }}</div>
      </div>
    </div>

    <div class="filters-card">
      <div class="filter-row">
        <div class="filter-group search-group">
          <label>Buscar</label>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Número de compra o proveedor..."
            class="search-input"
          >
        </div>
        <div class="filter-group">
          <label>Estado</label>
          <select v-model="filters.status" @change="fetchPurchasesList">
            <option value="">Todos</option>
            <option value="DRAFT">Borrador</option>
            <option value="ISSUED">Emitida</option>
            <option value="PAID">Pagada</option>
            <option value="PARTIAL">Parcial</option>
            <option value="OVERDUE">Vencida</option>
            <option value="CANCELLED">Cancelada</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Proveedor</label>
          <select v-model="filters.partnerId" @change="fetchPurchasesList">
            <option value="">Todos</option>
            <option v-for="partner in partners" :key="partner.id" :value="partner.id">
              {{ partner.name }}
            </option>
          </select>
        </div>
        <button class="btn btn-secondary" @click="clearFilters">Limpiar</button>
      </div>
    </div>

    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Número</th>
            <th>Fecha</th>
            <th>Proveedor</th>
            <th>Método de Pago</th>
            <th>Estado</th>
            <th>Total</th>
            <th>Saldo</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="purchase in filteredPurchases" :key="purchase.id">
            <td>{{ purchase.purchase_number }}</td>
            <td>{{ formatDate(purchase.purchase_date) }}</td>
            <td>{{ purchase.partner?.name || 'N/A' }}</td>
            <td>
              <span class="badge badge-info">{{ purchase.payment_method }}</span>
            </td>
            <td>
              <span :class="['badge', getStatusClass(purchase.status)]">
                {{ purchase.status }}
              </span>
            </td>
            <td>${{ formatNumber(purchase.total_amount) }}</td>
            <td>${{ formatNumber(getBalance(purchase)) }}</td>
            <td>
              <div class="action-buttons">
                <button class="btn-icon-action" @click="viewPurchase(purchase)" title="Ver">
                  👁️
                </button>
                <button 
                  v-if="purchase.status !== 'PAID' && purchase.status !== 'CANCELLED' && getBalance(purchase) > 0"
                  class="btn-icon-action" 
                  @click="openPaymentModal(purchase)" 
                  title="Pagar"
                >
                  💰
                </button>
                <button 
                  v-if="purchase.status === 'DRAFT' || purchase.status === 'ISSUED'"
                  class="btn-icon-action" 
                  @click="editPurchase(purchase)" 
                  title="Editar"
                >
                  ✏️
                </button>
                <button 
                  v-if="purchase.status !== 'CANCELLED'"
                  class="btn-icon-action" 
                  @click="confirmCancel(purchase)" 
                  title="Anular"
                >
                  🚫
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="purchases.length === 0 && !loading">
            <td colspan="8" class="empty-message">No hay compras registradas</td>
          </tr>
        </tbody>
      </table>
      <div v-if="loading" class="loading-spinner">Cargando...</div>
    </div>

    <PaymentModal
      v-if="showPaymentModal"
      :purchase="selectedPurchase"
      @close="showPaymentModal = false"
      @paid="onPaymentRegistered"
    />

    <PurchaseDetailModal
      v-if="showDetailModal"
      :purchase="selectedPurchase"
      @close="showDetailModal = false"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import PaymentModal from './PaymentModal.vue'
import PurchaseDetailModal from './PurchaseDetailModal.vue'

export default {
  name: 'PurchasesIndexView',
  components: {
    PaymentModal,
    PurchaseDetailModal
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const companyId = computed(() => store.getters['company/selectedCompanyId'])

    const purchases = ref([])
    const partners = ref([])
    const statistics = ref(null)
    const loading = ref(false)

    const showPaymentModal = ref(false)
    const showDetailModal = ref(false)
    const selectedPurchase = ref(null)

    const filters = ref({
      status: '',
      partnerId: ''
    })
    const searchQuery = ref('')

    const filteredPurchases = computed(() => {
      if (!searchQuery.value) return purchases.value
      const query = searchQuery.value.toLowerCase()
      return purchases.value.filter(p => 
        p.purchase_number?.toLowerCase().includes(query) ||
        p.partner?.name?.toLowerCase().includes(query)
      )
    })

    const fetchPurchasesList = async () => {
      if (!companyId.value) return
      loading.value = true
      try {
        const res = await store.dispatch('purchases/fetchPurchases', {
          companyId: companyId.value,
          status: filters.value.status || null,
          partnerId: filters.value.partnerId || null
        })
        purchases.value = res.data
      } catch (err) {
        console.error('Error fetching purchases:', err)
      } finally {
        loading.value = false
      }
    }

    const fetchPartners = async () => {
      if (!companyId.value) return
      try {
        const res = await store.dispatch('partners/fetchPartners', {
          companyId: companyId.value,
          partnerType: 'SUPPLIER'
        })
        partners.value = res.data
      } catch (err) {
        console.error('Error fetching partners:', err)
      }
    }

    const fetchStatistics = async () => {
      if (!companyId.value) return
      try {
        const res = await store.dispatch('purchases/fetchStatistics', {
          companyId: companyId.value
        })
        statistics.value = res.data
      } catch (err) {
        console.error('Error fetching statistics:', err)
      }
    }

    const formatNumber = (value) => {
      return new Intl.NumberFormat('es-CO').format(value || 0)
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString('es-CO')
    }

    const getStatusClass = (status) => {
      const classes = {
        'DRAFT': 'badge-secondary',
        'ISSUED': 'badge-primary',
        'PAID': 'badge-success',
        'PARTIAL': 'badge-warning',
        'OVERDUE': 'badge-danger',
        'CANCELLED': 'badge-dark'
      }
      return classes[status] || 'badge-secondary'
    }

    const getBalance = (purchase) => {
      const paid = purchase.payments?.reduce((sum, p) => sum + parseFloat(p.amount), 0) || 0
      return purchase.total_amount - paid
    }

    const clearFilters = () => {
      filters.value = { status: '', partnerId: '' }
      searchQuery.value = ''
      fetchPurchasesList()
    }

    const viewPurchase = (purchase) => {
      selectedPurchase.value = purchase
      showDetailModal.value = true
    }

    const editPurchase = (purchase) => {
      router.push(`/purchases/edit/${purchase.id}`)
    }

    const openPaymentModal = (purchase) => {
      selectedPurchase.value = purchase
      showPaymentModal.value = true
    }

    const confirmCancel = async (purchase) => {
      const message = purchase.status === 'DRAFT' 
        ? `¿Está seguro de anular la compra borrador ${purchase.purchase_number}?`
        : `¡ADVERTENCIA! Anular la compra ${purchase.purchase_number} revertirá el stock de inventario y generará un asiento contable de reversión. ¿Desea continuar?`
      
      if (!confirm(message)) return
      
      try {
        await store.dispatch('purchases/cancelPurchase', {
          purchaseId: purchase.id,
          companyId: companyId.value
        })
        fetchPurchasesList()
        fetchStatistics()
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al anular la compra')
      }
    }

    watch(companyId, (newId) => {
      if (newId) {
        fetchPurchasesList()
        fetchPartners()
        fetchStatistics()
      }
    }, { immediate: true })

    const onPaymentRegistered = () => {
      showPaymentModal.value = false
      fetchPurchasesList()
      fetchStatistics()
    }

    onMounted(() => {
      // Data is already being fetched by the immediate watcher
    })

    return {
      purchases,
      filteredPurchases,
      partners,
      statistics,
      loading,
      filters,
      searchQuery,
      showPaymentModal,
      showDetailModal,
      selectedPurchase,
      fetchPurchasesList,
      formatNumber,
      formatDate,
      getStatusClass,
      getBalance,
      clearFilters,
      viewPurchase,
      editPurchase,
      openPaymentModal,
      confirmCancel,
      onPaymentRegistered
    }
  }
}
</script>

<style scoped>
.purchases-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-icon {
  font-size: 18px;
  font-weight: bold;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-label {
  font-size: 12px;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.filters-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 12px;
  color: #7f8c8d;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.search-group {
  flex: 1;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
}

.table-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #ecf0f1;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
  font-size: 12px;
  text-transform: uppercase;
}

.data-table tbody tr:hover {
  background-color: #f8f9fa;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.badge-primary { background: #3498db; color: white; }
.badge-success { background: #27ae60; color: white; }
.badge-warning { background: #f39c12; color: white; }
.badge-danger { background: #e74c3c; color: white; }
.badge-secondary { background: #95a5a6; color: white; }
.badge-dark { background: #34495e; color: white; }
.badge-info { background: #9b59b6; color: white; }

.action-buttons {
  display: flex;
  gap: 4px;
}

.btn-icon-action {
  padding: 4px 8px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
}

.btn-icon-action:hover {
  opacity: 0.7;
}

.empty-message {
  text-align: center;
  color: #7f8c8d;
  padding: 40px !important;
}

.loading-spinner {
  text-align: center;
  padding: 20px;
  color: #7f8c8d;
}
</style>