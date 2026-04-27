<template>
  <div class="reporte-retenciones-container">
    <div class="page-header">
      <h2>Reporte de Retenciones</h2>
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
      <p>Generando reporte de retenciones...</p>
    </div>

    <div v-if="error && !loading" class="alert alert-danger">{{ error }}</div>

    <div v-if="!loading && data" class="report-content">
      <div class="company-header">
        <h3>{{ data.company_name }}</h3>
        <p>NIT: {{ data.company_nit }}</p>
        <p>Período: {{ formatDateRange(data.date_from, data.date_to) }}</p>
      </div>

      <div class="table-responsive">
        <table class="retenciones-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>N° Factura</th>
              <th>Tipo</th>
              <th>NIT</th>
              <th>Nombre / Razón Social</th>
              <th>Concepto</th>
              <th class="text-right">Base</th>
              <th class="text-right">Tarifa</th>
              <th class="text-right">Valor Retención</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in data.entries" :key="entry.invoice_id + '-' + entry.concept">
              <td>{{ formatDate(entry.invoice_date) }}</td>
              <td><strong>{{ entry.invoice_number }}</strong></td>
              <td>
                <span class="type-badge" :class="entry.invoice_type === 'VENTA' ? 'badge-sale' : 'badge-purchase'">
                  {{ entry.invoice_type === 'VENTA' ? 'Venta' : 'Compra' }}
                </span>
              </td>
              <td>{{ entry.partner_nit || 'N/A' }}</td>
              <td>{{ entry.partner_name }}</td>
              <td>{{ entry.concept }}</td>
              <td class="text-right">{{ formatCurrency(entry.base_retencion) }}</td>
              <td class="text-right">{{ (Number(entry.tarifa) * 100).toFixed(1) }}%</td>
              <td class="text-right"><strong>{{ formatCurrency(entry.valor_retencion) }}</strong></td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="totals-row">
              <td colspan="8"><strong>TOTALES ({{ data.totals.num_retenciones }} retenciones)</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(data.totals.total_retenciones) }}</strong></td>
            </tr>
            <tr class="subtotals-row">
              <td colspan="6"></td>
              <td colspan="2">Retefuente:</td>
              <td class="text-right">{{ formatCurrency(data.totals.total_retefuente) }}</td>
            </tr>
            <tr class="subtotals-row">
              <td colspan="6"></td>
              <td colspan="2">ReteIVA:</td>
              <td class="text-right">{{ formatCurrency(data.totals.total_reteiva) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div v-if="data.entries.length === 0" class="empty-state">
        <i class="fas fa-receipt"></i>
        <p>No hay retenciones en el período seleccionado</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'ReporteRetencionesView',
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
        const res = await api.get(`${process.env.VUE_APP_API_URL}/api/v1/accounting/reporte-retenciones/`, { params })
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
      let csv = 'Fecha,N° Factura,Tipo,NIT,Nombre,Concepto,Base,Tarifa,Valor Retención\n'
      for (const e of this.data.entries) {
        csv += `"${this.formatDate(e.invoice_date)}","${e.invoice_number}","${e.invoice_type}","${e.partner_nit || ''}","${e.partner_name}","${e.concept}",${e.base_retencion},${Number(e.tarifa) * 100}%,${e.valor_retencion}\n`
      }
      const t = this.data.totals
      csv += `\nTotales,,,,,,,Retefuente:,${t.total_retefuente}\n`
      csv += `Totales,,,,,,,ReteIVA:,${t.total_reteiva}\n`
      csv += `Totales,,,,,,,Total:,${t.total_retenciones}\n`
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `retenciones_${new Date().toISOString().slice(0, 10)}.csv`
      link.click()
    }
  },
  created() { this.loadReporte() }
}
</script>

<style scoped>
.reporte-retenciones-container { max-width: 1400px; margin: 0 auto; padding: 20px; }
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
.table-responsive { overflow-x: auto; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.retenciones-table { width: 100%; border-collapse: collapse; background: white; min-width: 1100px; }
.retenciones-table th, .retenciones-table td { padding: 12px 10px; text-align: left; border-bottom: 1px solid #eee; white-space: nowrap; }
.retenciones-table th { background-color: #2c3e50; color: white; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }
.retenciones-table tbody tr:hover { background-color: #f8f9ff; }
.retenciones-table tfoot .totals-row { background-color: #e9ecef; font-weight: 700; }
.retenciones-table tfoot td { border-top: 2px solid #2c3e50; }
.retenciones-table tfoot .subtotals-row { background-color: #f8f9fa; }
.text-right { text-align: right !important; }
.type-badge { padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.badge-sale { background: #d4edda; color: #155724; }
.badge-purchase { background: #cce5ff; color: #004085; }
.empty-state { text-align: center; padding: 40px 20px; color: #6c757d; }
.empty-state i { font-size: 3rem; margin-bottom: 15px; }
.btn { padding: 10px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 6px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: #007bff; color: white; }
.btn-primary:hover:not(:disabled) { background: #0056b3; }
.btn-secondary { background: #6c757d; color: white; }
.btn-secondary:hover:not(:disabled) { background: #545b62; }
</style>
