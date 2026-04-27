<template>
  <div class="chart-of-accounts-container">
    <div class="page-header">
      <h2>Plan de Cuentas</h2>
      <div class="page-actions">
        <button @click="showAddAccount = true" class="btn btn-primary">
          <i class="fas fa-plus"></i> Nueva Cuenta
        </button>
      </div>
    </div>
    
    <!-- Add/Edit Account Modal -->
    <div v-if="showAddAccount || showEditAccount" class="modal-backdrop" @click.self="closeAccountForm">
      <div class="modal-content">
        <h3>{{ editAccountId ? 'Editar Cuenta' : 'Nueva Cuenta' }}</h3>
        <AccountForm 
          :account="editAccountId ? accountToEdit : null"
          @save="handleSaveAccount"
          @cancel="closeAccountForm"
        />
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando plan de cuentas...</p>
    </div>
    
    <!-- Error State -->
    <div v-if="error && !loading" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- Empty State -->
    <div v-if="!loading && chartOfAccounts.length === 0 && !error" class="empty-state">
      <i class="fas fa-list"></i>
      <p>No hay cuentas contables registradas</p>
      <button @click="showAddAccount = true" class="btn btn-primary mt-3">
        Crear Primera Cuenta
      </button>
    </div>
    
    <!-- Accounts Tree -->
    <div v-if="!loading && chartOfAccounts.length > 0" class="accounts-tree">
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchTerm"
          placeholder="Buscar cuentas por código o nombre..."
          @input="debouncedSearch"
        >
      </div>
      
      <div class="tree-container">
        <div v-for="account in filteredChartOfAccounts" 
             :key="account.id" 
             class="account-item"
             :class="{'is-parent': account.children && account.children.length > 0, 'has-children': account.children && account.children.length > 0}"
        >
          <div class="account-header" @click="toggleChildren(account.id)">
            <div class="account-icon">
              <template v-if="account.children && account.children.length > 0">
                <i class="fas" :class="{'fa-chevron-down': account.expanded, 'fa-chevron-right': !account.expanded}"></i>
              </template>
              <template v-else>
                <i class="fas fa-circle"></i>
              </template>
            </div>
            <div class="account-info">
              <div class="account-code">{{ account.code }}</div>
              <div class="account-name">{{ account.name }}</div>
            </div>
            <div class="account-type-badge">
              <span :class="getTypeClass(account.account_type)">{{ getTypeLabel(account.account_type) }}</span>
            </div>
          </div>
          
          <div v-if="account.expanded && account.children && account.children.length > 0" class="children-accounts">
            <div v-for="child in account.children" 
                 :key="child.id" 
                 class="child-account-item"
            >
              <div class="child-account-header">
                <div class="child-account-icon">
                  <i class="fas fa-minus-circle"></i>
                </div>
                <div class="child-account-info">
                  <div class="child-account-code">{{ child.code }}</div>
                  <div class="child-account-name">{{ child.name }}</div>
                </div>
                <div class="child-account-type-badge">
                  <span :class="getTypeClass(child.account_type)">{{ getTypeLabel(child.account_type) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AccountForm from '@/components/Accounting/AccountForm.vue'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'ChartOfAccountsListView',
  components: {
    AccountForm
  },
  data() {
    return {
      chartOfAccounts: [],
      account: null,
      loading: false,
      error: null,
      searchTerm: '',
      showAddAccount: false,
      showEditAccount: false,
      editAccountId: null,
      accountToEdit: null,
      searchTimeout: null
    }
  },
  computed: {
    ...mapGetters('accounting', ['getChartOfAccounts', 'getChartOfAccount']),
    filteredChartOfAccounts() {
      // First, get root accounts (those without parent_id or parent_id = null)
      const rootAccounts = this.chartOfAccounts.filter(acc => !acc.parent_id)
      
      // Apply search filter
      if (this.searchTerm) {
        const term = this.searchTerm.toLowerCase().trim()
        const filteredRoots = rootAccounts.filter(acc => 
          acc.code.toLowerCase().includes(term) ||
          acc.name.toLowerCase().includes(term)
        )
        
        // For each matching root, include all its children
        const result = []
        filteredRoots.forEach(root => {
          // Add the root
          result.push({ ...root, children: [] })
          // Add all children of this root
          const children = this.chartOfAccounts.filter(acc => acc.parent_id === root.id)
          children.forEach(child => {
            result[result.length - 1].children.push({ ...child, children: [] })
          })
        })
        
        return result
      }
      
      // No search term, return all with children
      const result = []
      rootAccounts.forEach(root => {
        const rootCopy = { ...root, children: [] }
        const children = this.chartOfAccounts.filter(acc => acc.parent_id === root.id)
        children.forEach(child => {
          rootCopy.children.push({ ...child, children: [] })
        })
        result.push(rootCopy)
      })
      
      return result
    }
  },
  watch: {
    '$route.params.companyId': {
      handler() {
        this.loadChartOfAccounts()
      },
      immediate: true
    }
  },
  methods: {
    ...mapActions('accounting', [
      'fetchChartOfAccounts',
      'fetchChartOfAccountById',
      'createChartOfAccount',
      'updateChartOfAccount',
      'deleteChartOfAccount'
    ]),
    
    loadChartOfAccounts() {
      // Get company ID from auth store or route
      const companyId = this.$route.params.companyId || 1 // Default for now
      this.fetchChartOfAccounts({ companyId, skip: 0, limit: 1000 })
        .then(res => {
          this.chartOfAccounts = res.data || []
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al cargar el plan de cuentas'
        })
    },
    
    debouncedSearch: function() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        // Just trigger a recomputation of filteredChartOfAccounts
      }, 300)
    },
    
    toggleChildren(accountId) {
      const account = this.chartOfAccounts.find(acc => acc.id === accountId)
      if (account) {
        account.expanded = !account.expanded
      }
    },
    
    showAddAccountForm() {
      this.showAddAccount = true
      this.editAccountId = null
      this.accountToEdit = null
    },
    
    editAccount(accountId) {
      this.editAccountId = accountId
      this.showEditAccount = true
      this.fetchChartOfAccountById({ accountId, companyId: this.$route.params.companyId || 1 })
        .then(res => {
          this.accountToEdit = res.data
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al cargar cuenta contable'
          this.closeAccountForm()
        })
    },
    
    closeAccountForm() {
      this.showAddAccount = false
      this.showEditAccount = false
      this.editAccountId = null
      this.accountToEdit = null
    },
    
    handleSaveAccount(accountData) {
      const companyId = this.$route.params.companyId || 1
      if (this.editAccountId) {
        // Update existing account
        this.updateChartOfAccount({ 
          accountId: this.editAccountId, 
          accountData, 
          companyId 
        })
        .then(() => {
          this.$toast.success('Cuenta contable actualizada exitosamente')
          this.closeAccountForm()
          this.loadChartOfAccounts()
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al actualizar cuenta contable'
        })
      } else {
        // Create new account
        this.createChartOfAccount({ 
          accountData, 
          companyId 
        })
        .then(() => {
          this.$toast.success('Cuenta contable creada exitosamente')
          this.closeAccountForm()
          this.loadChartOfAccounts()
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al crear cuenta contable'
        })
    }
    },
    
    deleteAccount(accountId) {
      if (!window.confirm('¿Está seguro de que desea eliminar esta cuenta contable? Esta acción no se puede deshacer si tiene subcuentas o movimientos asociados.')) {
        return
      }
      
      this.deleteChartOfAccount({ accountId, companyId: this.$route.params.companyId || 1 })
        .then(() => {
          this.$toast.success('Cuenta contable eliminada exitosamente')
          this.loadChartOfAccounts()
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al eliminar cuenta contable'
        })
    },
    
    getTypeClass(accountType) {
      switch (accountType) {
        case 'ASSET': return 'type-asset'
        case 'LIABILITY': return 'type-liability'
        case 'EQUITY': return 'type-equity'
        case 'REVENUE': return 'type-revenue'
        case 'EXPENSE': return 'type-expense'
        default: return ''
      }
    },
    
    getTypeLabel(accountType) {
      switch (accountType) {
        case 'ASSET': return 'Activo'
        case 'LIABILITY': return 'Pasivo'
        case 'EQUITY': return 'Patrimonio'
        case 'REVENUE': return 'Ingreso'
        case 'EXPENSE': return 'Gasto'
        default: return accountType
      }
    }
  },
  created() {
    this.loadChartOfAccounts()
  },
  beforeDestroy() {
    clearTimeout(this.searchTimeout)
  }
}
</script>

<style scoped>
.chart-of-accounts-container {
  max-width: 1000px;
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
  flex-wrap: wrap;
}

.loading-state,
.empty-state,
.alert {
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

.empty-state i {
  font-size: 4rem;
  color: #6c757d;
  margin-bottom: 20px;
}

.empty-state button {
  margin-top: 15px;
}

.accounts-tree {
  margin-top: 20px;
}

.search-bar {
  margin-bottom: 20px;
}

.search-bar input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.search-bar input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0,123,255,0.25);
}

.tree-container {
  max-height: 600px;
  overflow-y: auto;
}

.account-item,
.child-account-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 6px;
  background-color: #f8f9fa;
  margin-bottom: 4px;
  transition: background-color 0.2s;
}

.account-item:hover,
.child-account-item:hover {
  background-color: #e9ecef;
}

.account-item.is-parent {
  cursor: pointer;
  font-weight: 500;
}

.account-item.has-children {
  border-left: 3px solid #007bff;
}

.child-account-item {
  background-color: #fff;
  margin-left: 20px;
}

.account-header,
.child-account-header {
  display: flex;
  align-items: center;
  width: 100%;
}

.account-icon,
.child-account-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: #e9ecef;
  color: #495057;
  font-size: 0.9rem;
  margin-right: 12px;
}

.account-info,
.child-account-info {
  flex: 1;
  min-width: 0;
}

.account-code,
.child-account-code {
  font-weight: 600;
  color: #495057;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.account-name,
.child-account-name {
  color: #2c3e50;
  font-size: 0.9rem;
  margin-top: 2px;
}

.account-type-badge,
.child-account-type-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.type-asset {
  background-color: #d4edda;
  color: #155724;
  border-color: #c3e6cb;
}

.type-liability {
  background-color: #f8d7da;
  color: #721c24;
  border-color: #f5c6cb;
}

.type-equity {
  background-color: #d1ecf1;
  color: #0c5460;
  border-color: #bee5eb;
}

.type-revenue {
  background-color: #fff3cd;
  color: #856404;
  border-color: #ffeaa7;
}

.type-expense {
  background-color: #f8d7da;
  color: #721c24;
  border-color: #f5c6cb;
}

/* Responsive design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .page-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>