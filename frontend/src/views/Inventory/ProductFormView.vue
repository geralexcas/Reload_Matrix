<template>
  <div class="product-form-view">
    <div class="header">
      <h2>{{ editProductId ? 'Editar Producto' : 'Crear Nuevo Producto' }}</h2>
      <button @click="goBack" class="btn btn-secondary">
        <i class="fas fa-arrow-left"></i> Volver al listado
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando producto...</p>
    </div>

    <div v-if="error && !loading" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-if="!loading" class="form-card">
      <ProductForm 
        :product="productToEdit"
        @save="handleSaveProduct"
        @cancel="goBack"
      />
    </div>
  </div>
</template>

<script>
import ProductForm from '@/components/Inventory/ProductForm.vue'
import { mapActions } from 'vuex'

export default {
  name: 'ProductFormView',
  components: {
    ProductForm
  },
  data() {
    return {
      editProductId: null,
      productToEdit: null,
      loading: false,
      error: null
    }
  },
  created() {
    this.editProductId = this.$route.params.id || null
    if (this.editProductId) {
      this.loadProduct()
    }
  },
  methods: {
    ...mapActions('inventory', [
      'fetchProductById',
      'createProduct',
      'updateProduct'
    ]),
    
    goBack() {
      this.$router.push('/inventory')
    },
    
    loadProduct() {
      this.loading = true
      const companyId = this.$route.params.companyId || 1
      
      this.fetchProductById({ productId: this.editProductId, companyId })
        .then(res => {
          this.productToEdit = res.data
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al cargar el producto'
          this.$toast?.error('No se pudo cargar el producto')
        })
        .finally(() => {
          this.loading = false
        })
    },
    
    handleSaveProduct(productData) {
      const companyId = this.$route.params.companyId || 1
      
      if (this.editProductId) {
        // Update existing
        this.updateProduct({ 
          productId: this.editProductId, 
          productData, 
          companyId 
        })
        .then(() => {
          this.$toast?.success('Producto actualizado exitosamente')
          this.goBack()
        })
        .catch(err => {
          this.$toast?.error(err.response?.data?.detail || 'Error al actualizar producto')
        })
      } else {
        // Create new
        this.createProduct({ 
          productData, 
          companyId 
        })
        .then(() => {
          this.$toast?.success('Producto creado exitosamente')
          this.goBack()
        })
        .catch(err => {
          this.$toast?.error(err.response?.data?.detail || 'Error al crear producto')
        })
      }
    }
  }
}
</script>

<style scoped>
.product-form-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.header h2 {
  color: #2c3e50;
  margin: 0;
}

.form-card {
  background: white;
  border-radius: 10px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  border: 1px solid #ebeef5;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.loading-state,
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

.alert-danger {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 6px;
}
</style>
