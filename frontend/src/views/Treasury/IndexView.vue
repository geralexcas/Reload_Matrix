<template>
  <div class="treasury-index">
    <div class="view-header">
      <h2>Tesorería</h2>
    </div>

    <div class="summary-cards" v-if="summary">
      <div class="summary-card card-blue">
        <h3>Total Bancos</h3>
        <p class="amount">{{ formatCurrency(summary.total_banks) }}</p>
      </div>
      <div class="summary-card card-green">
        <h3>Total Caja</h3>
        <p class="amount">{{ formatCurrency(summary.total_cash) }}</p>
      </div>
      <div class="summary-card card-purple">
        <h3>Total Tesorería</h3>
        <p class="amount">{{ formatCurrency(summary.total_treasury) }}</p>
      </div>
    </div>

    <div class="feature-grid">
      <router-link to="/treasury/bank-accounts" class="feature-card">
        <div class="icon">🏦</div>
        <h3>Cuentas Bancarias</h3>
        <p>Gestiona cuentas de banco, saldos y movimientos</p>
      </router-link>
      <router-link to="/treasury/cash-accounts" class="feature-card">
        <div class="icon">💵</div>
        <h3>Cuentas de Caja</h3>
        <p>Caja principal, caja menor y registros</p>
      </router-link>
      <router-link to="/treasury/transactions" class="feature-card">
        <div class="icon">📋</div>
        <h3>Transacciones</h3>
        <p>Historial de todos los movimientos de tesorería</p>
      </router-link>
      <router-link to="/treasury/transfers" class="feature-card">
        <div class="icon">🔄</div>
        <h3>Transferencias</h3>
        <p>Transfiere entre cuentas bancarias y de caja</p>
      </router-link>
      <router-link to="/treasury/checks" class="feature-card">
        <div class="icon">📝</div>
        <h3>Cheques</h3>
        <p>Emite, cobra y gestiona cheques</p>
      </router-link>
      <router-link to="/treasury/cash-flow" class="feature-card">
        <div class="icon">📊</div>
        <h3>Flujo de Caja</h3>
        <p>Analiza entradas y salidas de dinero</p>
      </router-link>
      <router-link to="/treasury/reconciliations" class="feature-card">
        <div class="icon">✅</div>
        <h3>Conciliación Bancaria</h3>
        <p>Concilia extractos bancarios con el sistema</p>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TreasuryIndexView',
  computed: {
    summary() {
      return this.$store.state.treasury.treasurySummary
    }
  },
  mounted() {
    this.$store.dispatch('treasury/fetchTreasurySummary')
  },
  methods: {
    formatCurrency(value) {
      return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value || 0)
    }
  }
}
</script>

<style scoped>
.treasury-index { padding: 20px; }
.view-header { margin-bottom: 24px; }
.view-header h2 { margin: 0; font-size: 1.8rem; color: #1a1a2e; }
.summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }
.summary-card { padding: 20px; border-radius: 12px; color: #fff; }
.summary-card h3 { margin: 0 0 8px; font-size: 0.9rem; opacity: 0.9; }
.summary-card .amount { margin: 0; font-size: 1.6rem; font-weight: 700; }
.card-blue { background: linear-gradient(135deg, #667eea, #764ba2); }
.card-green { background: linear-gradient(135deg, #11998e, #38ef7d); }
.card-purple { background: linear-gradient(135deg, #fc4a1a, #f7b733); }
.feature-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }
.feature-card { display: block; padding: 24px; background: #fff; border-radius: 12px; text-decoration: none; color: #333; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s, box-shadow 0.2s; }
.feature-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.feature-card .icon { font-size: 2.5rem; margin-bottom: 12px; }
.feature-card h3 { margin: 0 0 8px; font-size: 1.1rem; }
.feature-card p { margin: 0; font-size: 0.85rem; color: #666; }
</style>
