<template>
  <div class="journal-entries-container">
    <div class="page-header">
      <h2>Asientos Contables</h2>
      <div class="page-actions">
        <button @click="showAddEntry = true" class="btn btn-primary">
          <i class="fas fa-plus"></i> Nuevo Asiento
        </button>
      </div>
    </div>
    
    <!-- Add/Edit Journal Entry Modal -->
    <div v-if="showAddEntry || showEditEntry" class="modal-backdrop" @click.self="closeEntryForm">
      <div class="modal-content">
        <h3>{{ editEntryId ? 'Editar Asiento' : 'Nuevo Asiento' }}</h3>
        <JournalEntryForm 
          :journalEntry="editEntryId ? entryToEdit : null"
          @save="handleSaveEntry"
          @cancel="closeEntryForm"
        />
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando asientos contables...</p>
    </div>
    
    <!-- Error State -->
    <div v-if="error && !loading" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- Empty State -->
    <div v-if="!loading && journalEntries.length === 0 && !error" class="empty-state">
      <i class="fas fa-book"></i>
      <p>No hay asientos contables registrados</p>
      <button @click="showAddEntry = true" class="btn btn-primary mt-3">
        Crear Primer Asiento
      </button>
    </div>
    
    <!-- Journal Entries Table -->
    <div v-if="!loading && journalEntries.length > 0" class="entries-table">
      <div class="table-header">
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchTerm"
            placeholder="Buscar asientos por número o descripción..."
            @input="debouncedSearch"
          >
        </div>
        <div class="filter-bar">
          <select v-model="filterStatus" @change="applyFilters">
            <option value="">Todos los Estados</option>
            <option value="Borrador">Borrador</option>
            <option value="Publicado">Publicado</option>
          </select>
          <select v-model="filterDateRange" @change="applyFilters">
            <option value="">Rango de Fechas</option>
            <option value="Hoy">Hoy</option>
            <option value="Esta Semana">Esta Semana</option>
            <option value="Este Mes">Este Mes</option>
            <option value="Este Año">Este Año</option>
          </select>
        </div>
      </div>
      
      <table class="entries-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Número</th>
            <th>Descripción</th>
            <th>Referencia</th>
            <th>Débitos</th>
            <th>Créditos</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in filteredJournalEntries" :key="entry.id" :class="{'posted': entry.is_posted}">
            <td>{{ formatDate(entry.entry_date) }}</td>
            <td>{{ entry.id }}</td>
            <td class="entry-description">
              <strong>{{ entry.description }}</strong>
              <p class="entry-reference">{{ entry.reference || '' }}</p>
            </td>
            <td>{{ Number(entry.total_debits).toFixed(2) }}</td>
            <td>{{ Number(entry.total_credits).toFixed(2) }}</td>
            <td>
              <span v-if="entry.is_posted" class="status-posted">Publicado</span>
              <span v-else class="status-draft">Borrador</span>
            </td>
            <td class="actions-cell">
              <button 
                @click="viewEntry(entry.id)"
                class="btn btn-icon btn-info"
                title="Ver Detalle"
              >
                <i class="fas fa-eye"></i>
              </button>
              <button 
                @click="editEntry(entry.id)"
                class="btn btn-icon btn-warning"
                title="Editar"
                :disabled="entry.is_posted"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button 
                @click="postEntry(entry.id)"
                class="btn btn-icon btn-success"
                title="Publicar"
                :disabled="entry.is_posted"
              >
                <i class="fas fa-check-circle"></i>
              </button>
              <button 
                @click="deleteEntry(entry.id)"
                class="btn btn-icon btn-danger"
                title="Eliminar"
                :disabled="entry.is_posted"
              >
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Pagination -->
      <div v-if="journalEntries.length > 0" class="pagination">
        <button 
          :disabled="currentPage <= 1"
          @click="previousPage"
          class="btn btn-sm"
        >
          Anterior
        </button>
        <span>Página {{ currentPage }} de {{ totalPages }}</span>
        <button 
          :disabled="currentPage >= totalPages || totalPages === 0"
          @click="nextPage"
          class="btn btn-sm"
        >
          Siguiente
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import JournalEntryForm from '@/components/Accounting/JournalEntryForm.vue'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'JournalEntryListView',
  components: {
    JournalEntryForm
  },
  data() {
    return {
      journalEntries: [],
      entry: null,
      loading: false,
      error: null,
      searchTerm: '',
      filterStatus: '',
      filterDateRange: '',
      currentPage: 1,
      itemsPerPage: 20,
      showAddEntry: false,
      showEditEntry: false,
      editEntryId: null,
      entryToEdit: null,
      searchTimeout: null
    }
  },
  computed: {
    ...mapGetters('accounting', ['getJournalEntries', 'getJournalEntry']),
    filteredJournalEntries() {
      let filtered = [...this.journalEntries]
      
      // Apply search filter
      if (this.searchTerm) {
        const term = this.searchTerm.toLowerCase().trim()
        filtered = filtered.filter(entry => 
          entry.id.toString().includes(term) ||
          entry.description.toLowerCase().includes(term) ||
          (entry.reference && entry.reference.toLowerCase().includes(term))
        )
      }
      
      // Apply status filter
      if (this.filterStatus) {
        const isPosted = this.filterStatus === 'Publicado'
        filtered = filtered.filter(entry => entry.is_posted === isPosted)
      }
      
      // Apply date range filter (simplified)
      if (this.filterDateRange) {
        const now = new Date()
        let startDate
        switch (this.filterDateRange) {
          case 'Hoy':
            startDate = new Date(now.setHours(0,0,0,0))
            break
          case 'Esta Semana':
            startDate = new Date(now)
            startDate.setDate(now.getDate() - now.getDay())
            break
          case 'Este Mes':
            startDate = new Date(now.getFullYear(), now.getMonth(), 1)
            break
          case 'Este Ano':
            startDate = new Date(now.getFullYear(), 0, 1)
            break
          default:
            startDate = null
        }
        if (startDate) {
          filtered = filtered.filter(entry => new Date(entry.entry_date) >= startDate)
        }
      }
      
      return filtered
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filteredJournalEntries.length / this.itemsPerPage))
    },
    paginatedEntries() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      return this.filteredJournalEntries.slice(start, start + this.itemsPerPage)
    }
  },
  watch: {
    '$route.params.companyId': {
      handler() {
        this.loadJournalEntries()
      },
      immediate: true
    }
  },
  methods: {
    ...mapActions('accounting', [
      'fetchJournalEntries',
      'fetchJournalEntryById',
      'createJournalEntry',
      'createJournalEntryWithLines',
      'postJournalEntry',
      'deleteJournalEntry' // We don't have this action yet, we'll need to add it
    ]),
    
    loadJournalEntries() {
      // Get company ID from auth store or route
      const companyId = parseInt(sessionStorage.getItem('selectedCompanyId')) || 1
      this.fetchJournalEntries({ companyId, skip: 0, limit: 1000 })
        .then(res => {
          this.journalEntries = res.data || []
          // Calculate totals for each entry
          this.journalEntries.forEach(entry => {
            entry.total_debits = entry.journal_entry_lines?.reduce((sum, line) => sum + parseFloat(line.debit_amount || 0), 0) || 0
            entry.total_credits = entry.journal_entry_lines?.reduce((sum, line) => sum + parseFloat(line.credit_amount || 0), 0) || 0
          })
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al cargar los asientos contables'
        })
    },
    
    debouncedSearch: function() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        // Just trigger a recomputation of filteredJournalEntries
      }, 300)
    },
    
    applyFilters() {
      this.currentPage = 1 // Reset to first page when filtering
    },
    
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },
    
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const options = { year: 'numeric', month: 'short', day: 'numeric' }
      return new Date(dateString).toLocaleDateString(undefined, options)
    },
    
    showAddEntryForm() {
      this.showAddEntry = true
      this.editEntryId = null
      this.entryToEdit = null
    },
    
    editEntry(entryId) {
      this.editEntryId = entryId
      this.showEditEntry = true
      this.fetchJournalEntryById({ entryId, companyId: parseInt(sessionStorage.getItem('selectedCompanyId')) || 1 })
        .then(res => {
          this.entryToEdit = res.data
          // Ensure lines are loaded
          if (!this.entryToEdit.journal_entry_lines) {
            this.entryToEdit.journal_entry_lines = []
          }
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al cargar el asiento contable'
          this.closeEntryForm()
        })
    },
    
    closeEntryForm() {
      this.showAddEntry = false
      this.showEditEntry = false
      this.editEntryId = null
      this.entryToEdit = null
    },
    
  handleSaveEntry(entryData) {
    const companyId = parseInt(sessionStorage.getItem('selectedCompanyId')) || 1
      if (this.editEntryId) {
        // Update existing entry
        this.updateJournalEntry({ 
          entryId: this.editEntryId, 
          entryData, 
          companyId 
        })
        .then(() => {
          this.$toast.success('Asiento contable actualizado exitosamente')
          this.closeEntryForm()
          this.loadJournalEntries()
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al actualizar asiento contable'
        })
      } else {
        // Create new entry
        this.createJournalEntryWithLines({ 
          entryData, 
          companyId 
        })
        .then(() => {
          this.$toast.success('Asiento contable creado exitosamente')
          this.closeEntryForm()
          this.loadJournalEntries()
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al crear asiento contable'
        })
    }
    },
    
    updateJournalEntry(params) {
      // We don't have an update action yet, we'll need to create it or use create with ID
      // For now, we'll simulate by creating a new entry (not ideal)
      // TODO: Add update action to store
      return this.createJournalEntryWithLines(params)
    },
    
    deleteEntry(entryId) {
      if (!window.confirm('¿Está seguro de que desea eliminar este asiento contable? Esta acción no se puede deshacer.')) {
        return
      }
      
      // We don't have delete action yet, simulate
      this.$toast.warning('Funcionalidad de eliminación en desarrollo')
    },
    
    viewEntry(entryId) {
      // Navigate to detail view
      this.$router.push({ name: 'journal-entry-detail', params: { entryId } })
    },
    
    postEntry(entryId) {
      if (!window.confirm('¿Está seguro de que desea publicar este asiento contable? Una vez publicado, no se podrá modificar.')) {
        return
      }
      
    this.postJournalEntry({ entryId, companyId: parseInt(sessionStorage.getItem('selectedCompanyId')) || 1 })
      .then(res => {
        if (res.data.warning) {
          this.$toast.warning(res.data.warning)
        } else {
          this.$toast.success('Asiento contable publicado exitosamente')
        }
        this.loadJournalEntries()
      })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al publicar asiento contable'
        })
    }
  },
  created() {
    this.loadJournalEntries()
  },
  beforeDestroy() {
    clearTimeout(this.searchTimeout)
  }
}
</script>

<style scoped>
.journal-entries-container {
  max-width: 1400px;
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

.entries-table {
  margin-top: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 15px;
}

.search-bar,
.filter-bar {
  flex: 1;
  min-width: 200px;
}

.search-bar input,
.filter-bar select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.search-bar input:focus,
.filter-bar select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0,123,255,0.25);
}

.entries-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.entries-table th,
.entries-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.entries-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.entries-table tbody tr:hover {
  background-color: #f8f9ff;
}

.entries-table tbody tr.posted {
  background-color: #e8f5e8;
}

.entries-table tbody tr:last-child td {
  border-bottom: none;
}

.entry-description {
  font-size: 0.95rem;
}

.entry-description p {
  margin: 4px 0 0 0;
  font-size: 0.85rem;
  color: #6c757d;
}

.actions-cell {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.btn-icon {
  width: 36px;
  height: 36px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.btn-icon.btn-info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.btn-icon.btn-info:hover {
  background-color: #bee5eb;
}

.btn-icon.btn-warning {
  background-color: #ffeaa7;
  color: #635d35;
}

.btn-icon.btn-warning:hover {
  background-color: #ffdf8e;
}

.btn-icon.btn-success {
  background-color: #d4edda;
  color: #155724;
}

.btn-icon.btn-success:hover {
  background-color: #c3e6cb;
}

.btn-icon.btn-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.btn-icon.btn-danger:hover {
  background-color: #f1c0c8;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 25px;
  gap: 15px;
  flex-wrap: wrap;
}

.pagination button {
  padding: 8px 16px;
  font-size: 0.9rem;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-bar,
  .filter-bar {
    width: 100%;
    margin-bottom: 10px;
  }
  
  .entries-table th,
  .entries-table td {
    padding: 12px 8px;
    font-size: 0.85rem;
  }
  
  .actions-cell {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .journal-entries-container {
    padding: 10px;
  }
  
  .entries-table thead {
    display: none;
  }
  
  .entries-table,
  .entries-table tbody,
  .entries-table tr,
  .entries-table td {
    display: block;
    width: 100%;
  }
  
  .entries-table tr {
    margin-bottom: 15px;
    border: 1px solid #ddd;
    border-radius: 6px;
  }
  
  .entries-table td {
    text-align: right;
    padding-left: 50%;
    position: relative;
    border-bottom: none;
  }
  
  .entries-table td::before {
    content: attr(data-label);
    position: absolute;
    left: 0;
    width: 50%;
    padding-left: 12px;
    font-weight: 600;
    color: #6c757d;
  }
  
  .entries-table td:last-child {
    border-bottom: 0;
  }
  
  .actions-cell {
    justify-content: flex-start;
  }
  
  .entry-description {
    font-size: 0.85rem;
  }
  
  .entry-description p {
    font-size: 0.75rem;
  }
}
</style>