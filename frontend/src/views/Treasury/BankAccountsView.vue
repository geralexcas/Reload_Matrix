<template>
  <div class="bank-accounts-view">
    <div class="view-header">
      <h2>Cuentas Bancarias</h2>
      <button class="btn btn-primary" @click="showCreateForm = true">+ Nueva Cuenta</button>
    </div>

    <div class="accounts-list">
      <div class="account-card" v-for="account in accounts" :key="account.id">
        <div class="account-info">
          <h3>{{ account.name }}</h3>
          <p class="bank-name">{{ account.bank_name }}</p>
          <p class="account-number">****{{ account.account_number.slice(-4) }}</p>
          <span class="badge" :class="'badge-' + account.account_type.toLowerCase()">{{ account.account_type }}</span>
        </div>
        <div class="account-balance">
          <span class="balance-amount">{{ formatCurrency(account.current_balance) }}</span>
          <span class="currency">{{ account.currency }}</span>
        </div>
        <div class="account-actions">
          <button class="btn btn-sm btn-success" @click="openDeposit(account)">Depositar</button>
          <button class="btn btn-sm btn-warning" @click="openWithdraw(account)">Retirar</button>
          <button class="btn btn-sm btn-secondary" @click="viewTransactions(account)">Movimientos</button>
          <button class="btn btn-sm btn-danger" @click="deleteAccount(account.id)" :disabled="account.current_balance != 0">Desactivar</button>
        </div>
      </div>
    </div>

    <div v-if="accounts.length === 0" class="empty">
      No hay cuentas bancarias registradas.
    </div>

    <div class="modal-overlay" v-if="showCreateForm" @click.self="showCreateForm = false">
      <div class="modal">
        <h3>Nueva Cuenta Bancaria</h3>
        <form @submit.prevent="createAccount">
          <div class="form-group">
            <label>Nombre:</label>
            <input v-model="createForm.name" required placeholder="Ej: Cuenta principal Bancolombia" />
          </div>
          <div class="form-group">
            <label>Banco:</label>
            <input v-model="createForm.bank_name" required placeholder="Ej: Bancolombia" />
          </div>
          <div class="form-group">
            <label>Número de cuenta:</label>
            <input v-model="createForm.account_number" required />
          </div>
          <div class="form-group">
            <label>Tipo:</label>
            <select v-model="createForm.account_type">
              <option value="CHECKING">Cuenta Corriente</option>
              <option value="SAVINGS">Cuenta de Ahorros</option>
              <option value="TIME_DEPOSIT">Depósito a Término</option>
            </select>
          </div>
          <div class="form-group">
            <label>Sucursal:</label>
            <input v-model="createForm.branch_office" />
          </div>
          <div class="form-group">
            <label>Cuenta contable vinculada:</label>
            <select v-model="createForm.linked_account_id">
              <option :value="null">Seleccionar cuenta contable...</option>
              <option v-for="acct in treasuryAccounts" :key="acct.id" :value="acct.id">
                {{ acct.code }} - {{ acct.name }}
              </option>
            </select>
            <small class="hint">Cuenta del plan de cuentas donde se registrarán los movimientos</small>
          </div>
          <div class="form-group balance-section">
            <label>💰 Saldo inicial de la cuenta:</label>
            <input v-model.number="createForm.initial_balance" type="number" step="0.01" min="0" class="balance-input" placeholder="0.00" />
            <small class="hint">Monto con el que inicia esta cuenta bancaria. Si es cuenta nueva, dejar en 0.</small>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Crear Cuenta</button>
            <button type="button" class="btn" @click="showCreateForm = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="showTxForm" @click.self="showTxForm = false">
      <div class="modal">
        <h3>{{ txType === 'deposit' ? 'Depositar' : 'Retirar' }}</h3>
        <p>Cuenta: {{ selectedAccount?.bank_name }} - {{ selectedAccount?.name }}</p>
        <form @submit.prevent="submitTransaction">
          <div class="form-group">
            <label>Monto:</label>
            <input v-model.number="txForm.amount" type="number" step="0.01" min="0.01" required />
          </div>
          <div class="form-group">
            <label>Descripción:</label>
            <input v-model="txForm.description" required />
          </div>
          <div class="form-group">
            <label>Referencia:</label>
            <input v-model="txForm.reference" />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Confirmar</button>
            <button type="button" class="btn" @click="showTxForm = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="showTransactions" @click.self="showTransactions = false">
      <div class="modal modal-lg">
        <h3>Movimientos - {{ selectedAccount?.bank_name }}</h3>
        <table class="data-table" v-if="accountTransactions.length">
          <thead>
            <tr>
              <th>Tipo</th>
              <th>Monto</th>
              <th>Descripción</th>
              <th>Saldo Después</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tx in accountTransactions" :key="tx.id">
              <td>{{ tx.transaction_type }}</td>
              <td>{{ formatCurrency(tx.amount) }}</td>
              <td>{{ tx.description || '-' }}</td>
              <td>{{ formatCurrency(tx.balance_after) }}</td>
              <td>{{ formatDate(tx.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty">Sin movimientos.</p>
        <div class="form-actions">
          <button class="btn" @click="showTransactions = false">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BankAccountsView',
  data() {
    return {
      showCreateForm: false,
      showTxForm: false,
      showTransactions: false,
      txType: 'deposit',
      selectedAccount: null,
      accountTransactions: [],
      createForm: { name: '', bank_name: '', account_number: '', account_type: 'CHECKING', initial_balance: 0, branch_office: '', linked_account_id: null },
      txForm: { amount: 0, description: '', reference: '' }
    }
  },
  computed: {
    accounts() { return this.$store.state.treasury.bankAccounts },
    treasuryAccounts() {
      const all = this.$store.state.accounting.chartOfAccounts || []
      const treasuryCodes = ['111001', '111002', '111003', '111004', '111010', '111011', '111012', '111020', '111030', '111040']
      return all.filter(a => treasuryCodes.includes(a.code))
    }
  },
  mounted() {
    this.$store.dispatch('treasury/fetchBankAccounts')
    this.$store.dispatch('accounting/fetchChartOfAccounts')
  },
  methods: {
    formatCurrency(v) { return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(v || 0) },
    formatDate(d) { return new Date(d).toLocaleDateString('es-CO') },
    async createAccount() {
      try {
        await this.$store.dispatch('treasury/createBankAccount', this.createForm)
        this.showCreateForm = false
        this.createForm = { name: '', bank_name: '', account_number: '', account_type: 'CHECKING', initial_balance: 0, branch_office: '', linked_account_id: null }
        this.$store.dispatch('treasury/fetchBankAccounts')
      } catch (e) { alert(e.response?.data?.detail || 'Error al crear') }
    },
    openDeposit(account) { this.selectedAccount = account; this.txType = 'deposit'; this.showTxForm = true; this.txForm = { amount: 0, description: '', reference: '' } },
    openWithdraw(account) { this.selectedAccount = account; this.txType = 'withdraw'; this.showTxForm = true; this.txForm = { amount: 0, description: '', reference: '' } },
    async submitTransaction() {
      try {
        const action = this.txType === 'deposit' ? 'treasury/deposit' : 'treasury/withdraw'
        await this.$store.dispatch(action, { account_type: 'BANK', account_id: this.selectedAccount.id, amount: this.txForm.amount, description: this.txForm.description, reference: this.txForm.reference })
        this.showTxForm = false
        this.$store.dispatch('treasury/fetchBankAccounts')
        if (this.showTransactions) this.viewTransactions(this.selectedAccount)
      } catch (e) { alert(e.response?.data?.detail || 'Error') }
    },
    async viewTransactions(account) {
      this.selectedAccount = account
      try {
        const res = await this.$store._actions['treasury/fetchBankAccounts']
        const api = (await import('@/services/api')).default
        const r = await api.get(`${process.env.VUE_APP_API_URL}/api/v1/treasury/bank-accounts/${account.id}/transactions/`)
        this.accountTransactions = r.data
        this.showTransactions = true
      } catch (e) { this.accountTransactions = []; this.showTransactions = true }
    },
    async deleteAccount(id) {
      if (!confirm('¿Desactivar esta cuenta? El saldo debe ser cero.')) return
      try {
        await this.$store.dispatch('treasury/deleteBankAccount', id)
        this.$store.dispatch('treasury/fetchBankAccounts')
      } catch (e) { alert(e.response?.data?.detail || 'Error al desactivar') }
    }
  }
}
</script>

<style scoped>
.bank-accounts-view { padding: 20px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.view-header h2 { margin: 0; }
.accounts-list { display: grid; gap: 16px; }
.account-card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); display: flex; flex-wrap: wrap; align-items: center; gap: 16px; }
.account-info { flex: 1; min-width: 200px; }
.account-info h3 { margin: 0 0 4px; }
.bank-name { margin: 0; color: #666; font-size: 0.9rem; }
.account-number { margin: 0; color: #999; font-size: 0.85rem; font-family: monospace; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-top: 4px; }
.badge-checking { background: #e3f2fd; color: #1565c0; }
.badge-savings { background: #e8f5e9; color: #2e7d32; }
.badge-time_deposit { background: #fff3e0; color: #e65100; }
.account-balance { text-align: right; min-width: 150px; }
.balance-amount { display: block; font-size: 1.4rem; font-weight: 700; color: #1a1a2e; }
.currency { font-size: 0.8rem; color: #999; }
.account-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.empty { text-align: center; padding: 40px; color: #999; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 12px; padding: 24px; max-width: 500px; width: 90%; max-height: 90vh; overflow-y: auto; }
.modal-lg { max-width: 800px; }
.modal h3 { margin: 0 0 16px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 0.85rem; }
.form-group input, .form-group select { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9rem; box-sizing: border-box; }
.hint { display: block; color: #999; font-size: 0.75rem; margin-top: 4px; }
.balance-section { background: #f0f7ff; padding: 16px; border-radius: 8px; border: 2px solid #667eea; }
.balance-section label { font-size: 1rem; color: #1a1a2e; }
.balance-input { font-size: 1.2rem; font-weight: 700; border-color: #667eea; background: #fff; }
.form-actions { display: flex; gap: 8px; margin-top: 16px; }
.btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.btn-primary { background: #667eea; color: #fff; }
.btn-success { background: #38ef7d; color: #fff; }
.btn-warning { background: #f7b733; color: #fff; }
.btn-secondary { background: #6c757d; color: #fff; }
.btn-danger { background: #dc3545; color: #fff; }
.btn-sm { padding: 4px 10px; font-size: 0.8rem; }
.data-table { width: 100%; border-collapse: collapse; margin-bottom: 12px; }
.data-table th, .data-table td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 0.85rem; }
.data-table th { background: #f8f9fa; font-weight: 600; }
</style>
