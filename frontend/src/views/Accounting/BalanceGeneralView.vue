<template>
  <div class="balance-general-view">
    <div class="view-header">
      <h2>{{ $t('nav.balanceGeneral') }}</h2>
      <div class="header-actions">
        <div class="date-filters">
          <label>{{ $t('common.cutDate') }}:</label>
          <input type="date" v-model="cutDate" class="form-control" />
          <button class="btn btn-primary" @click="fetchData">
            <i class="fas fa-search"></i> {{ $t('common.search') }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="data">
      <div class="report-card">
        <div class="report-header">
          <h3>{{ data.company_name }}</h3>
          <p>NIT: {{ data.company_nit }}</p>
          <p>{{ $t('common.cutDate') }}: {{ formatDate(data.cut_date) }}</p>
        </div>

        <div class="balance-equation">
          <span class="equation-label">{{ $t('accounting.equation') }}:</span>
          <span :class="['equation', isBalanced ? 'balanced' : 'unbalanced']">
            {{ $t('accounting.assets') }} ({{ formatCOP(data.total_activos) }}) = 
            {{ $t('accounting.liabilities') }} ({{ formatCOP(data.total_pasivos) }}) + 
            {{ $t('accounting.equity') }} ({{ formatCOP(data.total_patrimonio) }})
          </span>
          <span v-if="isBalanced" class="badge badge-success">{{ $t('accounting.balanced') }}</span>
          <span v-else class="badge badge-danger">{{ $t('accounting.notBalanced') }}</span>
        </div>

        <div class="balance-columns">
          <div class="column">
            <h4>{{ $t('accounting.assets') }}</h4>
            <div class="section">
              <h5>{{ $t('accounting.currentAssets') }}</h5>
              <div v-for="(item, idx) in data.activos_corrientes" :key="'ac'+idx" class="line-item">
                <span>{{ item.name }} ({{ item.code }})</span>
                <span class="amount">{{ formatCOP(item.balance) }}</span>
              </div>
              <div class="line-item total">
                <span>{{ $t('accounting.totalCurrent') }}</span>
                <span class="amount">{{ formatCOP(data.total_activos_corrientes) }}</span>
              </div>
            </div>
            <div class="section">
              <h5>{{ $t('accounting.nonCurrentAssets') }}</h5>
              <div v-for="(item, idx) in data.activos_no_corrientes" :key="'anc'+idx" class="line-item">
                <span>{{ item.name }} ({{ item.code }})</span>
                <span class="amount">{{ formatCOP(item.balance) }}</span>
              </div>
              <div class="line-item total">
                <span>{{ $t('accounting.totalNonCurrent') }}</span>
                <span class="amount">{{ formatCOP(data.total_activos_no_corrientes) }}</span>
              </div>
            </div>
            <div class="section grand-total">
              <div class="line-item">
                <span>{{ $t('accounting.totalAssets') }}</span>
                <span class="amount">{{ formatCOP(data.total_activos) }}</span>
              </div>
            </div>
          </div>

          <div class="column">
            <h4>{{ $t('accounting.liabilities') }}</h4>
            <div class="section">
              <h5>{{ $t('accounting.currentLiabilities') }}</h5>
              <div v-for="(item, idx) in data.pasivos_corrientes" :key="'pc'+idx" class="line-item">
                <span>{{ item.name }} ({{ item.code }})</span>
                <span class="amount">{{ formatCOP(item.balance) }}</span>
              </div>
              <div class="line-item total">
                <span>{{ $t('accounting.totalCurrent') }}</span>
                <span class="amount">{{ formatCOP(data.total_pasivos_corrientes) }}</span>
              </div>
            </div>
            <div class="section">
              <h5>{{ $t('accounting.nonCurrentLiabilities') }}</h5>
              <div v-for="(item, idx) in data.pasivos_no_corrientes" :key="'pnc'+idx" class="line-item">
                <span>{{ item.name }} ({{ item.code }})</span>
                <span class="amount">{{ formatCOP(item.balance) }}</span>
              </div>
              <div class="line-item total">
                <span>{{ $t('accounting.totalNonCurrent') }}</span>
                <span class="amount">{{ formatCOP(data.total_pasivos_no_corrientes) }}</span>
              </div>
            </div>
            <div class="section grand-total">
              <div class="line-item">
                <span>{{ $t('accounting.totalLiabilities') }}</span>
                <span class="amount">{{ formatCOP(data.total_pasivos) }}</span>
              </div>
            </div>
          </div>

          <div class="column">
            <h4>{{ $t('accounting.equity') }}</h4>
            <div class="section">
              <div v-for="(item, idx) in data.patrimonio" :key="'pat'+idx" class="line-item">
                <span>{{ item.name }} ({{ item.code }})</span>
                <span class="amount">{{ formatCOP(item.balance) }}</span>
              </div>
              <div class="line-item total">
                <span>{{ $t('accounting.totalEquity') }}</span>
                <span class="amount">{{ formatCOP(data.total_patrimonio) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="export-actions">
          <button class="btn btn-secondary" @click="exportCSV">
            <i class="fas fa-download"></i> {{ $t('common.export') }} CSV
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { formatCOP, formatDate } from '@/utils/formatters'

export default {
  name: 'BalanceGeneralView',
  data() {
    return {
      cutDate: new Date().toISOString().split('T')[0]
    }
  },
  computed: {
    ...mapState('accounting', {
      data: state => state.balanceGeneral,
      loading: state => state.loading,
      error: state => state.error
    }),
    companyId() {
      return this.$store.getters['company/getCompany']?.id || 1
    },
    isBalanced() {
      if (!this.data) return false
      const diff = Math.abs(
        Number(this.data.total_activos) - 
        (Number(this.data.total_pasivos) + Number(this.data.total_patrimonio))
      )
      return diff < 1
    }
  },
  methods: {
    formatCOP,
    formatDate,
    async fetchData() {
      try {
        await this.$store.dispatch('accounting/fetchBalanceGeneral', {
          companyId: this.companyId,
          cutDate: this.cutDate
        })
      } catch (err) {
        console.error('Error fetching balance general:', err)
      }
    },
    exportCSV() {
      if (!this.data) return
      const rows = [
        ['Balance General'],
        ['Empresa', this.data.company_name],
        ['NIT', this.data.company_nit],
        ['Fecha Corte', this.data.cut_date],
        [],
        ['ACTIVOS', '', this.data.total_activos],
        ...this.data.activos_corrientes.map(a => ['  ' + a.name, a.code, a.balance]),
        ['Total Corrientes', '', this.data.total_activos_corrientes],
        ...this.data.activos_no_corrientes.map(a => ['  ' + a.name, a.code, a.balance]),
        ['Total No Corrientes', '', this.data.total_activos_no_corrientes],
        [],
        ['PASIVOS', '', this.data.total_pasivos],
        ...this.data.pasivos_corrientes.map(p => ['  ' + p.name, p.code, p.balance]),
        ['Total Corrientes', '', this.data.total_pasivos_corrientes],
        ...this.data.pasivos_no_corrientes.map(p => ['  ' + p.name, p.code, p.balance]),
        ['Total No Corrientes', '', this.data.total_pasivos_no_corrientes],
        [],
        ['PATRIMONIO', '', this.data.total_patrimonio],
        ...this.data.patrimonio.map(p => ['  ' + p.name, p.code, p.balance]),
        [],
        ['VERIFICACIÓN', '', this.isBalanced ? 'BALANCEADO' : 'DESBALANCEADO']
      ]
      const csv = rows.map(r => r.join(',')).join('\n')
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'balance_general.csv'
      a.click()
    }
  },
  mounted() {
    this.fetchData()
  }
}
</script>

<style scoped>
.balance-general-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.date-filters {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-control {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.report-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 25px;
}

.report-header {
  text-align: center;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
  padding-bottom: 15px;
}

.report-header h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.balance-equation {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.equation-label {
  font-weight: 600;
  margin-right: 10px;
}

.badge {
  margin-left: 10px;
  padding: 4px 8px;
  border-radius: 4px;
}

.badge-success {
  background: #d4edda;
  color: #155724;
}

.badge-danger {
  background: #f8d7da;
  color: #721c24;
}

.balance-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.column {
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.column h4 {
  text-align: center;
  color: #2c3e50;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.section {
  margin-bottom: 15px;
}

.section h5 {
  color: #495057;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.line-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 0.85rem;
}

.line-item.total {
  font-weight: 600;
  border-top: 1px solid #ddd;
  padding-top: 8px;
  margin-top: 5px;
}

.line-item.grand-total {
  font-weight: 700;
  font-size: 1rem;
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
}

.amount {
  font-family: monospace;
}

.export-actions {
  margin-top: 20px;
  text-align: right;
}

.loading, .error-message {
  text-align: center;
  padding: 40px;
}

.error-message {
  color: #721c24;
  background: #f8d7da;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .balance-columns {
    grid-template-columns: 1fr;
  }
}
</style>