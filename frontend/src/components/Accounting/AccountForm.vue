<template>
  <form @submit.prevent="onSubmit" class="account-form">
    <div class="form-group">
      <label for="code">Código Contable:*</label>
      <input 
        type="text" 
        id="code" 
        v-model="form.code" 
        required
        maxlength="20"
        placeholder="Ej: 1100, 1110, etc."
      />
      <small class="form-text">Código único según el plan de cuentas colombiano</small>
    </div>
    
    <div class="form-group">
      <label for="name">Nombre de la Cuenta:*</label>
      <input 
        type="text" 
        id="name" 
        v-model="form.name" 
        required
        maxlength="255"
        placeholder="Nombre descriptivo de la cuenta"
      />
    </div>
    
    <div class="form-group">
      <label for="description">Descripción:</label>
      <textarea 
        id="description" 
        v-model="form.description" 
        maxlength="500"
        rows="3"
        placeholder="Detalles adicionales sobre la cuenta"
      ></textarea>
    </div>
    
    <div class="form-group">
      <label for="account_type">Tipo de Cuenta:*</label>
      <select 
        id="account_type" 
        v-model="form.account_type" 
        required
      >
        <option value="">Seleccione un tipo</option>
        <option value="ASSET">Activo</option>
        <option value="LIABILITY">Pasivo</option>
        <option value="EQUITY">Patrimonio</option>
        <option value="REVENUE">Ingreso</option>
        <option value="EXPENSE">Gasto</option>
      </select>
    </div>
    
    <div class="form-group" v-if="form.account_type">
      <label for="parent_id">Cuenta Padre (opcional):</label>
      <select 
        id="parent_id" 
        v-model="form.parent_id"
      >
        <option value="">Nivel Principal (sin cuenta padre)</option>
        <option 
          v-for="account in parentAccounts" 
          :key="account.id" 
          :value="account.id"
        >
          {{ account.code }} - {{ account.name }}
        </option>
      </select>
      <small class="form-text">Seleccione una cuenta padre para crear subcuentas</small>
    </div>
    
    <div class="form-group">
      <label for="is_active">Estado:</label>
      <div class="form-check">
        <input 
          type="checkbox" 
          id="is_active" 
          v-model="form.is_active"
          :true-value="true"
          :false-value="false"
        >
        <label for="is_active">Cuenta activa</label>
      </div>
    </div>
    
    <div class="form-actions">
      <button 
        type="button" 
        @click="cancel" 
        class="btn btn-outline"
      >
        Cancelar
      </button>
      <button 
        type="submit" 
        :disabled="isLoading"
        class="btn btn-primary"
      >
        {{ isLoading ? 'Guardando...' : (editMode ? 'Actualizar' : 'Crear') }}
      </button>
    </div>
  </form>
</template>

<script>
export default {
  name: 'AccountForm',
  props: {
    account: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      form: {
        code: '',
        name: '',
        description: '',
        account_type: '',
        parent_id: null,
        is_active: true
      },
      editMode: false,
      isLoading: false,
      parentAccounts: [],
      errors: {}
    }
  },
  watch: {
    account: {
      handler(newVal) {
        if (newVal) {
          this.editMode = true
          this.form = { ...newVal }
          // Convert parent_id to null if it's 0 or undefined
          this.form.parent_id = this.form.parent_id || null
        }
      },
      immediate: true
    }
  },
  methods: {
    validateForm() {
      this.errors = {}
      let isValid = true
      
      if (!this.form.code || this.form.code.trim() === '') {
        this.errors.code = 'El código contable es requerido'
        isValid = false
      } else {
        // Validate code format (numbers and possibly letters)
        if (!/^[A-Z0-9]+$/.test(this.form.code.toUpperCase())) {
          this.errors.code = 'El código solo puede contener letras y números'
          isValid = false
        }
      }
      
      if (!this.form.name || this.form.name.trim() === '') {
        this.errors.name = 'El nombre es requerido'
        isValid = false
      }
      
      if (!this.form.account_type) {
        this.errors.account_type = 'El tipo de cuenta es requerido'
        isValid = false
      }
      
      // Validate that parent is not the same as self (when editing)
      if (this.form.parent_id && this.editMode && this.form.parent_id == this.account.id) {
        this.errors.parent_id = 'Una cuenta no puede ser padre de sí misma'
        isValid = false
      }
      
      return isValid
    },
    
    onSubmit() {
      if (!this.validateForm()) {
        return
      }
      
      this.isLoading = true
      this.$emit('save', this.form)
    },
    
    cancel() {
      this.isLoading = false
      this.$emit('cancel')
    }
  },
  created() {
    // Load parent accounts for the dropdown
    this.loadParentAccounts()
  }
}
</script>

<style scoped>
.account-form {
  max-width: 500px;
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
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.875rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 3px rgba(0,123,255,0.25);
}

.form-group .form-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.form-group input.error,
.form-group textarea.error,
.form-group select.error {
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
</style>