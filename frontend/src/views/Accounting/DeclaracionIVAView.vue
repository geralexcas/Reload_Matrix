<template>
  <div class="declaracion-iva-container">
    <div class="page-header">
      <h2>Declaración de IVA</h2>
      <div class="page-actions">
        <button @click="exportCSV" class="btn btn-secondary" :disabled="loading">
          <i class="fas fa-file-csv"></i> Exportar
        </button>
        <button @click="loadDeclaracion" class="btn btn-primary" :disabled="loading">
          <i class="fas fa-sync-alt"></i> Generar
        </button>
      </div>
    </div>

    <div class="filters-bar">
      <div class="filter-group">
        <label>Desde</label>
        <input type="date" v-model="dateFrom" @change="loadDeclaracion" />
      </div>
      <div class="filter-group">
        <label>Hasta</label>
        <input type="date" v-model="dateTo" @change="loadDeclaracion" />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Generando declaración de IVA...</p>
    </div>

    <div v-if="error && !loading" class="alert alert-danger">{{ error }}</div>

    <div v-if="!loading && data" class="report-content">
      <div class="company-header">
        <h3>{{ data.company_name }}</h3>
        <p>NIT: {{ data.company_nit }}-{{ data.company_dv }} | Régimen: {{ data.regimen }}</p>
        <p>Período: {{ data.period }}</p>
      </div>

      <div v-if="['SIMPLE', 'NO_RESPONSABLE'].includes(data.regimen)" class="alert alert-info">
        <i class="fas fa-info-circle"></i>
        Régimen Simple / No Responsable: No declara IVA por separado.
      </div>

      <div v-else class="iva-grid">
        <div class="iva-section">
          <h4>IVA Generado (Ventas)</h4>
          <table class="iva-table">
            <thead>
              <tr>
                <th>Concepto</th>
                <th class="text-right">Base</th>
                <th class="text-right">IVA</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in data.iva_generado" :key="item.concept">
                <td>{{ item.concept }}</td>
                <td class="text-right">{{ formatCurrency(item.base) }}</td>
                <td class="text-right">{{ formatCurrency(item.tax_amount) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="total-row">
                <td><strong>Total IVA Generado</strong></td>
                <td></td>
                <td class="text-right"><strong>{{ formatCurrency(data.total_iva_generado) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>

        <div class="iva-section">
          <h4>IVA Soportado (Compras)</h4>
          <table class="iva-table">
            <thead>
              <tr>
                <th>Concepto</th>
                <th class="text-right">Base</th>
                <th class="text-right">IVA</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in data.iva_soportado" :key="item.concept">
                <td>{{ item.concept }}</td>
                <td class="text-right">{{ formatCurrency(item.base) }}</td>
                <td class="text-right">{{ formatCurrency(item.tax_amount) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="total-row">
                <td><strong>Total IVA Soportado</strong></td>
                <td></td>
                <td class="text-right"><strong>{{ formatCurrency(data.total_iva_soportado) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <div v-if="!['SIMPLE', 'NO_RESPONSABLE'].includes(data.regimen)" class="iva-result" :class="data.es_a_pagar ? 'payable' : 'favor'">
        <div class="result-card">
          <h4>{{ data.es_a_pagar ? 'IVA a Pagar' : 'IVA a Favor' }}</h4>
          <div class="result-amount">{{ formatCurrency(data.es_a_pagar ? data.iva_a_pagar : data.iva_a_favor) }}</div>
          <p class="result-note">
            {{ data.es_a_pagar
              ? 'El IVA generado supera el IVA soportado. Debe pagar la diferencia a la DIAN.'
              : 'El IVA soportado supera el IVA generado. Tiene saldo a favor.'
            }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'DeclaracionIVAView',
  data() {
    return { data: null, loading: false, error: null, dateFrom: '', dateTo: '' }
  },
  methods: {
    async loadDeclaracion() {
      this.loading = true
      this.error = null
      try {
        const params = { company_id: this.$route.params.companyId || 1 }
        if (this.dateFrom) params.date_from = this.dateFrom
        if (this.dateTo) params.date_to = this.dateTo
        const res = await api.get(`${process.env.VUE_APP_API_URL}/api/v1/accounting/declaracion-iva/`, { params })
        this.data = res.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al generar declaración'
      } finally {
        this.loading = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' })
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(Number(value))
    },
    exportCSV() {
      if (!this.data) return
      let csv = 'Concepto,Base,IVA\n'
      csv += '--- IVA GENERADO ---\n'
      for (const item of this.data.iva_generado) csv += `"${item.concept}",${item.base},${item.tax_amount}\n`
      csv += `Total IVA Generado,,${this.data.total_iva_generado}\n`
      csv += '--- IVA SOPORTADO ---\n'
      for (const item of this.data.iva_soportado) csv += `"${item.concept}",${item.base},${item.tax_amount}\n`
      csv += `Total IVA Soportado,,${this.data.total_iva_soportado}\n`
      csv += `Resultado,,${this.data.es_a_pagar ? this.data.iva_a_pagar : -this.data.iva_a_favor}\n`
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `declaracion_iva_${new Date().toISOString().slice(0, 10)}.csv`
      link.click()
    }
  },
  created() { this.loadDeclaracion() }
}
</script>

<style scoped>
.declaracion-iva-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
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
.alert-info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
.company-header { background: #e9ecef; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; }
.company-header h3 { margin: 0 0 5px 0; color: #2c3e50; }
.company-header p { margin: 2px 0; color: #6c757d; font-size: 0.9rem; }
.iva-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
.iva-section { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 20px; }
.iva-section h4 { margin: 0 0 15px 0; color: #2c3e50; }
.iva-table { width: 100%; border-collapse: collapse; }
.iva-table th, .iva-table td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
.iva-table th { background: #f8f9fa; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }
.iva-table tfoot .total-row { background: #e9ecef; }
.text-right { text-align: right !important; }
.iva-result { margin-top: 20px; }
.result-card { padding: 25px; border-radius: 8px; text-align: center; }
.result-card.payable { background: #fff3cd; border: 2px solid #ffc107; }
.result-card.favor { background: #d4edda; border: 2px solid #28a745; }
.result-card h4 { margin: 0 0 10px 0; font-size: 1.1rem; }
.result-amount { font-size: 2rem; font-weight: 700; margin: 10px 0; }
.result-note { color: #6c757d; font-size: 0.9rem; margin: 10px 0 0 0; }
.btn { padding: 10px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 6px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: #007bff; color: white; }
.btn-primary:hover:not(:disabled) { background: #0056b3; }
.btn-secondary { background: #6c757d; color: white; }
.btn-secondary:hover:not(:disabled) { background: #545b62; }
@media (max-width: 768px) { .iva-grid { grid-template-columns: 1fr; } }
</style>
