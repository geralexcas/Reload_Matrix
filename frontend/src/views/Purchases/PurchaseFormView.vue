<template>
  <div class="purchase-form-container">
    <div class="page-header">
      <h1 class="page-title">{{ isEdit ? 'Editar Compra' : 'Nueva Compra' }}</h1>
      <button class="btn btn-secondary" @click="goBack">
        <span class="btn-icon">←</span>
        Volver
      </button>
    </div>

    <div class="form-card">
      <form @submit.prevent="submitPurchase">
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
              <option v-if="isEdit" value="PAID">Pagada</option>
              <option v-if="isEdit" value="PARTIAL">Parcial</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Notas</label>
          <textarea v-model="form.notes" rows="2" placeholder="Notas u observaciones..."></textarea>
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
                  <input v-model.number="item.quantity" type="number" min="1" step="0.01" @input="calculateItemTotal(index)" />
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

        <div class="totals-grid">
          <div class="totals-placeholder"></div>
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
              <label>Descuento Global:</label>
              <input v-model.number="form.discount_amount" type="number" step="0.01" min="0" class="discount-input" @input="calculateTotals" />
            </div>
            <div class="total-row total-final">
              <span>Total:</span>
              <span>${{ formatNumber(totalAmount) }}</span>
            </div>
          </div>
        </div>

        <div class="form-footer">
          <button type="button" class="btn btn-secondary" @click="goBack">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Guardando...' : (isEdit ? 'Actualizar Compra' : 'Crear Compra') }}
          </button>
        </div>
      </form>
    </div>

    <CreateProductModal
      v-if="showProductModal"
      @close="showProductModal = false"
      @created="onProductCreated"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import CreateProductModal from '@/components/product/CreateProductModal.vue'

export default {
  name: 'PurchaseFormView',
  components: {
    CreateProductModal
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    const companyId = computed(() => store.getters['company/selectedCompanyId'])

    const isEdit = computed(() => !!route.params.id)
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

    const loadPurchaseData = async () => {
      if (!isEdit.value) return
      loading.value = true
      try {
        const res = await store.dispatch('purchases/fetchPurchaseById', {
          purchaseId: route.params.id,
          companyId: companyId.value
        })
        const purchase = res.data
        form.value = {
          purchase_number: purchase.purchase_number,
          partner_id: purchase.partner_id,
          purchase_date: purchase.purchase_date,
          due_date: purchase.due_date,
          payment_method: purchase.payment_method,
          status: purchase.status,
          notes: purchase.notes || '',
          discount_amount: purchase.discount_amount || 0,
          items: purchase.items.map(item => ({
            product_id: item.product_id,
            description: item.description,
            quantity: item.quantity,
            unit_price: item.unit_price,
            discount_percent: item.discount_percent || 0,
            tax_rate: item.tax_rate || 0,
            line_total: item.line_total
          }))
        }
      } catch (err) {
        console.error('Error loading purchase:', err)
        alert('Error al cargar los datos de la compra')
        router.push('/purchases')
      } finally {
        loading.value = false
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

    const goBack = () => {
      router.push('/purchases')
    }

    const submitPurchase = async () => {
      if (!form.value.purchase_number || !form.value.partner_id || form.value.items.length === 0) {
        alert('Por favor complete los campos requeridos y adicione al menos un item')
        return
      }

      loading.value = true
      try {
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

        if (isEdit.value) {
          await store.dispatch('purchases/updatePurchase', {
            purchaseId: route.params.id,
            purchaseData: purchaseData,
            companyId: companyId.value
          })
          alert('Compra actualizada exitosamente')
        } else {
          await store.dispatch('purchases/createPurchase', {
            purchaseData: purchaseData,
            companyId: companyId.value
          })
          alert('Compra creada exitosamente')
        }
        router.push('/purchases')
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al procesar la compra')
      } finally {
        loading.value = false
      }
    }

    onMounted(async () => {
      if (!companyId.value) return
      await Promise.all([
        fetchSuppliers(),
        fetchProducts()
      ])
      if (isEdit.value) {
        await loadPurchaseData()
      } else {
        addItem()
      }
    })

    return {
      isEdit,
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
      submitPurchase,
      goBack
    }
  }
}
</script>

<style scoped>
.purchase-form-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.form-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-group label {
  font-size: 13px;
  color: #555;
  font-weight: 600;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #3498db;
  outline: none;
}

.items-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.items-section h3 {
  font-size: 18px;
  color: #2c3e50;
  margin-bottom: 15px;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.items-table th,
.items-table td {
  padding: 10px;
  border: 1px solid #eee;
  text-align: left;
}

.items-table th {
  background: #f8f9fa;
  font-size: 12px;
  color: #7f8c8d;
  text-transform: uppercase;
}

.items-table input,
.items-table select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.text-right {
  text-align: right;
}

.btn-remove {
  background: #ff7675;
  color: white;
  border: none;
  border-radius: 4px;
  width: 28px;
  height: 28px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.btn-remove:hover {
  background: #d63031;
}

.btn-add-item {
  background: #00cec9;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-add-item:hover {
  background: #00b894;
}

.totals-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  margin-top: 30px;
}

.totals-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  color: #2c3e50;
  font-size: 15px;
}

.discount-input {
  width: 120px;
  padding: 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: right;
}

.total-final {
  font-size: 20px;
  font-weight: 700;
  color: #2d3436;
  border-top: 2px solid #dfe6e9;
  padding-top: 15px;
  margin-top: 10px;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-primary:disabled {
  background: #b2bec3;
  cursor: not-allowed;
}

.btn-secondary {
  background: #636e72;
  color: white;
}

.btn-secondary:hover {
  background: #2d3436;
}

.product-select-wrapper {
  display: flex;
  gap: 6px;
}

.product-select-wrapper select {
  flex: 1;
}

.btn-create-product {
  background: #55efc4;
  color: #2d3436;
  border: none;
  border-radius: 4px;
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-size: 20px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-create-product:hover {
  background: #00b894;
  color: white;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  .totals-grid {
    grid-template-columns: 1fr;
  }
  .totals-placeholder {
    display: none;
  }
}
</style>
