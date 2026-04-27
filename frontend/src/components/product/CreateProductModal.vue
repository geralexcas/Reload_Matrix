<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Nuevo Producto</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <form @submit.prevent="submitProduct" class="modal-body">
        <div class="form-row">
          <div class="form-group">
            <label>SKU *</label>
            <input v-model="form.sku" type="text" required placeholder="Código interno" />
          </div>
          <div class="form-group">
            <label>Código de Barras</label>
            <input v-model="form.barcode" type="text" placeholder="EAN, UPC, etc." />
          </div>
        </div>

        <div class="form-group">
          <label>Nombre del Producto *</label>
          <input v-model="form.name" type="text" required placeholder="Nombre del producto" />
        </div>

        <div class="form-group">
          <label>Descripción</label>
          <textarea v-model="form.description" rows="2" placeholder="Detalles adicionales"></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Categoría</label>
            <div class="category-select">
              <select v-model="form.category">
                <option value="">Seleccionar categoría</option>
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                <option value="__new__">+ Nueva categoría</option>
              </select>
              <input 
                v-if="form.category === '__new__'" 
                v-model="newCategory" 
                type="text" 
                placeholder="Nueva categoría" 
                @keyup.enter="addNewCategory"
              />
              <button v-if="form.category === '__new__'" type="button" class="btn btn-sm btn-primary" @click="addNewCategory">Agregar</button>
            </div>
          </div>
          <div class="form-group">
            <label>Unidad de Medida</label>
            <select v-model="form.unit_of_measure">
              <option value="UNIDAD">Unidad</option>
              <option value="KG">Kilogramo</option>
              <option value="LITRO">Litro</option>
              <option value="METRO">Metro</option>
              <option value="PAQUETE">Paquete</option>
              <option value="DOCENA">Docena</option>
              <option value="LIBRA">Libra</option>
              <option value="GALON">Galón</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Precio de Compra *</label>
            <input v-model.number="form.purchase_price" type="number" step="0.01" min="0" required />
          </div>
          <div class="form-group">
            <label>Precio de Venta *</label>
            <input v-model.number="form.sale_price" type="number" step="0.01" min="0" required />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Stock Inicial</label>
            <input v-model.number="form.stock_level" type="number" step="0.01" min="0" />
          </div>
          <div class="form-group">
            <label>Stock Mínimo</label>
            <input v-model.number="form.min_stock_level" type="number" step="0.01" min="0" />
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Guardando...' : 'Crear Producto' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'

export default {
  name: 'CreateProductModal',
  emits: ['close', 'created'],
  setup(props, { emit }) {
    const store = useStore()
    const companyId = ref(store.getters['company/selectedCompanyId'])
    const loading = ref(false)
    const categories = ref([])
    const newCategory = ref('')
    const showNewCategory = ref(false)

    const form = ref({
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
      is_active: true
    })

    const fetchCategories = async () => {
      try {
        const res = await api.get('/api/v1/inventory/', {
          params: { company_id: companyId.value, skip: 0, limit: 1000 }
        })
        const products = res.data || res
        const uniqueCategories = [...new Set(products.map(p => p.category).filter(Boolean))]
        categories.value = uniqueCategories.sort()
      } catch (err) {
        console.error('Error fetching categories:', err)
      }
    }

    const addNewCategory = () => {
      if (newCategory.value.trim()) {
        form.value.category = newCategory.value.trim()
        showNewCategory.value = false
        newCategory.value = ''
      }
    }

    onMounted(() => {
      fetchCategories()
    })

    const submitProduct = async () => {
      if (!form.value.sku || !form.value.name) {
        alert('Por favor complete los campos requeridos')
        return
      }

      const productData = { ...form.value }
      if (productData.category === '__new__') {
        productData.category = newCategory.value.trim() || ''
      }

      loading.value = true
      try {
        const res = await api.post('/api/v1/inventory/', productData, {
          params: { company_id: companyId.value }
        })
        emit('created', res.data)
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al crear el producto')
      } finally {
        loading.value = false
      }
    }

    return {
      loading,
      form,
      categories,
      newCategory,
      showNewCategory,
      addNewCategory,
      submitProduct
    }
  }
}
</script>

<style scoped>
.category-select {
  display: flex;
  gap: 8px;
  align-items: center;
}
.category-select select {
  flex: 1;
}
.category-select input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ecf0f1;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
}

.modal-body {
  padding: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.form-group label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ecf0f1;
  margin-top: 16px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}
</style>