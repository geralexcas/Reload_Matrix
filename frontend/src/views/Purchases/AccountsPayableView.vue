<template>
  <div class="accounts-payable-container">
    <div class="page-header">
      <h1 class="page-title">Cuentas por Pagar</h1>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="refresh">
          <span>🔄</span> Actualizar
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="summary-cards">
      <div class="stat-card card-red">
        <div class="stat-label">Vencidas</div>
        <div class="stat-value">${{ formatNumber(summary.total_overdue) }}</div>
        <div class="stat-count">{{ summary.overdue_count }} factura(s)</div>
      </div>
      
      <div class="stat-card card-yellow">
        <div class="stat-label">Próximas a Vencer</div>
        <div class="stat-value">${{ formatNumber(summary.total_upcoming) }}</div>
        <div class="stat-count">{{ summary.upcoming_count }} factura(s)</div>
      </div>
      
      <div class="stat-card card-blue">
        <div class="stat-label">Total Pendiente</div>
        <div class="stat-value">${{ formatNumber(summary.total_pending) }}</div>
        <div class="stat-count">{{ summary.pending_count }} factura(s)</div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button 
        :class="['tab', activeTab === 'all' ? 'active' : '']" 
        @click="activeTab = 'all'"
      >
        Todas ({{ pendingInvoices.length }})
      </button>
      <button 
        :class="['tab', activeTab === 'overdue' ? 'active' : '']" 
        @click="activeTab = 'overdue'"
      >
        Vencidas ({{ overdueInvoices.length }})
      </button>
      <button 
        :class="['tab', activeTab === 'upcoming' ? 'active' : '']" 
        @click="activeTab = 'upcoming'"
      >
        Próximas ({{ upcomingInvoices.length }})
      </button>
    </div>

    <!-- Invoices Table -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Factura</th>
            <th>Proveedor</th>
            <th>Fecha Compra</th>
            <th>Fecha Vencimiento</th>
            <th>Estado</th>
            <th>Total</th>
            <th>Saldo Pendiente</th>
            <th>Días</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="invoice in displayedInvoices" 
            :key="invoice.id"
            :class="{
              'row-overdue': invoice.is_overdue,
              'row-upcoming': invoice.is_upcoming
            }"
          >
            <td>
              <span class="purchase-number">{{ invoice.purchase_number }}</span>
            </td>
            <td>{{ invoice.partner_name }}</td>
            <td>{{ formatDate(invoice.purchase_date) }}</td>
            <td>
              <span v-if="invoice.due_date" :class="getDueDateClass(invoice)">
                {{ formatDate(invoice.due_date) }}
              </span>
              <span v-else class="text-muted">Sin fecha</span>
            </td>
            <td>
              <span :class="['badge', getStatusBadge(invoice.status)]">
                {{ getStatusLabel(invoice.status) }}
              </span>
            </td>
            <td class="text-right">${{ formatNumber(invoice.total_amount) }}</td>
            <td class="text-right">
              <strong>${{ formatNumber(invoice.balance_due) }}</strong>
            </td>
            <td class="text-center">
              <span v-if="invoice.days_until_due !== null" :class="getDaysClass(invoice.days_until_due)">
                {{ invoice.days_until_due > 0 ? `+${invoice.days_until_due}` : invoice.days_until_due }}
              </span>
              <span v-else class="text-muted">-</span>
            </td>
            <td>
              <button class="btn btn-sm btn-primary" @click="viewPurchase(invoice.id)">
                Ver
              </button>
            </td>
          </tr>
          <tr v-if="displayedInvoices.length === 0">
            <td colspan="9" class="text-center text-muted">
              No hay facturas en esta categoría
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'AccountsPayableView',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const activeTab = ref('all')
    const overdueInvoices = ref([])
    const upcomingInvoices = ref([])
    const pendingInvoices = ref([])
    const summary = ref({
      total_pending: 0,
      total_overdue: 0,
      total_upcoming: 0,
      overdue_count: 0,
      upcoming_count: 0,
      pending_count: 0
    })

    const displayedInvoices = computed(() => {
      switch (activeTab.value) {
        case 'overdue':
          return overdueInvoices.value
        case 'upcoming':
          return upcomingInvoices.value
        default:
          return pendingInvoices.value
      }
    })

    const fetchAccountsPayable = async () => {
      loading.value = true
      try {
        const companyId = sessionStorage.getItem('selectedCompanyId')
        const response = await api.get(`/api/v1/purchases/accounts-payable`, {
          params: { company_id: companyId }
        })
        const data = response.data
        overdueInvoices.value = data.overdue_invoices || []
        upcomingInvoices.value = data.upcoming_invoices || []
        pendingInvoices.value = [
          ...overdueInvoices.value,
          ...upcomingInvoices.value,
          ...(data.pending_invoices || [])
        ]
        summary.value = data.summary || summary.value
      } catch (error) {
        console.error('Error fetching accounts payable:', error)
      } finally {
        loading.value = false
      }
    }

    const refresh = () => {
      fetchAccountsPayable()
    }

    const viewPurchase = (purchaseId) => {
      router.push(`/purchases?id=${purchaseId}`)
    }

    const formatNumber = (value) => {
      if (!value) return '0'
      return new Intl.NumberFormat('es-CO').format(value)
    }

    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleDateString('es-CO')
    }

    const getStatusBadge = (status) => {
      const badges = {
        'ISSUED': 'badge-warning',
        'PAID': 'badge-success',
        'PARTIAL': 'badge-info',
        'OVERDUE': 'badge-danger',
        'DRAFT': 'badge-secondary'
      }
      return badges[status] || 'badge-secondary'
    }

    const getStatusLabel = (status) => {
      const labels = {
        'ISSUED': 'Pendiente',
        'PAID': 'Pagada',
        'PARTIAL': 'Parcial',
        'OVERDUE': 'Vencida',
        'DRAFT': 'Borrador'
      }
      return labels[status] || status
    }

    const getDueDateClass = (invoice) => {
      if (invoice.is_overdue) return 'text-danger'
      if (invoice.is_upcoming) return 'text-warning'
      return ''
    }

    const getDaysClass = (days) => {
      if (days < 0) return 'days-overdue'
      if (days <= 7) return 'days-warning'
      return 'days-normal'
    }

    onMounted(() => {
      fetchAccountsPayable()
    })

    return {
      loading,
      activeTab,
      overdueInvoices,
      upcomingInvoices,
      pendingInvoices,
      summary,
      displayedInvoices,
      refresh,
      viewPurchase,
      formatNumber,
      formatDate,
      getStatusBadge,
      getStatusLabel,
      getDueDateClass,
      getDaysClass
    }
  }
}
</script>

<style scoped>
.accounts-payable-container {
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
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card.card-red {
  border-left: 4px solid #e74c3c;
}

.stat-card.card-yellow {
  border-left: 4px solid #f39c12;
}

.stat-card.card-blue {
  border-left: 4px solid #3498db;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.stat-count {
  font-size: 12px;
  color: #95a5a6;
  margin-top: 4px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.tab {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  color: #7f8c8d;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab:hover {
  color: #3498db;
}

.tab.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8f9fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  font-size: 13px;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #e0e0e0;
  font-size: 13px;
}

.data-table tr:hover {
  background: #f8f9fa;
}

.data-table tr.row-overdue {
  background: #fdeaea;
}

.data-table tr.row-upcoming {
  background: #fff8e6;
}

.purchase-number {
  font-weight: 600;
  color: #3498db;
}

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
}

.text-muted {
  color: #95a5a6;
}

.text-danger {
  color: #e74c3c;
}

.text-warning {
  color: #f39c12;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.badge-success {
  background: #d4edda;
  color: #155724;
}

.badge-warning {
  background: #fff3cd;
  color: #856404;
}

.badge-danger {
  background: #f8d7da;
  color: #721c24;
}

.badge-info {
  background: #d1ecf1;
  color: #0c5460;
}

.badge-secondary {
  background: #e2e3e5;
  color: #383d41;
}

.days-overdue {
  color: #e74c3c;
  font-weight: 600;
}

.days-warning {
  color: #f39c12;
  font-weight: 600;
}

.days-normal {
  color: #27ae60;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>