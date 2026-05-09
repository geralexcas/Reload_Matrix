<template>
  <div class="libro-mayor-container">
    <div class="page-header">
      <h2>Libro Mayor</h2>
      <div class="page-actions">
        <button @click="exportCSV" class="btn btn-secondary" :disabled="loading">
          <i class="fas fa-file-csv"></i> Exportar CSV
        </button>
        <button @click="loadLibroMayor" class="btn btn-primary" :disabled="loading">
          <i class="fas fa-sync-alt"></i> Actualizar
        </button>
      </div>
    </div>

    <div class="filters-bar">
      <div class="filter-group">
        <label>Desde</label>
        <input type="date" v-model="dateFrom" @change="loadLibroMayor" />
      </div>
      <div class="filter-group">
        <label>Hasta</label>
        <input type="date" v-model="dateTo" @change="loadLibroMayor" />
      </div>
      <div class="filter-group">
        <label>Cuenta</label>
        <input type="text" v-model="accountCode" placeholder="Ej: 1130" @keyup.enter="loadLibroMayor" />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Generando Libro Mayor...</p>
    </div>

    <div v-if="error && !loading" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-if="!loading && libroMayor" class="libro-content">
      <div class="company-header">
        <h3>{{ libroMayor.company_name || 'Empresa' }}</h3>
        <p>NIT: {{ libroMayor.company_nit || 'N/A' }}</p>
        <p>Período: {{ formatDateRange(libroMayor.date_from, libroMayor.date_to) }}</p>
      </div>

      <div v-for="account in libroMayor.accounts" :key="account.account_code" class="account-section">
        <div class="account-header" @click="toggleAccount(account.account_code)">
          <div class="account-info">
            <i :class="expandedAccounts.includes(account.account_code) ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"></i>
            <span class="account-code">{{ account.account_code }}</span>
            <span class="account-name">{{ account.account_name }}</span>
            <span class="account-type-badge" :class="'type-' + account.account_type.toLowerCase()">
              {{ getAccountTypeLabel(account.account_type) }}
            </span>
          </div>
          <div class="account-summary">
            <span class="summary-item">
              <small>Saldo Inicial:</small>
              <strong>{{ formatCurrency(account.initial_balance) }}</strong>
            </span>
            <span class="summary-item">
              <small>Débitos:</small>
              <strong>{{ formatCurrency(account.total_debits) }}</strong>
            </span>
            <span class="summary-item">
              <small>Créditos:</small>
              <strong>{{ formatCurrency(account.total_credits) }}</strong>
            </span>
            <span class="summary-item final">
              <small>Saldo Final:</small>
              <strong>{{ formatCurrency(account.final_balance) }}</strong>
            </span>
          </div>
        </div>

        <div v-show="expandedAccounts.includes(account.account_code)" class="account-lines">
          <table class="lines-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Referencia</th>
                <th>Descripción</th>
                <th class="text-right">Débito</th>
                <th class="text-right">Crédito</th>
                <th class="text-right">Saldo</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(line, idx) in account.lines" :key="idx">
                <td>{{ formatDate(line.entry_date) }}</td>
                <td>{{ line.reference || '-' }}</td>
                <td>{{ line.description || '-' }}</td>
                <td class="text-right">{{ formatCurrency(line.debit) }}</td>
                <td class="text-right">{{ formatCurrency(line.credit) }}</td>
                <td class="text-right" :class="{'debit-positive': line.balance > 0, 'credit-negative': line.balance < 0}">
                  {{ formatCurrency(line.balance) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="libroMayor.accounts.length === 0" class="empty-state">
        <i class="fas fa-file-invoice"></i>
        <p>No hay movimientos contables en el período seleccionado</p>
      </div>

      <div class="grand-totals">
        <h4>Totales Generales</h4>
        <div class="totals-row">
          <span>Total Débitos:</span>
          <strong>{{ formatCurrency(libroMayor.grand_total_debits) }}</strong>
        </div>
        <div class="totals-row">
          <span>Total Créditos:</span>
          <strong>{{ formatCurrency(libroMayor.grand_total_credits) }}</strong>
        </div>
        <div class="totals-row balance-check" :class="{'balanced': isBalanced, 'unbalanced': !isBalanced}">
          <span>Diferencia:</span>
          <strong>{{ formatCurrency(balanceDifference) }}</strong>
          <span class="badge" :class="isBalanced ? 'badge-success' : 'badge-danger'">
            {{ isBalanced ? 'Cuadrado' : 'Descuadrado' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'LibroMayorView',
  data() {
    return {
      libroMayor: null,
      loading: false,
      error: null,
      dateFrom: '',
      dateTo: '',
      accountCode: '',
      expandedAccounts: []
    }
  },
  computed: {
    isBalanced() {
      if (!this.libroMayor) return true
      const debits = Number(this.libroMayor.grand_total_debits) || 0
      const credits = Number(this.libroMayor.grand_total_credits) || 0
      return Math.abs(debits - credits) < 0.01
    },
    balanceDifference() {
      if (!this.libroMayor) return 0
      const debits = Number(this.libroMayor.grand_total_debits) || 0
      const credits = Number(this.libroMayor.grand_total_credits) || 0
      return debits - credits
    }
  },
  methods: {
    async loadLibroMayor() {
      this.loading = true
      this.error = null
      try {
        const companyId = this.$route.params.companyId || 1
        const params = { company_id: companyId }
        if (this.dateFrom) params.date_from = this.dateFrom
        if (this.dateTo) params.date_to = this.dateTo
        if (this.accountCode) params.account_code = this.accountCode

        const res = await api.get(
          '/api/v1/accounting/libro-mayor/',
          { params }
        )
        this.libroMayor = res.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al generar el Libro Mayor'
      } finally {
        this.loading = false
      }
    },
    toggleAccount(code) {
      const idx = this.expandedAccounts.indexOf(code)
      if (idx >= 0) {
        this.expandedAccounts.splice(idx, 1)
      } else {
        this.expandedAccounts.push(code)
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('es-CO', {
        year: 'numeric', month: 'short', day: 'numeric'
      })
    },
    formatDateRange(from, to) {
      if (!from && !to) return 'Todo el período'
      const f = from ? this.formatDate(from) : 'Inicio'
      const t = to ? this.formatDate(to) : 'Actual'
      return `${f} - ${t}`
    },
    formatCurrency(value) {
      if (value === undefined || value === null) return '$ 0'
      const num = Number(value)
      if (isNaN(num)) return '$ 0'
      return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(num)
    },
    getAccountTypeLabel(type) {
      const labels = {
        ASSET: 'Activo',
        LIABILITY: 'Pasivo',
        EQUITY: 'Patrimonio',
        REVENUE: 'Ingreso',
        EXPENSE: 'Gasto'
      }
      return labels[type] || type
    },
    exportCSV() {
      if (!this.libroMayor || !this.libroMayor.accounts.length) return

      let csv = 'Cuenta,Nombre,Tipo,Saldo Inicial,Débitos,Créditos,Saldo Final\n'
      for (const acc of this.libroMayor.accounts) {
        csv += `"${acc.account_code}","${acc.account_name}","${acc.account_type}",${acc.initial_balance},${acc.total_debits},${acc.total_credits},${acc.final_balance}\n`
      }
      csv += `\nTotales,,,${this.libroMayor.accounts.reduce((s, a) => s + Number(a.initial_balance), 0)},${this.libroMayor.grand_total_debits},${this.libroMayor.grand_total_credits},${this.libroMayor.accounts.reduce((s, a) => s + Number(a.final_balance), 0)}\n`

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `libro_mayor_${new Date().toISOString().slice(0, 10)}.csv`
      link.click()
    }
  },
  created() {
    this.loadLibroMayor()
  }
}
</script>

<style scoped>
.libro-mayor-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.page-header h2 {
  color: #2c3e50;
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 10px;
}

.filters-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
  flex-wrap: wrap;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #495057;
}

.filter-group input {
  padding: 8px 12px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
}

.filter-group input:focus {
  outline: none;
  border-color: #007bff;
}

.loading-state {
  text-align: center;
  padding: 40px 20px;
}

.loading-state .spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.alert {
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.company-header {
  background: #e9ecef;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.company-header h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.company-header p {
  margin: 2px 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
}

.account-section {
  margin-bottom: 15px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.account-header {
  background: #f8f9fa;
  padding: 15px 20px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.account-header:hover {
  background: #e9ecef;
}

.account-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.account-code {
  font-weight: 700;
  font-size: 1.1rem;
  color: #2c3e50;
}

.account-name {
  color: #495057;
}

.account-type-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.type-asset { background: #d1ecf1; color: #0c5460; }
.type-liability { background: #f8d7da; color: #721c24; }
.type-equity { background: #d4edda; color: #155724; }
.type-revenue { background: #d1e7dd; color: #0f5132; }
.type-expense { background: #fff3cd; color: #664d03; }

.account-summary {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.summary-item small {
  color: #6c757d;
  font-size: 0.75rem;
}

.summary-item strong {
  color: #2c3e50;
}

.summary-item.final strong {
  color: #007bff;
}

.account-lines {
  border-top: 1px solid #dee2e6;
}

.lines-table {
  width: 100%;
  border-collapse: collapse;
}

.lines-table th,
.lines-table td {
  padding: 10px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.lines-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.lines-table tbody tr:hover {
  background: #f8f9ff;
}

.text-right {
  text-align: right !important;
}

.debit-positive {
  color: #155724;
}

.credit-negative {
  color: #721c24;
}

.grand-totals {
  background: #2c3e50;
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-top: 25px;
}

.grand-totals h4 {
  margin: 0 0 15px 0;
  border-bottom: 1px solid rgba(255,255,255,0.2);
  padding-bottom: 10px;
}

.totals-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.totals-row:last-child {
  border-bottom: none;
}

.balance-check .badge {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-left: 10px;
}

.badge-success {
  background: #28a745;
  color: white;
}

.badge-danger {
  background: #dc3545;
  color: white;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

@media (max-width: 768px) {
  .account-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .account-summary {
    width: 100%;
    justify-content: space-between;
  }

  .lines-table th,
  .lines-table td {
    padding: 8px 6px;
    font-size: 0.8rem;
  }
}
</style>
