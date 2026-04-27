<template>
  <div class="journal-entry-detail-container">
    <div class="page-header">
      <h2>Detalle del Asiento Contable</h2>
      <div class="page-actions">
        <router-link :to="{ name: 'journal-entry-edit', params: { entryId: journalEntry.id } }" 
                     v-if="!journalEntry.is_posted"
                     class="btn btn-outline btn-primary">
          <i class="fas fa-edit"></i> Editar
        </router-link>
        <button 
          v-if="!journalEntry.is_posted"
          @click="postEntry"
          class="btn btn-outline btn-success"
        >
          <i class="fas fa-check-circle"></i> Publicar
        </button>
        <router-link to="/accounting/journal-entries" class="btn btn-outline">
          <i class="fas fa-arrow-left"></i> Volver a la lista
        </router-link>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando asiento contable...</p>
    </div>
    
    <!-- Error State -->
    <div v-if="error && !loading" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- Journal Entry Details -->
    <div v-if="!loading && journalEntry" class="entry-details">
      <div class="entry-header">
        <div class="entry-info">
          <h3>Asiento Contable #{{ journalEntry.id }}</h3>
          <p><strong>Fecha:</strong> {{ formatDate(journalEntry.entry_date) }}</p>
          <p><strong>Descripción:</strong> {{ journalEntry.description }}</p>
          <p v-if="journalEntry.reference"><strong>Referencia:</strong> {{ journalEntry.reference }}</p>
        </div>
        <div class="entry-status">
          <span :class="[ 'status-badge', journalEntry.is_posted ? 'status-posted' : 'status-draft' ]">
            {{ journalEntry.is_posted ? 'Publicado' : 'Borrador' }}
          </span>
        </div>
      </div>
      
      <div class="entry-divider"></div>
      
      <div class="entry-summary">
        <h3>Resumen</h3>
        <div class="summary-items">
          <div class="summary-item">
            <span class="summary-label">Total Débitos:</span>
            <span class="summary-value">{{ formatCurrency(totalDebits) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Total Créditos:</span>
            <span class="summary-value">{{ formatCurrency(totalCredits) }}</span>
          </div>
          <div class="summary-item balance-check">
            <span class="summary-label">Balance:</span>
            <span class="summary-value" :class="{'balanced': isBalanced, 'not-balanced': !isBalanced}">
              {{ formatCurrency(totalDebits - totalCredits) }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="entry-divider"></div>
      
      <div class="entry-lines">
        <h3>Líneas del Asiento ({{ journalEntry.journal_entry_lines?.length || 0 }})</h3>
        <div v-if="!journalEntry.journal_entry_lines || journalEntry.journal_entry_lines.length === 0" class="empty-lines">
          <p>No hay líneas en este asiento.</p>
        </div>
        <table v-else class="lines-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Cuenta Contable</th>
              <th>Descripción</th>
              <th>Débito</th>
              <th>Crédito</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(line, index) in journalEntry.journal_entry_lines" :key="index">
              <td>{{ index + 1 }}</td>
              <td>
                <div class="account-code">{{ line.account?.code || '' }}</div>
                <div class="account-name">{{ line.account?.name || 'Cuenta no encontrada' }}</div>
              </td>
              <td class="line-description">{{ line.description || '' }}</td>
              <td class="amount-debit">{{ formatCurrency(line.debit_amount || 0) }}</td>
              <td class="amount-credit">{{ formatCurrency(line.credit_amount || 0) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'JournalEntryDetailView',
  data() {
    return {
      journalEntry: null,
      loading: false,
      error: null
    }
  },
  computed: {
    ...mapGetters('accounting', ['getJournalEntry']),
    totalDebits() {
      return this.journalEntry?.journal_entry_lines?.reduce((sum, line) => sum + parseFloat(line.debit_amount || 0), 0) || 0
    },
    totalCredits() {
      return this.journalEntry?.journal_entry_lines?.reduce((sum, line) => sum + parseFloat(line.credit_amount || 0), 0) || 0
    },
    isBalanced() {
      return Math.abs(this.totalDebits - this.totalCredits) < 0.01
    }
  },
  watch: {
    '$route.params.entryId': {
      handler() {
        this.loadJournalEntry()
      },
      immediate: true
    }
  },
  methods: {
    ...mapActions('accounting', [
      'fetchJournalEntryById',
      'postJournalEntry'
    ]),
    
    loadJournalEntry() {
      const entryId = this.$route.params.entryId
      if (!entryId) {
        this.error = 'ID de asiento no proporcionado'
        return
      }
      
      this.loading = true
      this.error = null
      
      // Get company ID from route or auth (we'll need to pass it or get from store)
      // For simplicity, we'll get it from the journal entry once we have it, but the API needs it
      // We'll assume we can get it from the route or default to 1
      const companyId = this.$route.params.companyId || 1
      
      this.fetchJournalEntryById({ entryId, companyId })
        .then(res => {
          this.journalEntry = res.data
          // Ensure we have the lines
          if (!this.journalEntry.journal_entry_lines) {
            this.journalEntry.journal_entry_lines = []
          }
          // Load account details for each line (in a real app, we'd eager load or fetch separately)
          // For now, we'll just note that the account relation should be loaded by the API
          this.loading = false
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al cargar el asiento contable'
          this.loading = false
        })
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const options = { year: 'numeric', month: 'short', day: 'numeric' }
      return new Date(dateString).toLocaleDateString(undefined, options)
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP'
      }).format(amount)
    },
    
    postEntry() {
      if (!this.journalEntry) return
      
      if (!window.confirm('¿Está seguro de que desea publicar este asiento contable? Una vez publicado, no se podrá modificar.')) {
        return
      }
      
      this.postJournalEntry({ entryId: this.journalEntry.id, companyId: this.$route.params.companyId || 1 })
        .then(() => {
          this.$toast.success('Asiento contable publicado exitosamente')
          // Refresh the entry to show updated status
          this.loadJournalEntry()
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al publicar asiento contable'
        })
    }
  }
}
</script>

<style scoped>
.journal-entry-detail-container {
  max-width: 800px;
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

.entry-details {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.entry-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 25px;
  border-bottom: 1px solid #eee;
}

.entry-info {
  flex: 2;
}

.entry-info h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.entry-info p {
  margin: 0 0 8px 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.entry-status {
  flex: 1;
  text-align: right;
}

.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-posted {
  background-color: #d4edda;
  color: #155724;
}

.status-draft {
  background-color: #fff3cd;
  color: #856404;
}

.entry-divider {
  height: 2px;
  background-color: #eee;
  margin: 25px 0;
}

.entry-summary {
  padding: 25px;
}

.entry-summary h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
}

.summary-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
}

.summary-label {
  font-weight: 500;
  color: #6c757d;
}

.summary-value {
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.balance-check {
  font-weight: bold;
}

.balanced {
  color: #28a745;
}

.not-balanced {
  color: #dc3545;
}

.entry-lines {
  padding: 25px;
}

.entry-lines h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
}

.empty-lines {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 40px;
}

.lines-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.lines-table th,
.lines-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.lines-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.lines-table tbody tr:hover {
  background-color: #f8f9ff;
}

.lines-table tbody tr:last-child td {
  border-bottom: none;
}

.account-code {
  font-weight: 600;
  color: #495057;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
}

.account-name {
  color: #6c757d;
  font-size: 0.85rem;
  margin-top: 2px;
}

.line-description {
  color: #6c757d;
  font-size: 0.85rem;
}

.amount-debit,
.amount-credit {
  font-weight: 600;
  font-family: 'Courier New', monospace;
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
  
  .entry-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .entry-info {
    margin-bottom: 20px;
  }
}
</style>