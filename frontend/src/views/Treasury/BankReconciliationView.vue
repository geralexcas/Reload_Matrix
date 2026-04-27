<template>
  <div class="bank-reconciliation-view">
    <div class="view-header">
      <h2>Conciliación Bancaria</h2>
      <button class="btn btn-primary" @click="showCreateForm = true">+ Nueva Conciliación</button>
    </div>

    <div v-if="!currentRecon">
      <table class="data-table" v-if="reconciliations.length">
        <thead>
          <tr>
            <th>Banco</th>
            <th>Fecha Extracto</th>
            <th>Saldo Extracto</th>
            <th>Saldo Sistema</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reconciliations" :key="r.id">
            <td>{{ bankName(r.bank_account_id) }}</td>
            <td>{{ formatDate(r.statement_date) }}</td>
            <td>{{ formatCurrency(r.statement_balance) }}</td>
            <td>{{ formatCurrency(r.system_balance) }}</td>
            <td><span class="badge" :class="r.status === 'COMPLETED' ? 'badge-green' : 'badge-blue'">{{ r.status === 'COMPLETED' ? 'Completada' : 'En progreso' }}</span></td>
            <td>
              <button class="btn btn-sm btn-primary" @click="openReconciliation(r.id)" v-if="r.status === 'IN_PROGRESS'">Continuar</button>
              <button class="btn btn-sm btn-secondary" @click="openReconciliation(r.id)" v-else>Ver</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">No hay conciliaciones.</div>
    </div>

    <div v-if="currentRecon" class="reconciliation-detail">
      <div class="recon-header">
        <button class="btn btn-sm" @click="currentRecon = null; $store.commit('treasury/setCurrentReconciliation', null)">← Volver</button>
        <h3>Conciliación #{{ currentRecon.id }} - {{ bankName(currentRecon.bank_account_id) }}</h3>
      </div>

      <div class="recon-balances">
        <div class="balance-card">
          <h4>Saldo según Extracto</h4>
          <p class="amount">{{ formatCurrency(currentRecon.statement_balance) }}</p>
        </div>
        <div class="balance-card">
          <h4>Saldo según Sistema</h4>
          <p class="amount">{{ formatCurrency(currentRecon.system_balance) }}</p>
        </div>
        <div class="balance-card">
          <h4>Saldo Ajustado</h4>
          <p class="amount">{{ formatCurrency(currentRecon.adjusted_balance) }}</p>
        </div>
      </div>

      <div class="recon-actions" v-if="currentRecon.status === 'IN_PROGRESS'">
        <button class="btn btn-primary" @click="completeReconciliation">Completar Conciliación</button>
      </div>

      <div v-if="currentRecon.is_balanced && currentRecon.status === 'COMPLETED'" class="balanced-msg">
        ✅ Conciliación balanceada correctamente
      </div>
      <div v-if="!currentRecon.is_balanced && currentRecon.status === 'COMPLETED'" class="unbalanced-msg">
        ⚠️ Conciliación NO balanceada - Diferencia: {{ formatCurrency(Math.abs((currentRecon.adjusted_balance || 0) - currentRecon.system_balance)) }}
      </div>

      <table class="data-table" v-if="currentRecon.lines && currentRecon.lines.length">
        <thead>
          <tr>
            <th>Descripción</th>
            <th>Monto</th>
            <th>Conciliado</th>
            <th>Diferencia</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="line in currentRecon.lines" :key="line.id">
            <td>{{ line.description || '-' }}</td>
            <td>{{ formatCurrency(line.amount) }}</td>
            <td>{{ line.is_matched ? '✅ Sí' : '⏳ Pendiente' }}</td>
            <td>{{ formatCurrency(line.difference) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="modal-overlay" v-if="showCreateForm" @click.self="showCreateForm = false">
      <div class="modal">
        <h3>Nueva Conciliación Bancaria</h3>
        <form @submit.prevent="createReconciliation">
          <div class="form-group">
            <label>Cuenta bancaria:</label>
            <select v-model="form.bank_account_id" required>
              <option value="">Seleccionar...</option>
              <option v-for="a in bankAccounts" :key="a.id" :value="a.id">{{ a.bank_name }} - {{ a.name }} ({{ formatCurrency(a.current_balance) }})</option>
            </select>
          </div>
          <div class="form-group">
            <label>Fecha del extracto:</label>
            <input v-model="form.statement_date" type="datetime-local" required />
          </div>
          <div class="form-group">
            <label>Saldo según extracto bancario:</label>
            <input v-model.number="form.statement_balance" type="number" step="0.01" required />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Crear</button>
            <button type="button" class="btn" @click="showCreateForm = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BankReconciliationView',
  data() {
    return {
      showCreateForm: false,
      form: { bank_account_id: '', statement_date: '', statement_balance: 0 },
      currentRecon: null
    }
  },
  computed: {
    reconciliations() { return this.$store.state.treasury.reconciliations },
    bankAccounts() { return this.$store.state.treasury.bankAccounts }
  },
  mounted() {
    this.$store.dispatch('treasury/fetchBankAccounts')
    this.$store.dispatch('treasury/fetchReconciliations')
  },
  methods: {
    formatCurrency(v) { return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(v || 0) },
    formatDate(d) { return new Date(d).toLocaleDateString('es-CO') },
    bankName(id) { const a = this.bankAccounts.find(x => x.id === id); return a ? `${a.bank_name} - ${a.name}` : '#' + id },
    async createReconciliation() {
      try {
        await this.$store.dispatch('treasury/createReconciliation', this.form)
        this.showCreateForm = false
        this.form = { bank_account_id: '', statement_date: '', statement_balance: 0 }
        this.$store.dispatch('treasury/fetchReconciliations')
      } catch (e) { alert(e.response?.data?.detail || 'Error') }
    },
    async openReconciliation(id) {
      try {
        const res = await this.$store.dispatch('treasury/fetchReconciliationById', id)
        this.currentRecon = res.data
      } catch (e) { alert('Error al cargar') }
    },
    async completeReconciliation() {
      if (!confirm('¿Completar la conciliación?')) return
      try {
        const res = await this.$store.dispatch('treasury/completeReconciliation', this.currentRecon.id)
        this.currentRecon = res.data
        this.$store.dispatch('treasury/fetchReconciliations')
        this.$store.dispatch('treasury/fetchBankAccounts')
      } catch (e) { alert(e.response?.data?.detail || 'Error') }
    }
  }
}
</script>

<style scoped>
.bank-reconciliation-view { padding: 20px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.view-header h2 { margin: 0; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 0.85rem; }
.data-table th { background: #f8f9fa; font-weight: 600; }
.empty { text-align: center; padding: 40px; color: #999; }
.reconciliation-detail { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.recon-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.recon-header h3 { margin: 0; }
.recon-balances { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 20px; }
.balance-card { background: #f8f9fa; padding: 16px; border-radius: 8px; text-align: center; }
.balance-card h4 { margin: 0 0 8px; font-size: 0.85rem; color: #666; }
.balance-card .amount { margin: 0; font-size: 1.3rem; font-weight: 700; }
.recon-actions { margin-bottom: 20px; }
.balanced-msg { background: #e8f5e9; color: #2e7d32; padding: 12px; border-radius: 8px; margin-bottom: 16px; text-align: center; }
.unbalanced-msg { background: #fff3e0; color: #e65100; padding: 12px; border-radius: 8px; margin-bottom: 16px; text-align: center; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.badge-green { background: #e8f5e9; color: #2e7d32; }
.badge-blue { background: #e3f2fd; color: #1565c0; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 12px; padding: 24px; max-width: 500px; width: 90%; }
.modal h3 { margin: 0 0 16px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 0.85rem; }
.form-group input, .form-group select { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
.form-actions { display: flex; gap: 8px; margin-top: 16px; }
.btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.btn-primary { background: #667eea; color: #fff; }
.btn-secondary { background: #6c757d; color: #fff; }
.btn-sm { padding: 4px 10px; font-size: 0.8rem; }
</style>
