<template>
  <div class="estado-resultados-view">
    <div class="view-header">
      <h2>{{ $t('nav.estadoResultados') }}</h2>
      <div class="header-actions">
        <div class="date-filters">
          <input type="date" v-model="dateFrom" class="form-control" :placeholder="$t('common.dateFrom')" />
          <input type="date" v-model="dateTo" class="form-control" :placeholder="$t('common.dateTo')" />
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
          <p>{{ $t('common.period') }}: {{ formatDate(data.date_from) }} - {{ formatDate(data.date_to) }}</p>
        </div>

        <div class="income-section">
          <h4>{{ $t('accounting.income') }}</h4>
          <div v-for="acc in data.ingresos" :key="acc.account_code" class="line-item">
            <span>{{ acc.account_code }} - {{ acc.account_name }}</span>
            <span class="amount">{{ formatCOP(acc.balance) }}</span>
          </div>
          <div class="line-item total">
            <span>{{ $t('accounting.grossIncome') }}</span>
            <span class="amount">{{ formatCOP(data.total_ingresos) }}</span>
          </div>
        </div>

        <div class="costs-section">
          <h4>{{ $t('accounting.costs') }}</h4>
          <div v-for="acc in data.costos" :key="acc.account_code" class="line-item">
            <span>{{ acc.account_code }} - {{ acc.account_name }}</span>
            <span class="amount">{{ formatCOP(acc.balance) }}</span>
          </div>
          <div class="line-item total">
            <span>{{ $t('accounting.grossProfit') }}</span>
            <span class="amount">{{ formatCOP(data.utilidad_bruta) }}</span>
          </div>
        </div>

        <div class="expenses-section">
          <h4>{{ $t('accounting.expenses') }}</h4>
          <div v-for="acc in data.gastos" :key="acc.account_code" class="line-item">
            <span>{{ acc.account_code }} - {{ acc.account_name }}</span>
            <span class="amount">{{ formatCOP(acc.balance) }}</span>
          </div>
          <div class="line-item total">
            <span>{{ $t('accounting.totalExpenses') }}</span>
            <span class="amount">{{ formatCOP(data.total_gastos) }}</span>
          </div>
        </div>

        <div class="net-income-section" :class="data.utilidad_neta >= 0 ? 'positive' : 'negative'">
          <div class="line-item big">
            <span>{{ $t('accounting.netIncome') }}</span>
            <span class="amount">{{ formatCOP(data.utilidad_neta) }}</span>
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
  name: 'EstadoResultadosView',
  data() {
    return {
      dateFrom: '',
      dateTo: ''
    }
  },
  computed: {
    ...mapState('accounting', {
      data: state => state.estadoResultados,
      loading: state => state.loading,
      error: state => state.error
    }),
    companyId() {
      return this.$store.getters['company/getCompany']?.id || 1
    }
  },
  methods: {
    formatCOP,
    formatDate,
    async fetchData() {
      try {
        await this.$store.dispatch('accounting/fetchEstadoResultados', {
          companyId: this.companyId,
          dateFrom: this.dateFrom,
          dateTo: this.dateTo
        })
      } catch (err) {
        console.error('Error fetching estado resultados:', err)
      }
    },
    exportCSV() {
      if (!this.data) return
      const rows = [
        ['Estado de Resultados'],
        ['Empresa', this.data.company_name],
        ['NIT', this.data.company_nit],
        ['Período', `${this.data.date_from} - ${this.data.date_to}`],
        [],
        ['INGRESOS'],
        ...this.data.ingresos.map(a => [`${a.account_code} - ${a.account_name}`, a.balance]),
        ['Total Ingresos', this.data.total_ingresos],
        [],
        ['COSTOS'],
        ...this.data.costos.map(a => [`${a.account_code} - ${a.account_name}`, a.balance]),
        ['Utilidad Bruta', this.data.utilidad_bruta],
        [],
        ['GASTOS'],
        ...this.data.gastos.map(a => [`${a.account_code} - ${a.account_name}`, a.balance]),
        ['Total Gastos', this.data.total_gastos],
        [],
        ['UTILIDAD NETA', this.data.utilidad_neta]
      ]
      const csv = rows.map(r => r.join(',')).join('\n')
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'estado_resultados.csv'
      a.click()
    }
  },
  mounted() {
    const today = new Date()
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
    this.dateFrom = firstDay.toISOString().split('T')[0]
    this.dateTo = today.toISOString().split('T')[0]
    this.fetchData()
  }
}
</script>

<style scoped>
.estado-resultados-view {
  max-width: 1000px;
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
  gap: 10px;
  flex-wrap: wrap;
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
  margin-bottom: 25px;
  border-bottom: 2px solid #eee;
  padding-bottom: 15px;
}

.report-header h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.report-header p {
  margin: 5px 0;
  color: #6c757d;
}

.income-section, .costs-section, .expenses-section {
  margin-bottom: 20px;
}

.income-section h4, .costs-section h4, .expenses-section h4 {
  color: #495057;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
  margin-bottom: 10px;
}

.line-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.line-item.total {
  font-weight: 600;
  border-bottom: 2px solid #ddd;
}

.line-item.big {
  font-size: 1.2rem;
  font-weight: 700;
  padding: 15px 0;
}

.amount {
  font-family: monospace;
}

.net-income-section {
  margin-top: 20px;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.net-income-section.positive {
  background-color: #d4edda;
  color: #155724;
}

.net-income-section.negative {
  background-color: #f8d7da;
  color: #721c24;
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
</style>