<template>
  <div class="wallet-view">
    <div class="view-header">
      <div class="header-title">
        <h2>💰 Monedero Electrónico</h2>
        <p class="text-muted">Gestión de saldos, anticipos y puntos de fidelidad.</p>
      </div>
      <button class="btn btn-primary" @click="openCreateForm">+ Nuevo Monedero</button>
    </div>

    <!-- Filtros y Búsqueda -->
    <div class="card filters-card mb-4">
      <div class="filter-group">
        <input v-model="searchQuery" placeholder="Buscar por socio o ID..." class="search-input" />
        <select v-model="filterCurrency" class="filter-select">
          <option value="">Todas las monedas</option>
          <option value="COP">COP</option>
          <option value="USD">USD</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Cargando monederos...</p>
    </div>

    <div v-else class="wallets-grid">
      <div class="wallet-card" v-for="wallet in filteredWallets" :key="wallet.id">
        <div class="wallet-status" :class="{ active: wallet.is_active }">
          {{ wallet.is_active ? 'Activo' : 'Inactivo' }}
        </div>
        <div class="wallet-header">
          <div class="wallet-info">
            <span class="wallet-id">#{{ wallet.id }}</span>
            <h3 class="partner-name">{{ wallet.partner_name || 'Sin Socio Vinculado' }}</h3>
          </div>
          <div class="balance-display">
            <span class="balance-amount">{{ formatCurrency(wallet.balance, wallet.currency) }}</span>
            <span class="loyalty-badge" v-if="wallet.loyalty_points > 0">
              ⭐ {{ wallet.loyalty_points }} pts
            </span>
          </div>
        </div>
        
        <div class="wallet-footer">
          <div class="action-buttons">
            <button class="btn-action deposit" @click="openDeposit(wallet)" title="Depositar">
              <span>⬇️</span> Ingreso
            </button>
            <button class="btn-action withdraw" @click="openWithdraw(wallet)" title="Retirar">
              <span>⬆️</span> Retiro
            </button>
            <button class="btn-action history" @click="viewTransactions(wallet)" title="Movimientos">
              <span>📜</span> Historial
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && filteredWallets.length === 0" class="empty-state">
      <div class="empty-icon">📂</div>
      <p>No se encontraron monederos.</p>
      <button class="btn btn-outline" @click="openCreateForm">Crear el primero</button>
    </div>

    <!-- Modal Crear Monedero -->
    <div class="modal-overlay" v-if="showCreateForm" @click.self="showCreateForm = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Crear Nuevo Monedero</h3>
          <button class="close-btn" @click="showCreateForm = false">×</button>
        </div>
        <form @submit.prevent="createWallet">
          <div class="form-group">
            <label>Seleccionar Socio (Opcional):</label>
            <select v-model="createForm.partner_id" class="form-control">
              <option :value="null">-- Ninguno --</option>
              <option v-for="p in partners" :key="p.id" :value="p.id">
                {{ p.name }} ({{ p.nit }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Moneda:</label>
            <select v-model="createForm.currency" class="form-control">
              <option value="COP">COP - Peso Colombiano</option>
              <option value="USD">USD - Dólar</option>
            </select>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCreateForm = false">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? 'Guardando...' : 'Crear Monedero' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Transacción (Depósito/Retiro) -->
    <div class="modal-overlay" v-if="showTransactionForm" @click.self="showTransactionForm = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>{{ txType === 'deposit' ? 'Registrar Ingreso' : 'Registrar Retiro' }}</h3>
          <button class="close-btn" @click="showTransactionForm = false">×</button>
        </div>
        <form @submit.prevent="submitTransaction">
          <div class="transaction-summary">
            <div class="label">Socio:</div>
            <div class="value">{{ selectedWallet?.partner_name || 'Sin Socio' }}</div>
          </div>
          <div class="form-group">
            <label>Monto ({{ selectedWallet?.currency }}):</label>
            <input v-model.number="txForm.amount" type="number" step="0.01" min="0.01" required class="form-control amount-input" />
          </div>
          <div class="form-group">
            <label>Concepto / Descripción:</label>
            <textarea v-model="txForm.description" required class="form-control" rows="3" placeholder="Ej: Anticipo para reparación #123"></textarea>
          </div>
          <div class="form-group">
            <label>Cuenta de Tesorería a afectar (Opcional):</label>
            <select v-model="txForm.treasuryAccount" class="form-control">
              <option :value="null">-- Ninguna (Solo afecta el saldo del monedero) --</option>
              <optgroup label="Cajas">
                <option v-for="c in cashAccounts" :key="'cash-'+c.id" :value="{type: 'CASH', id: c.id}">
                  {{ c.name }}
                </option>
              </optgroup>
              <optgroup label="Bancos">
                <option v-for="b in bankAccounts" :key="'bank-'+b.id" :value="{type: 'BANK', id: b.id}">
                  {{ b.bank_name }} - {{ b.account_number }}
                </option>
              </optgroup>
            </select>
            <small class="text-muted" style="font-size: 0.8rem; margin-top: 5px; display: block;">
              Selecciona una cuenta si el dinero entra/sale realmente de caja o bancos.
            </small>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showTransactionForm = false">Cancelar</button>
            <button type="submit" class="btn" :class="txType === 'deposit' ? 'btn-success' : 'btn-warning'" :disabled="submitting">
              {{ submitting ? 'Procesando...' : (txType === 'deposit' ? 'Confirmar Ingreso' : 'Confirmar Retiro') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Historial -->
    <div class="modal-overlay" v-if="showTransactions" @click.self="showTransactions = false">
      <div class="modal modal-lg card">
        <div class="modal-header">
          <h3>Movimientos - {{ selectedWallet?.partner_name || 'Monedero #' + selectedWallet?.id }}</h3>
          <button class="close-btn" @click="showTransactions = false">×</button>
        </div>
        <div class="transactions-list">
          <table class="data-table" v-if="transactions.length">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Concepto</th>
                <th class="text-right">Monto</th>
                <th class="text-right">Saldo</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tx in transactions" :key="tx.id">
                <td class="text-muted">{{ formatDate(tx.created_at) }}</td>
                <td>
                  <span class="badge" :class="tx.transaction_type.toLowerCase()">
                    {{ translateTxType(tx.transaction_type) }}
                  </span>
                </td>
                <td class="description-cell">{{ tx.description || '-' }}</td>
                <td class="text-right" :class="tx.transaction_type === 'DEPOSIT' ? 'text-success' : 'text-danger'">
                  {{ tx.transaction_type === 'DEPOSIT' ? '+' : '-' }} {{ formatCurrency(tx.amount, selectedWallet?.currency) }}
                </td>
                <td class="text-right font-weight-bold">
                  {{ formatCurrency(tx.balance_after, selectedWallet?.currency) }}
                </td>
                <td class="text-center" v-if="tx.transaction_type === 'DEPOSIT'">
                  <button class="btn-print-mini" @click="openPrintReceipt(tx)" title="Imprimir Recibo">
                    🖨️
                  </button>
                </td>
                <td v-else></td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty-state">
            <p>No hay movimientos registrados.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showTransactions = false">Cerrar</button>
        </div>
      </div>
    </div>

    <!-- Modal de Impresión de Recibo -->
    <WalletReceiptModal
      v-if="showReceiptPrint"
      :show="showReceiptPrint"
      :transaction="selectedTxForPrint"
      :partnerName="selectedWallet?.partner_name"
      :partnerNit="selectedWalletPartnerNit"
      :company="currentCompany"
      @close="showReceiptPrint = false"
    />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import WalletReceiptModal from '@/components/Wallet/WalletReceiptModal.vue'

export default {
  name: 'WalletView',
  components: {
    WalletReceiptModal
  },
  data() {
    return {
      searchQuery: '',
      filterCurrency: '',
      showCreateForm: false,
      showTransactionForm: false,
      showTransactions: false,
      showReceiptPrint: false,
      selectedWallet: null,
      selectedTxForPrint: null,
      txType: 'deposit',
      submitting: false,
      createForm: { 
        partner_id: null, 
        currency: 'COP' 
      },
      txForm: { 
        amount: 0, 
        description: '',
        treasuryAccount: null
      },
      transactions: []
    }
  },
  computed: {
    wallets() {
      return this.$store.getters['wallet/getWallets']
    },
    partners() {
      return this.$store.getters['partners/getPartners']
    },
    loading() {
      return this.$store.getters['wallet/isLoading']
    },
    cashAccounts() {
      return this.$store.getters['treasury/getCashAccounts'] || [];
    },
    bankAccounts() {
      return this.$store.getters['treasury/getBankAccounts'] || [];
    },
    companyId() {
      return this.$store.getters['company/getCompany']?.id || 1
    },
    currentCompany() {
      return this.$store.getters['company/getCompany'] || {}
    },
    selectedWalletPartnerNit() {
      if (!this.selectedWallet?.partner_id) return '';
      const partner = this.partners.find(p => p.id === this.selectedWallet.partner_id);
      return partner ? partner.nit : '';
    },
    filteredWallets() {
      return this.wallets.filter(w => {
        const matchesSearch = !this.searchQuery || 
          w.id.toString().includes(this.searchQuery) ||
          (w.partner_name && w.partner_name.toLowerCase().includes(this.searchQuery.toLowerCase()))
        
        const matchesCurrency = !this.filterCurrency || w.currency === this.filterCurrency
        
        return matchesSearch && matchesCurrency
      })
    }
  },
  async mounted() {
    await this.refreshData()
  },
  methods: {
    async refreshData() {
      await Promise.all([
        this.$store.dispatch('wallet/fetchWallets', { companyId: this.companyId }),
        this.$store.dispatch('partners/fetchPartners', { companyId: this.companyId }),
        this.$store.dispatch('treasury/fetchCashAccounts'),
        this.$store.dispatch('treasury/fetchBankAccounts')
      ])
    },
    openCreateForm() {
      this.createForm = { partner_id: null, currency: 'COP' }
      this.showCreateForm = true
    },
    async createWallet() {
      this.submitting = true
      try {
        await this.$store.dispatch('wallet/createWallet', {
          walletData: this.createForm,
          companyId: this.companyId
        })
        this.showCreateForm = false
        await this.refreshData()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.detail || err.message))
      } finally {
        this.submitting = false
      }
    },
    openDeposit(wallet) {
      this.selectedWallet = wallet
      this.txType = 'deposit'
      this.txForm = { amount: 0, description: '', treasuryAccount: null }
      this.showTransactionForm = true
    },
    openWithdraw(wallet) {
      this.selectedWallet = wallet
      this.txType = 'withdraw'
      this.txForm = { amount: 0, description: '', treasuryAccount: null }
      this.showTransactionForm = true
    },
    async submitTransaction() {
      this.submitting = true
      try {
        const action = this.txType === 'deposit' ? 'deposit' : 'withdraw'
        await this.$store.dispatch(`wallet/${action}`, {
          walletId: this.selectedWallet.id,
          amount: this.txForm.amount,
          description: this.txForm.description,
          companyId: this.companyId,
          accountType: this.txForm.treasuryAccount ? this.txForm.treasuryAccount.type : null,
          accountId: this.txForm.treasuryAccount ? this.txForm.treasuryAccount.id : null
        })
        this.showTransactionForm = false
        await this.refreshData()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.detail || err.message))
      } finally {
        this.submitting = false
      }
    },
    async viewTransactions(wallet) {
      this.selectedWallet = wallet
      try {
        const res = await this.$store.dispatch('wallet/fetchTransactions', {
          walletId: wallet.id,
          companyId: this.companyId
        })
        this.transactions = res.data || []
        this.showTransactions = true
      } catch (err) {
        alert('Error al cargar historial')
      }
    },
    openPrintReceipt(tx) {
      this.selectedTxForPrint = tx;
      this.showReceiptPrint = true;
    },
    formatCurrency(value, currency = 'COP') {
      return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0
      }).format(value)
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString('es-CO', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      })
    },
    translateTxType(type) {
      const types = {
        'DEPOSIT': 'Ingreso',
        'WITHDRAWAL': 'Retiro',
        'TRANSFER_IN': 'Transf. Entrada',
        'TRANSFER_OUT': 'Transf. Salida'
      }
      return types[type] || type
    }
  }
}
</script>

<style scoped>
.wallet-view {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  text-align: left;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header-title h2 { margin-bottom: 0.25rem; font-size: 1.75rem; }

/* Filtros */
.filters-card {
  padding: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.filter-group {
  display: flex;
  gap: 1rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.95rem;
}

.filter-select {
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  min-width: 150px;
}

/* Wallets Grid */
.wallets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
}

.wallet-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  position: relative;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #f0f0f0;
}

.wallet-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.wallet-status {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 20px;
  text-transform: uppercase;
  font-weight: bold;
}

.wallet-status.active { background: #e8f5e9; color: #2e7d32; }

.wallet-id {
  font-size: 0.8rem;
  color: #9e9e9e;
  font-weight: 600;
}

.partner-name {
  margin: 0.25rem 0 1rem 0;
  font-size: 1.15rem;
  color: #1a1a2e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.balance-display {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance-amount {
  font-size: 1.5rem;
  font-weight: 800;
  color: #28a745;
}

.loyalty-badge {
  background: #fff3e0;
  color: #f57c00;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: bold;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  flex: 1;
  padding: 0.6rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  transition: opacity 0.2s;
}

.btn-action:hover { opacity: 0.85; }
.btn-action.deposit { background: #e3f2fd; color: #1976d2; }
.btn-action.withdraw { background: #fff3e0; color: #e65100; }
.btn-action.history { background: #f5f5f5; color: #616161; }

/* Modales */
.modal-overlay {
  position: fixed;
  top:0; left:0; right:0; bottom:0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  width: 90%;
  max-width: 450px;
  padding: 2rem;
  border-radius: 20px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #999; }

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  margin-top: 0.5rem;
}

.amount-input {
  font-size: 1.5rem;
  font-weight: bold;
  color: #28a745;
  text-align: center;
}

.transaction-summary {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
}

.transaction-summary .label { color: #666; }
.transaction-summary .value { font-weight: bold; }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 2rem;
}

/* Tabla de Movimientos */
.modal-lg { max-width: 800px; }
.transactions-list { max-height: 400px; overflow-y: auto; margin: 1rem 0; }

.data-table { width: 100%; border-collapse: collapse; }
.data-table th { padding: 12px; background: #f8f9fa; border-bottom: 2px solid #eee; text-align: left; }
.data-table td { padding: 12px; border-bottom: 1px solid #eee; }

.badge { padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
.badge.deposit { background: #e8f5e9; color: #2e7d32; }
.badge.withdrawal { background: #ffebee; color: #c62828; }

.text-success { color: #28a745; }
.text-danger { color: #dc3545; }
.text-right { text-align: right; }
.font-weight-bold { font-weight: bold; }

.empty-state { text-align: center; padding: 4rem 2rem; color: #999; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }

.btn { padding: 0.75rem 1.5rem; border-radius: 10px; border: none; cursor: pointer; font-weight: 600; }
.btn-primary { background: #1a1a2e; color: white; }
.btn-success { background: #28a745; color: white; }
.btn-warning { background: #ffc107; color: #333; }
.btn-secondary { background: #e0e0e0; color: #666; }
.btn-outline { background: transparent; border: 1px solid #1a1a2e; color: #1a1a2e; }

.loading-container { text-align: center; padding: 4rem; }
.spinner { border: 4px solid #f3f3f3; border-top: 4px solid #1a1a2e; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.btn-print-mini {
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 1.2rem;
  transition: all 0.2s;
}
.btn-print-mini:hover {
  background: #e0e0e0;
  transform: scale(1.1);
}
.text-center { text-align: center; }
</style>
