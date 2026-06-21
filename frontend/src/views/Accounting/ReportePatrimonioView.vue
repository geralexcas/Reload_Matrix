<template>
  <div class="reporte-patrimonio-container">
    <div class="page-header">
      <h2>Reporte de Patrimonio</h2>
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
        <label>Fecha de corte</label>
        <input type="date" v-model="cutDate" @change="loadReporte" />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Generando reporte de patrimonio...</p>
    </div>

    <div v-if="error && !loading" class="alert alert-danger">{{ error }}</div>

    <div v-if="!loading && data" class="report-content">
      <div class="company-header">
        <h3>{{ data.company_name }}</h3>
        <p>NIT: {{ data.company_nit }}</p>
        <p>Fecha de corte: {{ formatDate(data.cut_date) }}</p>
      </div>

      <div class="balance-grid">
        <!-- Lado Izquierdo: ACTIVOS -->
        <div class="balance-section activos">
          <div class="section-header">
            <h4>Activos</h4>
            <span class="section-total">{{ formatCurrency(data.total_activos) }}</span>
          </div>
          <table class="balance-table">
            <tbody>
              <tr v-for="acc in data.activos" :key="acc.account_code">
                <td>
                  <span class="account-code">{{ acc.account_code }}</span>
                  {{ acc.account_name }}
                </td>
                <td class="text-right">{{ formatCurrency(acc.balance) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="total-row">
                <td><strong>Total Activos</strong></td>
                <td class="text-right"><strong>{{ formatCurrency(data.total_activos) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Lado Derecho: PASIVOS Y PATRIMONIO -->
        <div class="right-column">
          <!-- PASIVOS -->
          <div class="balance-section pasivos mb-4">
            <div class="section-header">
              <h4>Pasivos</h4>
              <span class="section-total">{{ formatCurrency(data.total_pasivos) }}</span>
            </div>
            <table class="balance-table">
              <tbody>
                <tr v-for="acc in data.pasivos" :key="acc.account_code">
                  <td>
                    <span class="account-code">{{ acc.account_code }}</span>
                    {{ acc.account_name }}
                  </td>
                  <td class="text-right">{{ formatCurrency(acc.balance) }}</td>
                </tr>
                <tr v-if="data.pasivos.length === 0">
                  <td colspan="2" class="text-center text-muted py-3">Sin pasivos registrados</td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="total-row">
                  <td><strong>Total Pasivos</strong></td>
                  <td class="text-right"><strong>{{ formatCurrency(data.total_pasivos) }}</strong></td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- PATRIMONIO -->
          <div class="balance-section patrimonio">
            <div class="section-header">
              <h4>Patrimonio</h4>
              <span class="section-total">{{ formatCurrency(data.total_patrimonio) }}</span>
            </div>
            <table class="balance-table">
              <tbody>
                <!-- Cuentas de Capital -->
                <tr v-for="acc in data.patrimonio_desglose.cuentas_patrimonio" :key="acc.account_code">
                  <td>
                    <span class="account-code">{{ acc.account_code }}</span>
                    {{ acc.account_name }}
                  </td>
                  <td class="text-right">{{ formatCurrency(acc.balance) }}</td>
                </tr>
                <!-- Utilidad del Ejercicio (Calculada) -->
                <tr class="utilidad-row">
                  <td>
                    <span class="account-code">RES</span>
                    Utilidad del Ejercicio (Ingresos - Gastos)
                    <div class="utilidad-detail">
                      ({{ formatCurrency(data.patrimonio_desglose.ingresos_totales) }} - {{ formatCurrency(data.patrimonio_desglose.gastos_totales) }})
                    </div>
                  </td>
                  <td class="text-right" :class="data.patrimonio_desglose.utilidad_ejercicio >= 0 ? 'text-success' : 'text-danger'">
                    {{ formatCurrency(data.patrimonio_desglose.utilidad_ejercicio) }}
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="total-row">
                  <td><strong>Total Patrimonio</strong></td>
                  <td class="text-right"><strong>{{ formatCurrency(data.total_patrimonio) }}</strong></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>

      <div class="patrimonio-result">
        <div class="result-card">
          <h4>Ecuación Contable</h4>
          <div class="equation">
            <div class="eq-group">
              <span class="eq-label">ACTIVOS</span>
              <span class="eq-value text-success">{{ formatCurrency(data.total_activos) }}</span>
            </div>
            <span class="eq-operator">=</span>
            <div class="eq-group">
              <span class="eq-label">PASIVOS</span>
              <span class="eq-value text-danger">{{ formatCurrency(data.total_pasivos) }}</span>
            </div>
            <span class="eq-operator">+</span>
            <div class="eq-group">
              <span class="eq-label">PATRIMONIO</span>
              <span class="eq-value text-warning">{{ formatCurrency(data.total_patrimonio) }}</span>
            </div>
          </div>
          <div v-if="Math.abs(Number(data.total_activos) - (Number(data.total_pasivos) + Number(data.total_patrimonio))) > 0.01" class="imbalance-warning">
            ⚠️ Atención: Existe un descuadre en la ecuación contable.
          </div>
        </div>
      </div>

      <div v-if="data.activos.length === 0 && data.pasivos.length === 0 && data.patrimonio_desglose.cuentas_patrimonio.length === 0" class="empty-state">
        <i class="fas fa-balance-scale"></i>
        <p>No hay movimientos registrados al corte seleccionado</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'ReportePatrimonioView',
  data() {
    return { data: null, loading: false, error: null, cutDate: '' }
  },
  methods: {
    async loadReporte() {
      this.loading = true
      this.error = null
      try {
        const params = { company_id: this.$store.getters['company/selectedCompanyId'] || 1 }
        if (this.cutDate) params.cut_date = this.cutDate
        const res = await api.get('/api/v1/accounting/reporte-patrimonio/', { params })
        this.data = res.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al generar reporte'
      } finally {
        this.loading = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' })
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(Number(value))
    },
    exportCSV() {
      if (!this.data) return
      let csv = 'Tipo,Cuenta,Codigo,Saldo\n'
      // Activos
      for (const acc of this.data.activos) csv += `Activo,"${acc.account_name}","${acc.account_code}",${acc.balance}\n`
      csv += `Activo,TOTAL ACTIVOS,,${this.data.total_activos}\n`
      
      // Pasivos
      for (const acc of this.data.pasivos) csv += `Pasivo,"${acc.account_name}","${acc.account_code}",${acc.balance}\n`
      csv += `Pasivo,TOTAL PASIVOS,,${this.data.total_pasivos}\n`
      
      // Patrimonio
      for (const acc of this.data.patrimonio_desglose.cuentas_patrimonio) {
        csv += `Patrimonio,"${acc.account_name}","${acc.account_code}",${acc.balance}\n`
      }
      csv += `Patrimonio,"Utilidad del Ejercicio (Ingresos - Gastos)",RES,${this.data.patrimonio_desglose.utilidad_ejercicio}\n`
      csv += `Patrimonio,TOTAL PATRIMONIO,,${this.data.total_patrimonio}\n`
      
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `patrimonio_${new Date().toISOString().slice(0, 10)}.csv`
      link.click()
    }
  },
  created() { this.loadReporte() }
}
</script>

<style scoped>
.reporte-patrimonio-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
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
.balance-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 25px; }
.right-column { display: flex; flex-direction: column; gap: 20px; }
.balance-section { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); overflow: hidden; height: fit-content; }
.section-header { padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,0,0,0.05); }
.activos .section-header { background: #e8f5e9; border-left: 5px solid #2e7d32; }
.pasivos .section-header { background: #ffebee; border-left: 5px solid #c62828; }
.patrimonio .section-header { background: #fff3e0; border-left: 5px solid #ef6c00; }
.section-header h4 { margin: 0; color: #2c3e50; font-weight: 700; }
.section-total { font-weight: 700; font-size: 1.1rem; }
.balance-table { width: 100%; border-collapse: collapse; }
.balance-table td { padding: 12px 20px; border-bottom: 1px solid #eee; font-size: 0.95rem; }
.balance-table tbody tr:hover { background: #f8f9ff; }
.account-code { font-weight: 700; color: #007bff; margin-right: 10px; font-family: monospace; }
.text-right { text-align: right !important; }
.text-center { text-align: center !important; }
.text-success { color: #28a745 !important; }
.text-danger { color: #dc3545 !important; }
.text-warning { color: #ffc107 !important; }
.text-muted { color: #6c757d !important; }
.py-3 { padding-top: 1rem !important; padding-bottom: 1rem !important; }
.mb-4 { margin-bottom: 1.5rem !important; }

.utilidad-row { background: #f8f9fa; }
.utilidad-detail { font-size: 0.75rem; color: #6c757d; margin-top: 4px; }

.balance-table tfoot .total-row { background: #f1f3f5; color: #212529; }
.balance-table tfoot td { border-bottom: none; }

.patrimonio-result { margin-top: 30px; }
.result-card { background: #2c3e50; color: white; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.result-card h4 { margin: 0 0 20px 0; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; }
.equation { display: flex; align-items: center; justify-content: center; gap: 20px; flex-wrap: wrap; }

.eq-group { display: flex; flex-direction: column; align-items: center; gap: 5px; }
.eq-label { font-size: 0.7rem; font-weight: 700; opacity: 0.7; }
.eq-value { font-size: 1.5rem; font-weight: 700; }

.eq-operator { font-size: 1.8rem; font-weight: 300; opacity: 0.5; }
.imbalance-warning { margin-top: 20px; padding: 10px; background: rgba(220, 53, 69, 0.2); border-radius: 6px; color: #ff8787; font-size: 0.9rem; }

.empty-state { text-align: center; padding: 60px 20px; color: #6c757d; }
.empty-state i { font-size: 4rem; margin-bottom: 20px; opacity: 0.3; }
.btn { padding: 10px 18px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 8px; font-weight: 600; transition: all 0.2s; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: #007bff; color: white; }
.btn-primary:hover:not(:disabled) { background: #0056b3; transform: translateY(-1px); }
.btn-secondary { background: #6c757d; color: white; }
.btn-secondary:hover:not(:disabled) { background: #545b62; }
@media (max-width: 992px) { .balance-grid { grid-template-columns: 1fr; } .equation { gap: 15px; } .eq-value { font-size: 1.2rem; } }
</style>
