<template>
  <div class="reporte-ingresos-container">
    <div class="page-header">
      <h2>Reporte de Ingresos</h2>
      <div class="page-actions">
        <button @click="exportCSV" class="btn btn-secondary" :disabled="loading">
          <i class="fas fa-file-csv"></i> Exportar
        </button>
        <button @click="loadReporte" class="btn btn-primary" :disabled="loading">
          <i class="fas fa-sync-alt"></i> Generar
        </button>
      </div>
    </div>

    <div class="filters-bar">
      <div class="filter-group">
        <label>Desde</label>
        <input type="date" v-model="dateFrom" @change="loadReporte" />
      </div>
      <div class="filter-group">
        <label>Hasta</label>
        <input type="date" v-model="dateTo" @change="loadReporte" />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Generando reporte de ingresos...</p>
    </div>

    <div v-if="error && !loading" class="alert alert-danger">{{ error }}</div>

    <div v-if="!loading && data" class="report-content">
      <div class="company-header">
        <h3>{{ data.company_name }}</h3>
        <p>NIT: {{ data.company_nit }}</p>
        <p>Período: {{ formatDateRange(data.date_from, data.date_to) }}</p>
      </div>

      <div class="summary-cards">
        <div class="summary-card">
          <h4>Ingresos Operacionales</h4>
          <div class="amount">{{ formatCurrency(data.totals.total_ingresos_operacionales) }}</div>
        </div>
        <div class="summary-card">
          <h4>IVA Generado</h4>
          <div class="amount">{{ formatCurrency(data.totals.total_iva_generado) }}</div>
        </div>
        <div class="summary-card">
          <h4>Devoluciones</h4>
          <div class="amount warning">{{ formatCurrency(data.totals.total_devoluciones) }}</div>
        </div>
        <div class="summary-card highlight">
          <h4>Ingresos Netos</h4>
          <div class="amount">{{ formatCurrency(data.totals.ingresos_netos) }}</div>
        </div>
      </div>

      <div class="table-responsive">
        <table class="ingresos-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>N° Factura</th>
              <th>Cliente</th>
              <th>Fuente</th>
              <th class="text-right">Base</th>
              <th class="text-right">IVA</th>
              <th class="text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in data.entries" :key="entry.invoice_id">
              <td>{{ formatDate(entry.date) }}</td>
              <td><strong>{{ entry.invoice_number }}</strong></td>
              <td>{{ entry.partner_name }}</td>
              <td>{{ entry.source }}</td>
              <td class="text-right">{{ formatCurrency(entry.base) }}</td>
              <td class="text-right">{{ formatCurrency(entry.tax_amount) }}</td>
              <td class="text-right"><strong>{{ formatCurrency(entry.total) }}</strong></td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="totals-row">
              <td colspan="4"><strong>TOTALES ({{ data.totals.num_facturas }} facturas)</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(data.totals.total_ingresos_operacionales) }}</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(data.totals.total_iva_generado) }}</strong></td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div v-if="data.entries.length === 0" class="empty-state">
        <i class="fas fa-chart-line"></i>
        <p>No hay ingresos en el período seleccionado</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'ReporteIngresosView',
  data() {
    return { data: null, loading: false, error: null, dateFrom: '', dateTo: '' }
  },
  methods: {
    async loadReporte() {
      this.loading = true
      this.error = null
      try {
        const params = { company_id: this.$route.params.companyId || 1 }
        if (this.dateFrom) params.date_from = this.dateFrom
        if (this.dateTo) params.date_to = this.dateTo
        const res = await api.get(`${process.env.VUE_APP_API_URL}/api/v1/accounting/reporte-ingresos/`, { params })
        this.data = res.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al generar reporte'
      } finally {
        this.loading = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' })
    },
    formatDateRange(from, to) {
      if (!from && !to) return 'Todo el período'
      const f = from ? this.formatDate(from) : 'Inicio'
      const t = to ? this.formatDate(to) : 'Actual'
      return `${f} - ${t}`
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(Number(value))
    },
    exportCSV() {
      if (!this.data || !this.data.entries.length) return
      let csv = 'Fecha,N° Factura,Cliente,Fuente,Base,IVA,Total\n'
      for (const e of this.data.entries) {
        csv += `"${this.formatDate(e.date)}","${e.invoice_number}","${e.partner_name}","${e.source}",${e.base},${e.tax_amount},${e.total}\n`
      }
      const t = this.data.totals
      csv += `\nTotales,,,,${t.total_ingresos_operacionales},${t.total_iva_generado},\n`
      csv += `Ingresos Netos,,,,${t.ingresos_netos},,\n`
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `ingresos_${new Date().toISOString().slice(0, 10)}.csv`
      link.click()
    }
  },
  created() { this.loadReporte() }
}
</script>

<style scoped>
.reporte-ingresos-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; flex-wrap: wrap; gap: 15px; }
.page-header h2 { color: #2c3e50; margin: 0; }
.page-actions { display: flex; gap: 10px; }
.filters-bar { display: flex; gap: 20px; margin-bottom: 25px; flex-wrap: wrap; background: #f8f9fa; padding: 15px; border-radius: 8px; }
.filter-group { display: flex; flex-direction: column; gap: 5px; }
.filter-group label { font-size: 0.85rem; font-weight: 600; color: #495057; }
.filter-group input { padding: 8px 12px; border: 2px solid #ddd; border-radius: 6px; }
.loading-state { text-align: center; padding: 40px; }
.loading-state .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #007bff; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.alert { padding: 15px; border-radius: 6px; margin-bottom: 20px; }
.alert-danger { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
.company-header { background: #e9ecef; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; }
.company-header h3 { margin: 0 0 5px 0; color: #2c3e50; }
.company-header p { margin: 2px 0; color: #6c757d; font-size: 0.9rem; }
.summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }
.summary-card { background: white; border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.summary-card h4 { margin: 0 0 10px 0; font-size: 0.9rem; color: #6c757d; }
.summary-card .amount { font-size: 1.5rem; font-weight: 700; color: #2c3e50; }
.summary-card .amount.warning { color: #dc3545; }
.summary-card.highlight { background: #007bff; color: white; }
.summary-card.highlight h4 { color: rgba(255,255,255,0.8); }
.summary-card.highlight .amount { color: white; }
.table-responsive { overflow-x: auto; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.ingresos-table { width: 100%; border-collapse: collapse; background: white; }
.ingresos-table th, .ingresos-table td { padding: 12px 10px; text-align: left; border-bottom: 1px solid #eee; white-space: nowrap; }
.ingresos-table th { background-color: #2c3e50; color: white; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }
.ingresos-table tbody tr:hover { background-color: #f8f9ff; }
.ingresos-table tfoot .totals-row { background-color: #e9ecef; font-weight: 700; }
.ingresos-table tfoot td { border-top: 2px solid #2c3e50; }
.text-right { text-align: right !important; }
.empty-state { text-align: center; padding: 40px 20px; color: #6c757d; }
.empty-state i { font-size: 3rem; margin-bottom: 15px; }
.btn { padding: 10px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 6px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: #007bff; color: white; }
.btn-primary:hover:not(:disabled) { background: #0056b3; }
.btn-secondary { background: #6c757d; color: white; }
.btn-secondary:hover:not(:disabled) { background: #545b62; }
</style>
