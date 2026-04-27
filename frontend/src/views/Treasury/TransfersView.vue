<template>
  <div class="transfers-view">
    <div class="view-header">
      <h2>Transferencias entre Cuentas</h2>
    </div>

    <div class="transfer-form-card">
      <form @submit.prevent="submitTransfer">
        <div class="transfer-row">
          <div class="transfer-side">
            <h3>Desde</h3>
            <div class="form-group">
              <label>Tipo:</label>
              <select v-model="form.fromType" @change="loadFromAccounts">
                <option value="BANK">Banco</option>
                <option value="CASH">Caja</option>
              </select>
            </div>
            <div class="form-group">
              <label>Cuenta:</label>
              <select v-model="form.fromId" required>
                <option value="">Seleccionar...</option>
                <option v-for="a in fromAccounts" :key="a.id" :value="a.id">
                  {{ a.name }} ({{ formatCurrency(a.current_balance) }})
                </option>
              </select>
            </div>
          </div>

          <div class="transfer-arrow">→</div>

          <div class="transfer-side">
            <h3>Hacia</h3>
            <div class="form-group">
              <label>Tipo:</label>
              <select v-model="form.toType" @change="loadToAccounts">
                <option value="BANK">Banco</option>
                <option value="CASH">Caja</option>
              </select>
            </div>
            <div class="form-group">
              <label>Cuenta:</label>
              <select v-model="form.toId" required>
                <option value="">Seleccionar...</option>
                <option v-for="a in toAccounts" :key="a.id" :value="a.id">
                  {{ a.name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Monto a transferir:</label>
          <input v-model.number="form.amount" type="number" step="0.01" min="0.01" required />
        </div>
        <div class="form-group">
          <label>Descripción:</label>
          <input v-model="form.description" placeholder="Motivo de la transferencia" />
        </div>
        <div class="form-group">
          <label>Referencia:</label>
          <input v-model="form.reference" placeholder="N° referencia (opcional)" />
        </div>

        <button type="submit" class="btn btn-primary">Realizar Transferencia</button>
      </form>
    </div>

    <div v-if="message" :class="['message', messageType === 'success' ? 'msg-success' : 'msg-error']">
      {{ message }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'TransfersView',
  data() {
    return {
      form: { fromType: 'BANK', fromId: '', toType: 'CASH', toId: '', amount: 0, description: '', reference: '' },
      message: '',
      messageType: 'success'
    }
  },
  computed: {
    bankAccounts() { return this.$store.state.treasury.bankAccounts },
    cashAccounts() { return this.$store.state.treasury.cashAccounts },
    fromAccounts() { return this.form.fromType === 'BANK' ? this.bankAccounts : this.cashAccounts },
    toAccounts() { return this.form.toType === 'BANK' ? this.bankAccounts : this.cashAccounts }
  },
  mounted() {
    this.$store.dispatch('treasury/fetchBankAccounts')
    this.$store.dispatch('treasury/fetchCashAccounts')
  },
  methods: {
    formatCurrency(v) { return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(v || 0) },
    loadFromAccounts() { this.form.fromId = '' },
    loadToAccounts() { this.form.toId = '' },
    async submitTransfer() {
      this.message = ''
      if (!this.form.fromId || !this.form.toId) { this.message = 'Selecciona ambas cuentas'; this.messageType = 'error'; return }
      if (this.form.fromType === this.form.toType && this.form.fromId === this.form.toId) { this.message = 'No puedes transferir a la misma cuenta'; this.messageType = 'error'; return }
      try {
        await this.$store.dispatch('treasury/transfer', {
          from_account_type: this.form.fromType,
          from_account_id: this.form.fromId,
          to_account_type: this.form.toType,
          to_account_id: this.form.toId,
          amount: this.form.amount,
          description: this.form.description,
          reference: this.form.reference
        })
        this.message = 'Transferencia realizada con éxito'
        this.messageType = 'success'
        this.form = { fromType: 'BANK', fromId: '', toType: 'CASH', toId: '', amount: 0, description: '', reference: '' }
        this.$store.dispatch('treasury/fetchBankAccounts')
        this.$store.dispatch('treasury/fetchCashAccounts')
      } catch (e) { this.message = e.response?.data?.detail || 'Error'; this.messageType = 'error' }
    }
  }
}
</script>

<style scoped>
.transfers-view { padding: 20px; }
.view-header { margin-bottom: 24px; }
.view-header h2 { margin: 0; }
.transfer-form-card { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); max-width: 800px; }
.transfer-row { display: flex; gap: 20px; align-items: flex-start; margin-bottom: 16px; }
.transfer-side { flex: 1; }
.transfer-side h3 { margin: 0 0 8px; font-size: 1rem; color: #667eea; }
.transfer-arrow { font-size: 2rem; color: #667eea; padding-top: 30px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 0.85rem; }
.form-group input, .form-group select { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
.btn { padding: 10px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
.btn-primary { background: #667eea; color: #fff; }
.message { margin-top: 16px; padding: 12px 16px; border-radius: 6px; }
.msg-success { background: #e8f5e9; color: #2e7d32; }
.msg-error { background: #ffebee; color: #c62828; }
</style>
