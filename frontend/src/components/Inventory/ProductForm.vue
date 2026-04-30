<template>
  <form @submit.prevent="onSubmit" class="product-form">
    <div class="form-group">
      <label for="sku">SKU (Código interno):*</label>
      <input 
        type="text" 
        id="sku" 
        v-model="form.sku" 
        required
        maxlength="50"
        placeholder="Ej: PROD-001"
      />
      <small class="form-text">Código único para identificar el producto internamente</small>
    </div>
    
    <div class="form-group">
      <label for="barcode">Código de Barras:</label>
      <input 
        type="text" 
        id="barcode" 
        v-model="form.barcode" 
        maxlength="100"
        placeholder="Ej: 7798123456789"
        @input="cleanBarcode"
      />
      <small class="form-text">Solo números. Dejar vacío si no aplica.</small>
    </div>
    
    <div class="form-group">
      <label for="name">Nombre del Producto:*</label>
      <input 
        type="text" 
        id="name" 
        v-model="form.name" 
        required
        maxlength="255"
        placeholder="Nombre descriptivo del producto"
      />
    </div>
    
    <div class="form-group">
      <label for="description">Descripción:</label>
      <textarea 
        id="description" 
        v-model="form.description" 
        maxlength="500"
        rows="3"
        placeholder="Detalles adicionales del producto"
      ></textarea>
    </div>
    
    <div class="form-group">
      <label for="category">Categoría:</label>
      <input 
        type="text" 
        id="category" 
        v-model="form.category" 
        maxlength="100"
        placeholder="Ej: Electrónica, Ropas, Alimentos"
      />
    </div>
    
    <div class="form-group">
      <label for="supplier_id">Proveedor:</label>
      <select 
        id="supplier_id" 
        v-model="form.supplier_id"
      >
        <option :value="null">Sin proveedor</option>
        <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
          {{ supplier.name }} - {{ supplier.document_id }}
        </option>
      </select>
    </div>
    
    <div class="form-group">
      <label for="unit_of_measure">Unidad de Medida:</label>
      <select 
        id="unit_of_measure" 
        v-model="form.unit_of_measure"
      >
        <option value="UNIDAD">Unidad</option>
        <option value="KG">Kilogramo</option>
        <option value="LITRO">Litro</option>
        <option value="METRO">Metro</option>
        <option value="PAQUETE">Paquete</option>
        <option value="DOCENA">Docena</option>
        <option value="LIBRA">Libra</option>
        <option value="GALON">Galon</option>
        <option value="ML">Mililitro</option>
        <option value="CM">Centimetro</option>
        <option value="MM">Milimetro</option>
      </select>
    </div>
    
    <div class="form-group">
      <label for="purchase_price">Precio de Compra:*</label>
      <input 
        type="number" 
        id="purchase_price" 
        v-model.number="form.purchase_price" 
        required
        min="0"
        step="0.01"
        placeholder="0.00"
      />
      <small class="form-text">Costo de adquisición del producto</small>
    </div>
    
    <div class="form-group">
      <label for="sale_price">Precio de Venta:*</label>
      <input 
        type="number" 
        id="sale_price" 
        v-model.number="form.sale_price" 
        required
        min="0"
        step="0.01"
        placeholder="0.00"
      />
      <small class="form-text">Precio al que se vende el producto</small>
    </div>
    
    <div class="form-group">
      <label for="stock_level">Nivel de Stock Actual:*</label>
      <input 
        type="number" 
        id="stock_level" 
        v-model.number="form.stock_level" 
        required
        min="0"
        step="0.01"
        placeholder="0.00"
      />
    </div>
    
    <div class="form-group">
      <label for="payment_method">Forma de Pago:*</label>
      <select 
        id="payment_method" 
        v-model="form.payment_method"
        required
      >
        <option v-for="method in paymentMethods" :key="method.value" :value="method.value">
          {{ method.label }}
        </option>
      </select>
    </div>
    
    <div class="form-group">
      <label for="min_stock_level">Nivel Mínimo de Stock:*</label>
      <input 
        type="number" 
        id="min_stock_level" 
        v-model.number="form.min_stock_level" 
        required
        min="0"
        step="0.01"
        placeholder="0.00"
      />
      <small class="form-text">Cuando el stock llega a este nivel, se activa la alerta</small>
    </div>
    
    <div class="form-group">
      <label for="max_stock_level">Nivel Máximo de Stock:*</label>
      <input 
        type="number" 
        id="max_stock_level" 
        v-model.number="form.max_stock_level" 
        required
        min="0"
        step="0.01"
        placeholder="999999.99"
      />
      <small class="form-text">Límite máximo de stock permitido</small>
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
        <label for="is_active">Producto activo</label>
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
import api from '@/services/api'

export default {
  name: 'ProductForm',
  props: {
    product: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      form: {
        sku: '',
        barcode: '',
        name: '',
        description: '',
        category: '',
        unit_of_measure: 'UNIDAD',
        purchase_price: 0,
        sale_price: 0,
        stock_level: 0,
        min_stock_level: 0,
        max_stock_level: 999999.99,
        supplier_id: null,
        payment_method: 'CASH',
        is_active: true
      },
      paymentMethods: [
        { value: 'CASH', label: 'Efectivo' },
        { value: 'BANK_TRANSFER', label: 'Transferencia' },
        { value: 'CREDIT', label: 'Crédito (Pendiente)' }
      ],
      suppliers: [],
      editMode: false,
      isLoading: false,
      errors: {}
    }
  },
  watch: {
    product: {
      handler(newVal) {
        if (newVal) {
          this.editMode = true
          this.form = { ...newVal }
          // Ensure numeric fields are numbers
          this.form.purchase_price = parseFloat(this.form.purchase_price) || 0
          this.form.sale_price = parseFloat(this.form.sale_price) || 0
          this.form.stock_level = parseFloat(this.form.stock_level) || 0
          this.form.min_stock_level = parseFloat(this.form.min_stock_level) || 0
          this.form.max_stock_level = parseFloat(this.form.max_stock_level) || 999999.99
          if (this.form.supplier_id === undefined) this.form.supplier_id = null
          if (this.form.payment_method === undefined) this.form.payment_method = 'CASH'
        }
      },
      immediate: true
    }
  },
  mounted() {
    this.fetchSuppliers()
  },
  methods: {
    async fetchSuppliers() {
      try {
        const response = await api.get('/api/v1/partners/', {
          params: { partner_type: 'SUPPLIER', limit: 1000 }
        })
        const responseBoth = await api.get('/api/v1/partners/', {
          params: { partner_type: 'BOTH', limit: 1000 }
        })
        // Merge them inside the local state
        this.suppliers = [...(response.data || []), ...(responseBoth.data || [])]
      } catch (err) {
        console.error('Error cargando proveedores', err)
      }
    },
    cleanBarcode() {
      // Remove any non-digit characters
      if (this.form.barcode) {
        this.form.barcode = this.form.barcode.replace(/\D/g, '')
      }
    },
    
    validateForm() {
      this.errors = {}
      let isValid = true
      
      if (!this.form.sku || this.form.sku.trim() === '') {
        this.errors.sku = 'El SKU es requerido'
        isValid = false
      }
      
      if (!this.form.name || this.form.name.trim() === '') {
        this.errors.name = 'El nombre es requerido'
        isValid = false
      }
      
      if (this.form.purchase_price < 0) {
        this.errors.purchase_price = 'El precio de compra no puede ser negativo'
        isValid = false
      }
      
      if (this.form.sale_price < 0) {
        this.errors.sale_price = 'El precio de venta no puede ser negativo'
        isValid = false
      }
      
      if (this.form.stock_level < 0) {
        this.errors.stock_level = 'El stock no puede ser negativo'
        isValid = false
      }
      
      if (this.form.min_stock_level < 0) {
        this.errors.min_stock_level = 'El nivel mínimo de stock no puede ser negativo'
        isValid = false
      }
      
      if (this.form.max_stock_level < 0) {
        this.errors.max_stock_level = 'El nivel máximo de stock no puede ser negativo'
        isValid = false
      }
      
      if (parseFloat(this.form.min_stock_level) > parseFloat(this.form.max_stock_level)) {
        this.errors.min_stock_level = 'El nivel mínimo no puede ser mayor que el máximo'
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
  }
}
</script>

<style scoped>
.product-form {
  max-width: 600px;
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