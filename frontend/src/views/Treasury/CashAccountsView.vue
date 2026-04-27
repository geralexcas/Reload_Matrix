<template>
  <div class="cash-accounts-view">
    <div class="view-header">
      <h2>Cuentas de Caja</h2>
      <button class="btn btn-primary" @click="showCreateForm = true">+ Nueva Caja</button>
    </div>

    <div class="accounts-list">
      <div class="account-card" v-for="account in accounts" :key="account.id">
        <div class="account-info">
          <h3>{{ account.name }}</h3>
          <span class="badge" :class="'badge-' + account.account_type.toLowerCase()">{{ typeLabel(account.account_type) }}</span>
        </div>
        <div class="account-balance">
          <span class="balance-amount">{{ formatCurrency(account.current_balance) }}</span>
          <span class="currency">{{ account.currency }}</span>
        </div>
        <div class="account-actions">
          <button class="btn btn-sm btn-success" @click="openDeposit(account)">Depositar</button>
          <button class="btn btn-sm btn-warning" @click="openWithdraw(account)">Retirar</button>
          <button class="btn btn-sm btn-danger" @click="deleteAccount(account.id)" :disabled="account.current_balance != 0">Desactivar</button>
        </div>
      </div>
    </div>

    <div v-if="accounts.length === 0" class="empty">No hay cuentas de caja registradas.</div>

    <div class="modal-overlay" v-if="showCreateForm" @click.self="showCreateForm = false">
      <div class="modal">
        <h3>Nueva Cuenta de Caja</h3>
        <form @submit.prevent="createAccount">
          <div class="form-group">
            <label>Nombre:</label>
            <input v-model="createForm.name" required placeholder="Ej: Caja principal" />
          </div>
          <div class="form-group">
            <label>Tipo:</label>
            <select v-model="createForm.account_type">
              <option value="MAIN_CASH">Caja Principal</option>
              <option value="PETTY_CASH">Caja Menor</option>
              <option value="REGISTER_CASH">Caja Registro</option>
            </select>
          </div>
          <div class="form-group">
            <label>Saldo inicial:</label>
            <input v-model.number="createForm.initial_balance" type="number" step="0.01" min="0" />
          </div>
          <div class="form-group" v-if="createForm.account_type === 'PETTY_CASH'">
            <label>Monto máximo caja menor:</label>
            <input v-model.number="createForm.max_petty_cash_amount" type="number" step="0.01" />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Crear</button>
            <button type="button" class="btn" @click="showCreateForm = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="showTxForm" @click.self="showTxForm = false">
      <div class="modal">
        <h3>{{ txType === 'deposit' ? 'Depositar' : 'Retirar' }}</h3>
        <p>Caja: {{ selectedAccount?.name }}</p>
        <form @submit.prevent="submitTransaction">
          <div class="form-group">
            <label>Monto:</label>
            <input v-model.number="txForm.amount" type="number" step="0.01" min="0.01" required />
          </div>
          <div class="form-group">
            <label>Descripción:</label>
            <input v-model="txForm.description" required />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Confirmar</button>
            <button type="button" class="btn" @click="showTxForm = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CashAccountsView',
  data() {
    return {
      showCreateForm: false,
      showTxForm: false,
      txType: 'deposit',
      selectedAccount: null,
      createForm: { name: '', account_type: 'MAIN_CASH', initial_balance: 0, max_petty_cash_amount: null },
      txForm: { amount: 0, description: '' }
    }
  },
  computed: {
    accounts() { return this.$store.state.treasury.cashAccounts }
  },
  mounted() {
    this.$store.dispatch('treasury/fetchCashAccounts')
  },
  methods: {
    formatCurrency(v) { return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(v || 0) },
    typeLabel(t) { return { MAIN_CASH: 'Caja Principal', PETTY_CASH: 'Caja Menor', REGISTER_CASH: 'Caja Registro' }[t] || t },
    async createAccount() {
      try {
        await this.$store.dispatch('treasury/createCashAccount', this.createForm)
        this.showCreateForm = false
        this.createForm = { name: '', account_type: 'MAIN_CASH', initial_balance: 0, max_petty_cash_amount: null }
        this.$store.dispatch('treasury/fetchCashAccounts')
      } catch (e) { alert(e.response?.data?.detail || 'Error') }
    },
    openDeposit(a) { this.selectedAccount = a; this.txType = 'deposit'; this.showTxForm = true; this.txForm = { amount: 0, description: '' } },
    openWithdraw(a) { this.selectedAccount = a; this.txType = 'withdraw'; this.showTxForm = true; this.txForm = { amount: 0, description: '' } },
    async submitTransaction() {
      try {
        const action = this.txType === 'deposit' ? 'treasury/deposit' : 'treasury/withdraw'
        await this.$store.dispatch(action, { account_type: 'CASH', account_id: this.selectedAccount.id, amount: this.txForm.amount, description: this.txForm.description, reference: '' })
        this.showTxForm = false
        this.$store.dispatch('treasury/fetchCashAccounts')
      } catch (e) { alert(e.response?.data?.detail || 'Error') }
    },
    async deleteAccount(id) {
      if (!confirm('¿Desactivar esta cuenta? El saldo debe ser cero.')) return
      try {
        await this.$store.dispatch('treasury/deleteCashAccount', id)
        this.$store.dispatch('treasury/fetchCashAccounts')
      } catch (e) { alert(e.response?.data?.detail || 'Error') }
    }
  }
}
</script>

<style scoped>
.cash-accounts-view { padding: 20px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.view-header h2 { margin: 0; }
.accounts-list { display: grid; gap: 16px; }
.account-card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); display: flex; flex-wrap: wrap; align-items: center; gap: 16px; }
.account-info { flex: 1; }
.account-info h3 { margin: 0 0 4px; }
.account-balance { text-align: right; min-width: 150px; }
.balance-amount { display: block; font-size: 1.4rem; font-weight: 700; color: #1a1a2e; }
.currency { font-size: 0.8rem; color: #999; }
.account-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-top: 4px; }
.badge-main_cash { background: #e3f2fd; color: #1565c0; }
.badge-petty_cash { background: #fff3e0; color: #e65100; }
.badge-register_cash { background: #e8f5e9; color: #2e7d32; }
.empty { text-align: center; padding: 40px; color: #999; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 12px; padding: 24px; max-width: 500px; width: 90%; }
.modal h3 { margin: 0 0 16px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 0.85rem; }
.form-group input, .form-group select { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
.form-actions { display: flex; gap: 8px; margin-top: 16px; }
.btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.btn-primary { background: #667eea; color: #fff; }
.btn-success { background: #38ef7d; color: #fff; }
.btn-warning { background: #f7b733; color: #fff; }
.btn-danger { background: #dc3545; color: #fff; }
.btn-sm { padding: 4px 10px; font-size: 0.8rem; }
</style>
