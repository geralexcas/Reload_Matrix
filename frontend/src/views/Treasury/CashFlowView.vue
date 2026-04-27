<template>
  <div class="cash-flow-view">
    <div class="view-header">
      <h2>Flujo de Caja</h2>
    </div>

    <div class="filters">
      <div class="filter-group">
        <label>Desde:</label>
        <input type="date" v-model="dateFrom" />
      </div>
      <div class="filter-group">
        <label>Hasta:</label>
        <input type="date" v-model="dateTo" />
      </div>
      <button class="btn btn-primary" @click="loadCashFlow">Generar</button>
    </div>

    <div class="summary-cards" v-if="cashFlow">
      <div class="summary-card card-green">
        <h3>Total Entradas</h3>
        <p class="amount">{{ formatCurrency(cashFlow.total_inflows) }}</p>
      </div>
      <div class="summary-card card-red">
        <h3>Total Salidas</h3>
        <p class="amount">{{ formatCurrency(cashFlow.total_outflows) }}</p>
      </div>
      <div class="summary-card" :class="cashFlow.net_flow >= 0 ? 'card-green' : 'card-red'">
        <h3>Flujo Neto</h3>
        <p class="amount">{{ formatCurrency(cashFlow.net_flow) }}</p>
      </div>
    </div>

    <table class="data-table" v-if="cashFlow && cashFlow.entries.length">
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Cuenta</th>
          <th>Tipo</th>
          <th>Monto</th>
          <th>Descripción</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in cashFlow.entries" :key="entry.date + entry.transaction_type">
          <td>{{ formatDate(entry.date) }}</td>
          <td>{{ entry.account_name }}</td>
          <td>{{ txLabel(entry.transaction_type) }}</td>
          <td :class="isInflow(entry.transaction_type) ? 'positive' : 'negative'">{{ formatCurrency(entry.amount) }}</td>
          <td>{{ entry.description || '-' }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="cashFlow && cashFlow.entries.length === 0" class="empty">Sin movimientos en el período.</div>
  </div>
</template>

<script>
export default {
  name: 'CashFlowView',
  data() {
    return { dateFrom: '', dateTo: '' }
  },
  computed: {
    cashFlow() { return this.$store.state.treasury.cashFlow }
  },
  mounted() {
    this.loadCashFlow()
  },
  methods: {
    loadCashFlow() {
      this.$store.dispatch('treasury/fetchCashFlow', {
        dateFrom: this.dateFrom || null,
        dateTo: this.dateTo || null
      })
    },
    formatCurrency(v) { return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(v || 0) },
    formatDate(d) { return new Date(d).toLocaleDateString('es-CO') },
    txLabel(t) { return { DEPOSIT: 'Depósito', WITHDRAWAL: 'Retiro', TRANSFER_IN: 'Transferencia Rec.', TRANSFER_OUT: 'Transferencia Env.', FEE: 'Comisión', INTEREST: 'Interés', CHECK_ISSUED: 'Cheque Emitido', CHECK_CLEARED: 'Cheque Cobrado', CHECK_BOUNCED: 'Cheque Devuelto' }[t] || t },
    isInflow(t) { return ['DEPOSIT', 'TRANSFER_IN', 'INTEREST', 'CHECK_CLEARED'].includes(t) }
  }
}
</script>

<style scoped>
.cash-flow-view { padding: 20px; }
.view-header { margin-bottom: 24px; }
.view-header h2 { margin: 0; }
.filters { display: flex; gap: 16px; align-items: flex-end; margin-bottom: 20px; }
.filter-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 0.8rem; }
.filter-group input { padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px; }
.summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.summary-card { padding: 20px; border-radius: 12px; color: #fff; }
.summary-card h3 { margin: 0 0 8px; font-size: 0.9rem; opacity: 0.9; }
.summary-card .amount { margin: 0; font-size: 1.4rem; font-weight: 700; }
.card-green { background: linear-gradient(135deg, #11998e, #38ef7d); }
.card-red { background: linear-gradient(135deg, #eb3349, #f45c43); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 0.85rem; }
.data-table th { background: #f8f9fa; font-weight: 600; }
.positive { color: #2e7d32; font-weight: 600; }
.negative { color: #c62828; font-weight: 600; }
.empty { text-align: center; padding: 40px; color: #999; }
.btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.btn-primary { background: #667eea; color: #fff; }
</style>
