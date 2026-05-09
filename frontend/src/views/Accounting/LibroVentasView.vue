<template>
  <div class="libro-ventas-container">
    <div class="page-header">
      <h2>Libro de Ventas</h2>
      <div class="page-actions">
        <button @click="exportCSV" class="btn btn-secondary" :disabled="loading">
          <i class="fas fa-file-csv"></i> Exportar CSV
        </button>
        <button @click="loadLibroVentas" class="btn btn-primary" :disabled="loading">
          <i class="fas fa-sync-alt"></i> Actualizar
        </button>
      </div>
    </div>

    <div class="filters-bar">
      <div class="filter-group">
        <label>Desde</label>
        <input type="date" v-model="dateFrom" @change="loadLibroVentas" />
      </div>
      <div class="filter-group">
        <label>Hasta</label>
        <input type="date" v-model="dateTo" @change="loadLibroVentas" />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Generando Libro de Ventas...</p>
    </div>

    <div v-if="error && !loading" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-if="!loading && libroVentas" class="libro-content">
      <div class="company-header">
        <h3>{{ libroVentas.company_name || 'Empresa' }}</h3>
        <p>NIT: {{ libroVentas.company_nit || 'N/A' }}</p>
        <p>Período: {{ formatDateRange(libroVentas.date_from, libroVentas.date_to) }}</p>
      </div>

      <div class="table-responsive">
        <table class="ventas-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>N° Factura</th>
              <th>NIT</th>
              <th>Nombre / Razón Social</th>
              <th class="text-right">Base IVA 19%</th>
              <th class="text-right">IVA 19%</th>
              <th class="text-right">Base IVA 5%</th>
              <th class="text-right">IVA 5%</th>
              <th class="text-right">Sin IVA</th>
              <th class="text-right">Total IVA</th>
              <th class="text-right">Retefuente</th>
              <th class="text-right">ReteIVA</th>
              <th class="text-right">Total Factura</th>
              <th>Estado DIAN</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in libroVentas.entries" :key="entry.invoice_id">
              <td>{{ formatDate(entry.invoice_date) }}</td>
              <td><strong>{{ entry.invoice_number }}</strong></td>
              <td>{{ entry.partner_nit || 'N/A' }}</td>
              <td>{{ entry.partner_name }}</td>
              <td class="text-right">{{ formatCurrency(entry.base_iva_19) }}</td>
              <td class="text-right">{{ formatCurrency(entry.iva_19) }}</td>
              <td class="text-right">{{ formatCurrency(entry.base_iva_5) }}</td>
              <td class="text-right">{{ formatCurrency(entry.iva_5) }}</td>
              <td class="text-right">{{ formatCurrency(entry.base_no_iva) }}</td>
              <td class="text-right">{{ formatCurrency(entry.total_iva) }}</td>
              <td class="text-right">{{ formatCurrency(entry.retencion_fuente) }}</td>
              <td class="text-right">{{ formatCurrency(entry.retencion_iva) }}</td>
              <td class="text-right"><strong>{{ formatCurrency(entry.total_invoice) }}</strong></td>
              <td>
                <span class="status-badge" :class="'status-' + (entry.estado_dian || 'BORRADOR').toLowerCase()">
                  {{ entry.estado_dian || 'Borrador' }}
                </span>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="totals-row">
              <td colspan="4"><strong>TOTALES ({{ libroVentas.totals.num_facturas || 0 }} facturas)</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(libroVentas.totals.total_base_iva_19) }}</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(libroVentas.totals.total_iva_19) }}</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(libroVentas.totals.total_base_iva_5) }}</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(libroVentas.totals.total_iva_5) }}</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(libroVentas.totals.total_base_no_iva) }}</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(libroVentas.totals.total_iva) }}</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(libroVentas.totals.total_retencion_fuente) }}</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(libroVentas.totals.total_retencion_iva) }}</strong></td>
              <td class="text-right"><strong>{{ formatCurrency(libroVentas.totals.total_facturas) }}</strong></td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div v-if="libroVentas.entries.length === 0" class="empty-state">
        <i class="fas fa-file-invoice"></i>
        <p>No hay facturas de venta en el período seleccionado</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'LibroVentasView',
  data() {
    return {
      libroVentas: null,
      loading: false,
      error: null,
      dateFrom: '',
      dateTo: ''
    }
  },
  methods: {
    async loadLibroVentas() {
      this.loading = true
      this.error = null
      try {
        const companyId = this.$route.params.companyId || 1
        const params = { company_id: companyId }
        if (this.dateFrom) params.date_from = this.dateFrom
        if (this.dateTo) params.date_to = this.dateTo

        const res = await api.get(
          '/api/v1/accounting/libro-ventas/',
          { params }
        )
        this.libroVentas = res.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al generar el Libro de Ventas'
      } finally {
        this.loading = false
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
      const num = Number(value)
      return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(num)
    },
    exportCSV() {
      if (!this.libroVentas || !this.libroVentas.entries.length) return

      let csv = 'Fecha,N° Factura,NIT,Nombre/Base IVA 19%,IVA 19%,Base IVA 5%,IVA 5%,Sin IVA,Total IVA,Retefuente,ReteIVA,Total Factura,Estado DIAN\n'
      for (const entry of this.libroVentas.entries) {
        csv += `"${this.formatDate(entry.invoice_date)}","${entry.invoice_number}","${entry.partner_nit || ''}","${entry.partner_name}",${entry.base_iva_19},${entry.iva_19},${entry.base_iva_5},${entry.iva_5},${entry.base_no_iva},${entry.total_iva},${entry.retencion_fuente},${entry.retencion_iva},${entry.total_invoice},"${entry.estado_dian || ''}"\n`
      }
      const t = this.libroVentas.totals
      csv += `\nTOTALES,,,,${t.total_base_iva_19},${t.total_iva_19},${t.total_base_iva_5},${t.total_iva_5},${t.total_base_no_iva},${t.total_iva},${t.total_retencion_fuente},${t.total_retencion_iva},${t.total_facturas},\n`

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `libro_ventas_${new Date().toISOString().slice(0, 10)}.csv`
      link.click()
    }
  },
  created() {
    this.loadLibroVentas()
  }
}
</script>

<style scoped>
.libro-ventas-container {
  max-width: 1600px;
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

.table-responsive {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.ventas-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  min-width: 1200px;
}

.ventas-table th,
.ventas-table td {
  padding: 12px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
  white-space: nowrap;
}

.ventas-table th {
  background-color: #2c3e50;
  color: white;
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: sticky;
  top: 0;
}

.ventas-table tbody tr:hover {
  background-color: #f8f9ff;
}

.ventas-table tfoot .totals-row {
  background-color: #e9ecef;
  font-weight: 700;
}

.ventas-table tfoot td {
  border-top: 2px solid #2c3e50;
}

.text-right {
  text-align: right !important;
}

.status-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-borrador { background: #fff3cd; color: #856404; }
.status-enviado { background: #cce5ff; color: #004085; }
.status-aceptado { background: #d4edda; color: #155724; }
.status-rechazado { background: #f8d7da; color: #721c24; }

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
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
  .ventas-table th,
  .ventas-table td {
    padding: 8px 6px;
    font-size: 0.8rem;
  }
}
</style>
