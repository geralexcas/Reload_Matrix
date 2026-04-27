<template>
  <div class="check-register-view">
    <div class="view-header">
      <h2>Registro de Cheques</h2>
      <button class="btn btn-primary" @click="showIssueForm = true">+ Emitir Cheque</button>
    </div>

    <div class="filters">
      <div class="filter-group">
        <label>Banco:</label>
        <select v-model="filters.bankId" @change="loadChecks">
          <option value="">Todos</option>
          <option v-for="a in bankAccounts" :key="a.id" :value="a.id">{{ a.bank_name }} - {{ a.name }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Estado:</label>
        <select v-model="filters.status" @change="loadChecks">
          <option value="">Todos</option>
          <option value="ISSUED">Emitido</option>
          <option value="DELIVERED">Entregado</option>
          <option value="CLEARED">Cobrado</option>
          <option value="BOUNCED">Devuelto</option>
          <option value="VOIDED">Anulado</option>
        </select>
      </div>
    </div>

    <table class="data-table" v-if="checks.length">
      <thead>
        <tr>
          <th>N° Cheque</th>
          <th>Banco</th>
          <th>Beneficiario</th>
          <th>Monto</th>
          <th>Fecha Emisión</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="chk in checks" :key="chk.id">
          <td class="mono">{{ chk.check_number }}</td>
          <td>{{ bankName(chk.bank_account_id) }}</td>
          <td>{{ chk.payee }}</td>
          <td>{{ formatCurrency(chk.amount) }}</td>
          <td>{{ formatDate(chk.issue_date) }}</td>
          <td><span class="badge" :class="statusBadge(chk.status)">{{ statusLabel(chk.status) }}</span></td>
          <td>
            <button v-if="chk.status === 'ISSUED'" class="btn btn-sm btn-secondary" @click="updateStatus(chk.id, 'DELIVERED')">Entregar</button>
            <button v-if="chk.status === 'DELIVERED'" class="btn btn-sm btn-success" @click="updateStatus(chk.id, 'CLEARED')">Cobrar</button>
            <button v-if="chk.status === 'DELIVERED'" class="btn btn-sm btn-danger" @click="updateStatus(chk.id, 'BOUNCED')">Devolver</button>
            <button v-if="['ISSUED','DELIVERED'].includes(chk.status)" class="btn btn-sm btn-warning" @click="updateStatus(chk.id, 'VOIDED')">Anular</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="checks.length === 0" class="empty">No hay cheques registrados.</div>

    <div class="modal-overlay" v-if="showIssueForm" @click.self="showIssueForm = false">
      <div class="modal">
        <h3>Emitir Cheque</h3>
        <form @submit.prevent="issueCheck">
          <div class="form-group">
            <label>Cuenta bancaria:</label>
            <select v-model="form.bank_account_id" required>
              <option value="">Seleccionar...</option>
              <option v-for="a in bankAccounts" :key="a.id" :value="a.id">{{ a.bank_name }} - {{ a.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Número de cheque:</label>
            <input v-model="form.check_number" required />
          </div>
          <div class="form-group">
            <label>Beneficiario:</label>
            <input v-model="form.payee" required />
          </div>
          <div class="form-group">
            <label>Monto:</label>
            <input v-model.number="form.amount" type="number" step="0.01" min="0.01" required />
          </div>
          <div class="form-group">
            <label>Fecha de emisión:</label>
            <input v-model="form.issue_date" type="datetime-local" required />
          </div>
          <div class="form-group">
            <label>Notas:</label>
            <textarea v-model="form.notes" rows="2"></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Emitir</button>
            <button type="button" class="btn" @click="showIssueForm = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CheckRegisterView',
  data() {
    return {
      showIssueForm: false,
      filters: { bankId: '', status: '' },
      form: { bank_account_id: '', check_number: '', payee: '', amount: 0, issue_date: '', notes: '' }
    }
  },
  computed: {
    checks() { return this.$store.state.treasury.checks },
    bankAccounts() { return this.$store.state.treasury.bankAccounts }
  },
  mounted() {
    this.$store.dispatch('treasury/fetchBankAccounts')
    this.loadChecks()
  },
  methods: {
    loadChecks() {
      this.$store.dispatch('treasury/fetchChecks', {
        bankAccountId: this.filters.bankId || null,
        status: this.filters.status || null
      })
    },
    formatCurrency(v) { return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(v || 0) },
    formatDate(d) { return new Date(d).toLocaleDateString('es-CO') },
    bankName(id) { const a = this.bankAccounts.find(x => x.id === id); return a ? `${a.bank_name} (${a.name})` : '#' + id },
    statusLabel(s) { return { ISSUED: 'Emitido', DELIVERED: 'Entregado', CLEARED: 'Cobrado', BOUNCED: 'Devuelto', VOIDED: 'Anulado' }[s] || s },
    statusBadge(s) { return { ISSUED: 'badge-blue', DELIVERED: 'badge-orange', CLEARED: 'badge-green', BOUNCED: 'badge-red', VOIDED: 'badge-gray' }[s] || '' },
    async issueCheck() {
      try {
        await this.$store.dispatch('treasury/issueCheck', this.form)
        this.showIssueForm = false
        this.form = { bank_account_id: '', check_number: '', payee: '', amount: 0, issue_date: '', notes: '' }
        this.loadChecks()
        this.$store.dispatch('treasury/fetchBankAccounts')
      } catch (e) { alert(e.response?.data?.detail || 'Error') }
    },
    async updateStatus(id, status) {
      if (!confirm(`¿Cambiar estado a ${this.statusLabel(status)}?`)) return
      try {
        await this.$store.dispatch('treasury/updateCheckStatus', { checkId: id, status })
        this.loadChecks()
        this.$store.dispatch('treasury/fetchBankAccounts')
      } catch (e) { alert(e.response?.data?.detail || 'Error') }
    }
  }
}
</script>

<style scoped>
.check-register-view { padding: 20px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.view-header h2 { margin: 0; }
.filters { display: flex; gap: 16px; margin-bottom: 20px; }
.filter-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 0.8rem; }
.filter-group select { padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 0.85rem; }
.data-table th { background: #f8f9fa; font-weight: 600; }
.mono { font-family: monospace; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.badge-blue { background: #e3f2fd; color: #1565c0; }
.badge-orange { background: #fff3e0; color: #e65100; }
.badge-green { background: #e8f5e9; color: #2e7d32; }
.badge-red { background: #ffebee; color: #c62828; }
.badge-gray { background: #f5f5f5; color: #616161; }
.empty { text-align: center; padding: 40px; color: #999; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 12px; padding: 24px; max-width: 500px; width: 90%; }
.modal h3 { margin: 0 0 16px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 0.85rem; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
.form-actions { display: flex; gap: 8px; margin-top: 16px; }
.btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.btn-primary { background: #667eea; color: #fff; }
.btn-success { background: #38ef7d; color: #fff; }
.btn-warning { background: #f7b733; color: #fff; }
.btn-danger { background: #dc3545; color: #fff; }
.btn-secondary { background: #6c757d; color: #fff; }
.btn-sm { padding: 4px 10px; font-size: 0.8rem; }
</style>
