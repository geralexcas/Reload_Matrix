<template>
  <div class="modal-overlay">
    <div class="modal-content modal-lg">
      <div class="modal-header">
        <h2>Nueva Compra</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <form @submit.prevent="submitPurchase" class="modal-body">
        <div class="form-row">
          <div class="form-group">
            <label>Número de Factura *</label>
            <input v-model="form.purchase_number" type="text" required />
          </div>
          <div class="form-group">
            <label>Proveedor *</label>
            <select v-model="form.partner_id" required>
              <option value="">Seleccionar proveedor</option>
              <option v-for="partner in suppliers" :key="partner.id" :value="partner.id">
                {{ partner.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Fecha de Compra *</label>
            <input v-model="form.purchase_date" type="date" required />
          </div>
          <div class="form-group">
            <label>Fecha de Vencimiento</label>
            <input v-model="form.due_date" type="date" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Método de Pago *</label>
            <select v-model="form.payment_method" required>
              <option value="CASH">Efectivo</option>
              <option value="BANK_TRANSFER">Transferencia Bancaria</option>
              <option value="CHECK">Cheque</option>
              <option value="CREDIT_CARD">Tarjeta de Crédito</option>
              <option value="CREDIT">Crédito</option>
              <option value="PARTIAL_CREDIT">Crédito Parcial</option>
            </select>
          </div>
          <div class="form-group">
            <label>Estado *</label>
            <select v-model="form.status" required>
              <option value="ISSUED">Emitida</option>
              <option value="DRAFT">Borrador</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Notas</label>
          <textarea v-model="form.notes" rows="2"></textarea>
        </div>

        <div class="items-section">
          <h3>Items de la Compra</h3>
          
          <table class="items-table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Precio Unit.</th>
                <th>Desc %</th>
                <th>IVA %</th>
                <th>Total</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in form.items" :key="index">
                <td>
                  <div class="product-select-wrapper">
                    <select v-model="item.product_id" @change="onProductChange(index)">
                      <option value="">Seleccionar</option>
                      <option v-for="prod in products" :key="prod.id" :value="prod.id">
                        {{ prod.name }}
                      </option>
                    </select>
                    <button type="button" class="btn-create-product" @click="openCreateProductModal(index)" title="Crear producto">+</button>
                  </div>
                </td>
                <td>
                  <input v-model.number="item.quantity" type="number" min="1" @input="calculateItemTotal(index)" />
                </td>
                <td>
                  <input v-model.number="item.unit_price" type="number" step="0.01" min="0" @input="calculateItemTotal(index)" />
                </td>
                <td>
                  <input v-model.number="item.discount_percent" type="number" step="0.01" min="0" max="100" @input="calculateItemTotal(index)" />
                </td>
                <td>
                  <input v-model.number="item.tax_rate" type="number" step="0.01" min="0" max="100" @input="calculateItemTotal(index)" />
                </td>
                <td class="text-right">${{ formatNumber(item.line_total || 0) }}</td>
                <td>
                  <button type="button" class="btn-remove" @click="removeItem(index)">×</button>
                </td>
              </tr>
            </tbody>
          </table>

          <button type="button" class="btn-add-item" @click="addItem">+ Agregar Item</button>
        </div>

        <div class="totals-section">
          <div class="total-row">
            <span>Subtotal:</span>
            <span>${{ formatNumber(subtotal) }}</span>
          </div>
          <div class="total-row">
            <span>IVA:</span>
            <span>${{ formatNumber(taxAmount) }}</span>
          </div>
          <div class="total-row">
            <span>Descuento:</span>
            <span>-${{ formatNumber(form.discount_amount || 0) }}</span>
          </div>
          <div class="total-row total-final">
            <span>Total:</span>
            <span>${{ formatNumber(totalAmount) }}</span>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Guardando...' : 'Crear Compra' }}
          </button>
        </div>
      </form>

      <CreateProductModal
        v-if="showProductModal"
        @close="showProductModal = false"
        @created="onProductCreated"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import CreateProductModal from '@/components/product/CreateProductModal.vue'

export default {
  name: 'CreatePurchaseModal',
  components: {
    CreateProductModal
  },
  emits: ['close', 'created'],
  setup(props, { emit }) {
    const store = useStore()
    const companyId = computed(() => store.getters['company/selectedCompanyId'])

    const loading = ref(false)
    const suppliers = ref([])
    const products = ref([])

    const showProductModal = ref(false)
    const currentItemIndex = ref(0)

    const form = ref({
      purchase_number: '',
      partner_id: '',
      purchase_date: new Date().toISOString().split('T')[0],
      due_date: '',
      payment_method: 'CREDIT',
      status: 'ISSUED',
      notes: '',
      discount_amount: 0,
      items: []
    })

    const fetchSuppliers = async () => {
      try {
        const res = await store.dispatch('partners/fetchPartners', {
          companyId: companyId.value,
          partnerType: 'SUPPLIER'
        })
        suppliers.value = res.data
      } catch (err) {
        console.error('Error fetching suppliers:', err)
      }
    }

    const fetchProducts = async () => {
      try {
        const res = await store.dispatch('inventory/fetchProducts', {
          companyId: companyId.value
        })
        products.value = res.data
      } catch (err) {
        console.error('Error fetching products:', err)
      }
    }

    const openCreateProductModal = (index) => {
      currentItemIndex.value = index
      showProductModal.value = true
    }

    const onProductCreated = async (product) => {
      showProductModal.value = false
      await fetchProducts()
      form.value.items[currentItemIndex.value].product_id = product.id
      form.value.items[currentItemIndex.value].description = product.name
      form.value.items[currentItemIndex.value].unit_price = product.purchase_price || 0
      form.value.items[currentItemIndex.value].tax_rate = product.tax_rate || 19
      calculateItemTotal(currentItemIndex.value)
    }

    const addItem = () => {
      form.value.items.push({
        product_id: '',
        description: '',
        quantity: 1,
        unit_price: 0,
        discount_percent: 0,
        tax_rate: 19,
        line_total: 0
      })
    }

    const removeItem = (index) => {
      form.value.items.splice(index, 1)
    }

    const onProductChange = (index) => {
      const product = products.value.find(p => p.id === form.value.items[index].product_id)
      if (product) {
        form.value.items[index].description = product.name
        form.value.items[index].unit_price = product.purchase_price || 0
        form.value.items[index].tax_rate = product.tax_rate || 19
        calculateItemTotal(index)
      }
    }

    const calculateItemTotal = (index) => {
      const item = form.value.items[index]
      const subtotal = item.quantity * item.unit_price
      const discount = subtotal * (item.discount_percent / 100)
      const afterDiscount = subtotal - discount
      const tax = afterDiscount * (item.tax_rate / 100)
      item.line_total = afterDiscount + tax
    }

    const subtotal = computed(() => {
      return form.value.items.reduce((sum, item) => {
        const itemSubtotal = item.quantity * item.unit_price
        const discount = itemSubtotal * (item.discount_percent / 100)
        return sum + (itemSubtotal - discount)
      }, 0)
    })

    const taxAmount = computed(() => {
      return form.value.items.reduce((sum, item) => {
        const subtotal = item.quantity * item.unit_price
        const discount = subtotal * (item.discount_percent / 100)
        const afterDiscount = subtotal - discount
        return sum + (afterDiscount * (item.tax_rate / 100))
      }, 0)
    })

    const totalAmount = computed(() => {
      return subtotal.value + taxAmount.value - (form.value.discount_amount || 0)
    })

    const formatNumber = (value) => {
      return new Intl.NumberFormat('es-CO').format(value || 0)
    }

    const submitPurchase = async () => {
      if (!form.value.purchase_number || !form.value.partner_id || form.value.items.length === 0) {
        alert('Por favor complete los campos requeridos y adicione al menos un item')
        return
      }

      loading.value = true
      try {
        // Convertir strings vacíos a null para campos de fecha
        const purchaseData = {
          ...form.value,
          purchase_date: form.value.purchase_date || null,
          due_date: form.value.due_date || null,
          notes: form.value.notes || null,
          items: form.value.items.map(item => ({
            ...item,
            description: item.description || `Producto ${item.product_id}`
          }))
        }

        await store.dispatch('purchases/createPurchase', {
          purchaseData: purchaseData,
          companyId: companyId.value
        })
        emit('created')
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al crear la compra')
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchSuppliers()
      fetchProducts()
      addItem()
    })

    return {
      loading,
      suppliers,
      products,
      form,
      subtotal,
      taxAmount,
      totalAmount,
      showProductModal,
      currentItemIndex,
      openCreateProductModal,
      onProductCreated,
      addItem,
      removeItem,
      onProductChange,
      calculateItemTotal,
      formatNumber,
      submitPurchase
    }
  }
}
</script>

<style scoped>
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
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
}

.modal-lg {
  max-width: 900px;
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
  font-size: 20px;
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
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
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

.items-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.items-section h3 {
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 12px;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12px;
}

.items-table th,
.items-table td {
  padding: 8px;
  border: 1px solid #ecf0f1;
}

.items-table th {
  background: #f8f9fa;
  font-size: 11px;
  text-transform: uppercase;
}

.items-table input,
.items-table select {
  width: 100%;
  padding: 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.text-right {
  text-align: right;
}

.btn-remove {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  cursor: pointer;
}

.btn-add-item {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.totals-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.total-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  color: #2c3e50;
}

.total-final {
  font-size: 18px;
  font-weight: 600;
  border-top: 2px solid #ecf0f1;
  padding-top: 12px;
  margin-top: 8px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
  margin-top: 20px;
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

.product-select-wrapper {
  display: flex;
  gap: 4px;
}

.product-select-wrapper select {
  flex: 1;
}

.btn-create-product {
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  width: 28px;
  height: 28px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-create-product:hover {
  background: #219a52;
}
</style>