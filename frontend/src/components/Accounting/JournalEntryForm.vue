<template>
  <form @submit.prevent="onSubmit" class="journal-entry-form">
    <div class="form-group">
      <label for="entry_date">Fecha:*</label>
      <input 
        type="date" 
        id="entry_date" 
        v-model="form.entry_date" 
        required
        :disabled="isPosted"
      />
    </div>
    
    <div class="form-group">
      <label for="description">Descripción:*</label>
      <input 
        type="text" 
        id="description" 
        v-model="form.description" 
        required
        maxlength="500"
        :disabled="isPosted"
        placeholder="Descripción del asiento contable"
      />
    </div>
    
    <div class="form-group">
      <label for="reference">Referencia (opcional):</label>
      <input 
        type="text" 
        id="reference" 
        v-model="form.reference" 
        maxlength="100"
        :disabled="isPosted"
        placeholder="Número de factura, documento, etc."
      />
    </div>
    
    <div v-if="isPosted" class="alert alert-info">
      <strong>Asiento publicado:</strong> No se puede modificar
    </div>
    
    <div class="form-group">
      <label>Líneas del Asiento:</label>
      <div class="journal-lines-container">
        <div v-if="form.lines.length === 0" class="empty-lines">
          <p>No hay líneas en este asiento. Agregue al menos una línea.</p>
        </div>
        
        <div v-for="(line, index) in form.lines" :key="index" class="journal-line-item">
          <div class="line-header">
            <h4>Línea {{ index + 1 }}</h4>
            <button 
              @click="removeLine(index)" 
              class="btn btn-icon btn-danger"
              :disabled="isPosted || form.lines.length <= 1"
              title="Eliminar línea"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="line-content">
            <div class="line-field-group">
              <label :for="`account_${index}`">Cuenta Contable:*</label>
              <select 
                :id="`account_${index}`"
                v-model="line.account_id"
                required
                :disabled="isPosted"
              >
                <option value="">Seleccione una cuenta</option>
                <option 
                  v-for="account in chartOfAccounts" 
                  :key="account.id" 
                  :value="account.id"
                >
                  {{ account.code }} - {{ account.name }}
                </option>
              </select>
            </div>
            
            <div class="line-field-group">
              <label :for="`description_${index}`">Descripción de la Línea:</label>
              <input 
                :id="`description_${index}`"
                type="text"
                v-model="line.description"
                maxlength="255"
                :disabled="isPosted"
              />
            </div>
            
            <div class="line-field-group">
              <label :for="`debit_${index}`">Débito:*</label>
              <input 
                :id="`debit_${index}`"
                type="number"
                v-model.number="line.debit_amount"
                required
                min="0"
                step="0.01"
                :disabled="isPosted"
                @change="calculateTotals"
              />
            </div>
            
            <div class="line-field-group">
              <label :for="`credit_${index}`">Crédito:*</label>
              <input 
                :id="`credit_${index}`"
                type="number"
                v-model.number="line.credit_amount"
                required
                min="0"
                step="0.01"
                :disabled="isPosted"
                @change="calculateTotals"
              />
            </div>
          </div>
          
          <div class="line-validation" v-if="lineErrors[index]">
            <p class="text-danger">{{ lineErrors[index] }}</p>
          </div>
        </div>
        
        <div class="line-actions">
          <button 
            @click="addLine"
            class="btn btn-outline btn-primary"
            :disabled="isPosted"
          >
            <i class="fas fa-plus"></i> Agregar Línea
          </button>
        </div>
      </div>
    </div>
    
    <div class="form-group totals-section">
      <div class="totals-row">
        <span class="totals-label">Total Débitos:</span>
        <span class="totals-value">{{ formatCurrency(totalDebits) }}</span>
      </div>
      <div class="totals-row">
        <span class="totals-label">Total Créditos:</span>
        <span class="totals-value">{{ formatCurrency(totalCredits) }}</span>
      </div>
      <div class="totals-row balance-check">
        <span class="totals-label">Diferencia:</span>
        <span class="totals-value" :class="{'balanced': isBalanced, 'not-balanced': !isBalanced}">
          {{ formatCurrency(totalDebits - totalCredits) }}
        </span>
      </div>
    </div>
    
    <div class="form-actions">
      <button 
        type="button" 
        @click="cancel" 
        class="btn btn-outline"
        :disabled="isSubmitting"
      >
        Cancelar
      </button>
      <button 
        type="submit" 
        :disabled="isSubmitting || !isValid || isPosted"
        class="btn btn-primary"
      >
        {{ isSubmitting ? 'Guardando...' : (editMode ? 'Actualizar' : 'Crear') }}
      </button>
    </div>
  </form>
</template>

<script>
export default {
  name: 'JournalEntryForm',
  props: {
    journalEntry: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      form: {
        entry_date: '',
        description: '',
        reference: '',
        lines: []
      },
      editMode: false,
      isSubmitting: false,
      lineErrors: [],
      chartOfAccounts: [],
      isPosted: false,
      isLoading: false
    }
  },
  computed: {
    totalDebits() {
      return this.form.lines.reduce((sum, line) => sum + parseFloat(line.debit_amount || 0), 0)
    },
    totalCredits() {
      return this.form.lines.reduce((sum, line) => sum + parseFloat(line.credit_amount || 0), 0)
    },
    isBalanced() {
      return Math.abs(this.totalDebits - this.totalCredits) < 0.01
    },
    isValid() {
      // Basic validation
      if (!this.form.entry_date || !this.form.description) {
        return false
      }
      
      if (this.form.lines.length === 0) {
        return false
      }
      
      // Check each line
      for (let i = 0; i < this.form.lines.length; i++) {
        const line = this.form.lines[i]
        if (!line.account_id || line.account_id === '' ||
            isNaN(parseFloat(line.debit_amount || 0)) ||
            isNaN(parseFloat(line.credit_amount || 0))) {
          return false
        }
        
        // At least one of debit or credit must be greater than 0
        if (parseFloat(line.debit_amount || 0) === 0 && parseFloat(line.credit_amount || 0) === 0) {
          return false
        }
      }
      
      return this.isBalanced
    }
  },
  watch: {
    journalEntry: {
      handler(newVal) {
        if (newVal) {
          this.editMode = true
          this.isPosted = newVal.is_posted
          this.form = {
            entry_date: newVal.entry_date,
            description: newVal.description,
            reference: newVal.reference || '',
            lines: newVal.journal_entry_lines ? [...newVal.journal_entry_lines] : []
          }
          // Load chart of accounts
          this.loadChartOfAccounts()
        }
      },
      immediate: true
    }
  },
  methods: {
    addLine() {
      this.form.lines.push({
        account_id: '',
        description: '',
        debit_amount: 0,
        credit_amount: 0
      })
      // Clear error for new line
      this.lineErrors.push('')
    },
    
    removeLine(index) {
      if (this.form.lines.length > 1 && !this.isPosted) {
        this.form.lines.splice(index, 1)
        this.lineErrors.splice(index, 1)
      }
    },
    
    calculateTotals() {
      // This method is called from @change on inputs
      // We could add real-time validation here if needed
    },
    
    validateForm() {
      this.lineErrors = []
      let isValid = true
      
      if (!this.form.entry_date) {
        isValid = false
        // Date error would be handled by HTML5 validation
      }
      
      if (!this.form.description || this.form.description.trim() === '') {
        isValid = false
        // Description error
      }
      
      if (this.form.lines.length === 0) {
        isValid = false
        this.lineErrors.push('El asiento debe tener al menos una línea')
      }
      
      // Validate each line
      this.form.lines.forEach((line, index) => {
        let lineError = ''
        
        if (!line.account_id || line.account_id === '') {
          lineError += 'Seleccione una cuenta contable. '
          isValid = false
        }
        
        const debit = parseFloat(line.debit_amount || 0)
        const credit = parseFloat(line.credit_amount || 0)
        
        if (isNaN(debit) || debit < 0) {
          lineError += 'El débito debe ser un número válido. '
          isValid = false
        }
        
        if (isNaN(credit) || credit < 0) {
          lineError += 'El crédito debe ser un número válido. '
          isValid = false
        }
        
        if (debit === 0 && credit === 0) {
          lineError += 'Al menos uno de débito o crédito debe ser mayor a cero. '
          isValid = false
        }
        
        this.lineErrors[index] = lineError.trim()
      })
      
      // Check balance
      if (!this.isBalanced && this.form.lines.length > 0) {
        isValid = false
        // We'll show this in the totals section
      }
      
      return isValid
    },
    
    onSubmit() {
      if (!this.validateForm()) {
        return
      }
      
      this.isSubmitting = true
      this.$emit('save', this.form)
    },
    
    cancel() {
      this.isSubmitting = false
      this.$emit('cancel')
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP'
      }).format(amount)
    },
    
    loadChartOfAccounts() {
      // This would normally fetch from the store or API
      // For now, we'll simulate with an empty array
      // In a real implementation, we'd fetch from the accounting store
      this.isLoading = true
      // Simulate API call
      setTimeout(() => {
        // This would be replaced with actual store fetch
        this.chartOfAccounts = [
          { id: 1, code: '1110', name: 'Efectivo y equivalentes' },
          { id: 2, code: '1130', name: 'Cuentas por cobrar' },
          { id: 3, code: '1140', name: 'Inventarios' },
          { id: 4, code: '2110', name: 'Cuentas por pagar' },
          { id: 5, code: '4100', name: 'Ingresos por ventas' },
          { id: 6, code: '5100', name: 'Costo de ventas' },
          { id: 7, code: '6100', name: 'Gastos de administración' }
        ]
        this.isLoading = false
      }, 500)
    }
  },
  created() {
    // If we're editing an existing entry, load chart of accounts
    if (this.journalEntry) {
      this.loadChartOfAccounts()
    }
  }
}
</script>

<style scoped>
.journal-entry-form {
  max-width: 800px;
  width: 100%;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.875rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 3px rgba(0,123,255,0.25);
}

.form-group input[disabled],
.form-group select[disabled],
.form-group textarea[disabled] {
  background-color: #e9ecef;
  cursor: not-allowed;
}

.form-group .form-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: #dc3545;
}

.form-error {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  border-radius: 6px;
  padding: 10px 16px;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0069d9;
}

.btn-primary:active {
  background-color: #0062cc;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  background-color: transparent;
  color: #007bff;
  border: 2px solid #007bff;
}

.btn-outline:hover {
  background-color: #007bff;
  color: white;
}

.journal-lines-container {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
  background-color: #f8f9fa;
}

.empty-lines {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 20px;
}

.journal-line-item {
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-bottom: 10px;
  overflow: hidden;
}

.line-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #e9ecef;
  padding: 10px 15px;
  border-bottom: 1px solid #dee2e6;
}

.line-header h4 {
  margin: 0;
  font-size: 1rem;
  color: #495057;
}

.btn-icon {
  width: 30px;
  height: 30px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.line-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  padding: 15px;
}

.line-field-group {
  margin-bottom: 0;
}

.line-field-group label {
  display: block;
  margin-bottom: 0.3rem;
  font-weight: 500;
  color: #495057;
  font-size: 0.875rem;
}

.line-field-group input,
.line-field-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.875rem;
}

.line-field-group input:focus,
.line-field-group select:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

.line-validation {
  margin-top: 5px;
}

.totals-section {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 20px;
  margin-top: 20px;
}

.totals-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.totals-row:last-child {
  border-bottom: none;
}

.totals-label {
  font-weight: 600;
  color: #495057;
}

.totals-value {
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

.alert {
  padding: 12px;
  margin-bottom: 1rem;
  border-radius: 4px;
}

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
  border-color: #bee5eb;
}
</style>