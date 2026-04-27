<template>
  <div class="transactions-view">
    <div class="view-header">
      <h2>Transacciones de Tesorería</h2>
    </div>

    <div class="filters">
      <div class="filter-group">
        <label>Tipo de cuenta:</label>
        <select v-model="filters.accountType" @change="loadTransactions">
          <option value="">Todas</option>
          <option value="BANK">Bancos</option>
          <option value="CASH">Caja</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Tipo de transacción:</label>
        <select v-model="filters.txType" @change="loadTransactions">
          <option value="">Todas</option>
          <option value="DEPOSIT">Depósito</option>
          <option value="WITHDRAWAL">Retiro</option>
          <option value="TRANSFER_IN">Transferencia recibida</option>
          <option value="TRANSFER_OUT">Transferencia enviada</option>
          <option value="FEE">Comisión</option>
          <option value="INTEREST">Interés</option>
          <option value="CHECK_ISSUED">Cheque emitido</option>
          <option value="CHECK_CLEARED">Cheque cobrado</option>
          <option value="CHECK_BOUNCED">Cheque devuelto</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Desde:</label>
        <input type="date" v-model="filters.dateFrom" @change="loadTransactions" />
      </div>
      <div class="filter-group">
        <label>Hasta:</label>
        <input type="date" v-model="filters.dateTo" @change="loadTransactions" />
      </div>
    </div>

    <table class="data-table" v-if="transactions.length">
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Cuenta</th>
          <th>Tipo</th>
          <th>Monto</th>
          <th>Descripción</th>
          <th>Referencia</th>
          <th>Saldo Después</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="tx in transactions" :key="tx.id">
          <td>{{ formatDate(tx.created_at) }}</td>
          <td>{{ tx.account_type === 'BANK' ? 'Banco' : 'Caja' }}</td>
          <td><span class="badge" :class="txBadgeClass(tx.transaction_type)">{{ txLabel(tx.transaction_type) }}</span></td>
          <td :class="txInflow(tx.transaction_type) ? 'positive' : 'negative'">{{ formatCurrency(tx.amount) }}</td>
          <td>{{ tx.description || '-' }}</td>
          <td>{{ tx.reference || '-' }}</td>
          <td>{{ formatCurrency(tx.balance_after) }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="transactions.length === 0" class="empty">No hay transacciones.</div>
  </div>
</template>

<script>
export default {
  name: 'TransactionsView',
  data() {
    return {
      filters: { accountType: '', txType: '', dateFrom: '', dateTo: '' }
    }
  },
  computed: {
    transactions() { return this.$store.state.treasury.transactions }
  },
  mounted() {
    this.loadTransactions()
  },
  methods: {
    loadTransactions() {
      this.$store.dispatch('treasury/fetchTransactions', {
        accountType: this.filters.accountType || null,
        transactionType: this.filters.txType || null,
        dateFrom: this.filters.dateFrom || null,
        dateTo: this.filters.dateTo || null
      })
      },
    formatCurrency(v) { return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(v || 0) },
    formatDate(d) { return new Date(d).toLocaleDateString('es-CO') },
    txLabel(t) { return { DEPOSIT: 'Depósito', WITHDRAWAL: 'Retiro', TRANSFER_IN: 'Transferencia Rec.', TRANSFER_OUT: 'Transferencia Env.', FEE: 'Comisión', INTEREST: 'Interés', CHECK_ISSUED: 'Cheque Emitido', CHECK_CLEARED: 'Cheque Cobrado', CHECK_BOUNCED: 'Cheque Devuelto' }[t] || t },
    txBadgeClass(t) { return ['DEPOSIT', 'TRANSFER_IN', 'INTEREST', 'CHECK_CLEARED'].includes(t) ? 'badge-green' : 'badge-red' },
    txInflow(t) { return ['DEPOSIT', 'TRANSFER_IN', 'INTEREST', 'CHECK_CLEARED'].includes(t) }
  }
}
</script>

<style scoped>
.transactions-view { padding: 20px; }
.view-header { margin-bottom: 24px; }
.view-header h2 { margin: 0; }
.filters { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; align-items: flex-end; }
.filter-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 0.8rem; }
.filter-group input, .filter-group select { padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.85rem; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 0.85rem; }
.data-table th { background: #f8f9fa; font-weight: 600; }
.positive { color: #2e7d32; font-weight: 600; }
.negative { color: #c62828; font-weight: 600; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.badge-green { background: #e8f5e9; color: #2e7d32; }
.badge-red { background: #ffebee; color: #c62828; }
.empty { text-align: center; padding: 40px; color: #999; }
</style>
