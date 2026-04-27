<template>
  <div class="inventory-container">
    <div class="inventory-header">
      <h2>Gestión de Inventario</h2>
      <div class="header-actions">
        <button @click="$router.push('/inventory/new')" class="btn btn-primary">
          <i class="fas fa-plus"></i> Nuevo Producto
        </button>
        <button @click="scanBarcode" class="btn btn-secondary">
          <i class="fas fa-barcode"></i> Escanear Código
        </button>
        <button @click="loadLowStock" class="btn btn-warning">
          <i class="fas fa-exclamation-triangle"></i> Bajo Stock
        </button>
      </div>
    </div>
    
    <!-- Barcode Scanner Modal -->
    <div v-if="scanning" class="modal-backdrop" @click="scanning = false">
      <div class="modal-content">
        <h3>Escaneando Código de Barras</h3>
        <p>Apunte la cámara al código de barras del producto</p>
        <div id="barcode-scanner" style="width: 300px; height: 200px; border: 2px dashed #ccc; margin: 20px auto;"></div>
        <p class="scanner-status">{{ scannerStatus }}</p>
        <button @click="stopScanning" class="btn btn-danger">Cancelar</button>
      </div>
    </div>
    
    <!-- Removed Product Modal as it's now a full page view -->
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando productos...</p>
    </div>
    
    <!-- Error State -->
    <div v-if="error && !loading" class="alert alert-danger">
      {{ error }}
    </div>
    
    <!-- Empty State -->
    <div v-if="!loading && products.length === 0 && !error" class="empty-state">
      <i class="fas fa-boxes"></i>
      <p>No hay productos registrados</p>
      <button @click="$router.push('/inventory/new')" class="btn btn-primary mt-3">
        Agregar Primer Producto
      </button>
    </div>
    
    <!-- Products List -->
    <div v-if="!loading && products.length > 0" class="products-list">
      <!-- Filters and Search -->
      <div class="filters-bar">
        <input 
          type="text" 
          v-model="searchTerm"
          placeholder="Buscar productos..."
          @input="debouncedSearch"
          class="search-input"
        >
        <select v-model="filterCategory" @change="applyFilters">
          <option value="">Todas las Categorías</option>
          <option v-for="category in uniqueCategories" :key="category">
            {{ category }}
          </option>
        </select>
      </div>
      
      <!-- Products Table -->
      <table class="products-table">
        <thead>
          <tr>
            <th>Código</th>
            <th>Nombre</th>
            <th>Categoría</th>
            <th>Precio Compra</th>
            <th>Precio Venta</th>
            <th>Stock</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in filteredProducts" :key="product.id" :class="{'low-stock': product.stock_level <= product.min_stock_level}">
            <td>
              <div class="product-code">
                <span>{{ product.sku }}</span>
                <template v-if="product.barcode">
                  <span class="barcode-badge">📧 {{ product.barcode }}</span>
                </template>
              </div>
            </td>
            <td class="product-name">
              <strong>{{ product.name }}</strong>
              <p class="product-description">{{ product.description || '' }}</p>
            </td>
            <td>{{ product.category || '-' }}</td>
            <td>${{ Number(product.purchase_price).toFixed(2) }}</td>
            <td>${{ Number(product.sale_price).toFixed(2) }}</td>
            <td class="stock-level">
              <span>{{ Number(product.stock_level).toFixed(2) }} {{ product.unit_of_measure }}</span>
              <template v-if="product.stock_level <= product.min_stock_level">
                <span class="stock-alert">¡Bajo!</span>
              </template>
            </td>
            <td>
              <span v-if="product.is_active" class="status-active">Activo</span>
              <span v-else class="status-inactive">Inactivo</span>
            </td>
            <td class="actions-cell">
              <button 
                @click="editProduct(product.id)"
                class="btn btn-icon btn-info"
                title="Editar"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button 
                @click="deleteProduct(product.id)"
                class="btn btn-icon btn-danger"
                title="Eliminar"
              >
                <i class="fas fa-trash"></i>
              </button>
              <button 
                @click="adjustStock(product.id)"
                class="btn btn-icon btn-warning"
                title="Ajustar Stock"
              >
                <i class="fas fa-sync-alt"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Pagination -->
      <div v-if="products.length > 0" class="pagination">
        <button 
          :disabled="currentPage <= 1"
          @click="previousPage"
          class="btn btn-sm"
        >
          Anterior
        </button>
        <span>Página {{ currentPage }} de {{ totalPages }}</span>
        <button 
          :disabled="currentPage >= totalPage || totalPages === 0"
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
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'ProductListView',
  data() {
    return {
      products: [],
      product: null,
      loading: false,
      error: null,
      searchTerm: '',
      filterCategory: '',
      currentPage: 1,
      itemsPerPage: 20,
      scanning: false,
      scannerStatus: 'Listo para escanear...',
      uniqueCategories: []
    }
  },
  computed: {
    ...mapGetters('inventory', ['getProducts', 'getProduct']),
    filteredProducts() {
      let filtered = [...this.products]
      
      // Apply search filter
      if (this.searchTerm) {
        const term = this.searchTerm.toLowerCase().trim()
        filtered = filtered.filter(product => 
          product.name.toLowerCase().includes(term) ||
          product.sku.toLowerCase().includes(term) ||
          (product.barcode && product.barcode.includes(term)) ||
          (product.description && product.description.toLowerCase().includes(term)) ||
          (product.category && product.category.toLowerCase().includes(term))
        )
      }
      
      // Apply category filter
      if (this.filterCategory) {
        filtered = filtered.filter(product => product.category === this.filterCategory)
      }
      
      return filtered
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filteredProducts.length / this.itemsPerPage))
    },
    paginatedProducts() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      return this.filteredProducts.slice(start, start + this.itemsPerPage)
    }
  },
  watch: {
    '$route.params.companyId': {
      handler() {
        this.loadProducts()
      },
      immediate: true
    }
  },
  methods: {
    ...mapActions('inventory', [
      'fetchProducts',
      'fetchProductById',
      'createProduct',
      'updateProduct',
      'deleteProduct as deleteProductAction',
      'adjustStock',
      'fetchProductByBarcode',
      'getLowStockProducts'
    ]),
    
    loadProducts() {
      // Get company ID from auth store or route
      const companyId = this.$route.params.companyId || 1 // Default for now
      this.fetchProducts({ companyId, skip: 0, limit: 1000 })
        .then(res => {
          this.products = res.data || []
          this.extractCategories()
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al cargar productos'
        })
    },
    
    extractCategories() {
      const categories = [...new Set(this.products.map(p => p.category).filter(Boolean))]
      this.uniqueCategories = categories.sort()
    },
    
    debouncedSearch: function() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.applyFilters()
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
    
    showAddProductForm() {
      this.$router.push('/inventory/new')
    },
    
    editProduct(productId) {
      this.$router.push(`/inventory/edit/${productId}`)
    },
    
    closeProductForm() {
      // Not needed anymore
    },
    
    // handleSaveProduct is now in ProductFormView
    
    deleteProduct(productId) {
      if (!window.confirm('¿Está seguro de que desea eliminar este producto? Esta acción no se puede deshacer.')) {
        return
      }
      
      this.deleteProductAction({ productId, companyId: this.$route.params.companyId || 1 })
        .then(() => {
          this.$toast.success('Producto eliminado exitosamente')
          this.loadProducts()
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al eliminar producto'
        })
    },
    
    adjustStock(productId) {
      // This would open a stock adjustment modal
      this.$toast.info('Funcionalidad de ajuste de stock en desarrollo')
    },
    
    scanBarcode() {
      this.scanning = true
      this.scannerStatus = 'Iniciando escáner...'
      this.initBarcodeScanner()
    },
    
    stopScanning() {
      this.scanning = false
      if (this.scannerInstance) {
        this.scannerInstance.stop()
        this.scannerInstance = null
      }
      this.scannerStatus = 'Escaneo detenido'
    },
    
    initBarcodeScanner() {
      // This would integrate with a barcode scanning library like QuaggaJS
      // For now, we'll simulate it
      this.scannerStatus = 'Escáner iniciado. Apunte al código de barras.'
      
      // Simulate scanning after 2 seconds for demo
      setTimeout(() => {
        const fakeBarcode = '7798123456789' // Example EAN
        this.handleScannedBarcode(fakeBarcode)
      }, 2000)
    },
    
    handleScannedBarcode(barcode) {
      this.stopScanning()
      this.fetchProductByBarcode({ barcode, companyId: this.$route.params.companyId || 1 })
        .then(res => {
          if (res.data) {
            // Product found, navigate to edit
            this.editProductId = res.data.id
            this.showEditProduct = true
            this.productToEdit = res.data
            this.$toast.success(`Producto encontrado: ${res.data.name}`)
          } else {
            // Product not found, offer to create new
            if (window.confirm(`Producto con código ${barcode} no encontrado. ¿Desea crearlo ahora?`)) {
              this.$router.push('/inventory/new')
            }
          }
        })
        .catch(err => {
          if (err.response && err.response.status === 404) {
            // Product not found
            if (window.confirm(`Producto con código ${barcode} no encontrado. ¿Desea crearlo ahora?`)) {
              this.$router.push('/inventory/new')
            }
          } else {
            this.$toast.error('Error al buscar producto por código de barras')
          }
        })
    },
    
    loadLowStock() {
      this.getLowStockProducts({ companyId: this.$route.params.companyId || 1 })
        .then(res => {
          this.products = res.data || []
          this.extractCategories()
          if (this.products.length === 0) {
            this.$toast.info('No hay productos con bajo stock')
          }
        })
        .catch(err => {
          this.error = err.response?.data?.detail || 'Error al cargar productos de bajo stock'
        })
    }
  },
  created() {
    this.searchTimeout = null
    this.loadProducts()
  },
  beforeUnmount() {
    clearTimeout(this.searchTimeout)
    if (this.scannerInstance) {
      this.scannerInstance.stop()
    }
  }
}
</script>

<style scoped>
.inventory-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.inventory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.inventory-header h2 {
  color: #2c3e50;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
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

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
}

.btn-warning:hover {
  background-color: #e0a800;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
}

.btn-info:hover {
  background-color: #138496;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 10px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
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

.products-list {
  margin-top: 20px;
}

.filters-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  flex-wrap: wrap;
  align-items: end;
}

.search-input {
  flex: 1;
  min-width: 250px;
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0,123,255,0.25);
}

.filters-bar select {
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  background-color: white;
  min-width: 200px;
}

.filters-bar select:focus {
  outline: none;
  border-color: #007bff;
}

.products-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.products-table th,
.products-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.products-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.products-table tbody tr:hover {
  background-color: #f8f9ff;
}

.products-table tbody tr:last-child td {
  border-bottom: none;
}

.product-name {
  font-size: 0.95rem;
}

.product-description {
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 4px;
}

.stock-level {
  font-weight: 600;
}

.stock-alert {
  background-color: #fff3cd;
  color: #856404;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.75rem;
  margin-left: 8px;
}

.status-active {
  background-color: #d4edda;
  color: #155724;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.status-inactive {
  background-color: #f8d7da;
  color: #721c24;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
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

.btn-icon.btn-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.btn-icon.btn-danger:hover {
  background-color: #f1c0c8;
}

.btn-icon.btn-warning {
  background-color: #ffeaa7;
  color: #635d35;
}

.btn-icon.btn-warning:hover {
  background-color: #ffdf8e;
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

.barcode-badge {
  background-color: #e9ecef;
  color: #495057;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.75rem;
  margin-left: 8px;
}

/* Responsive design */
@media (max-width: 768px) {
  .inventory-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input,
  .filters-bar select {
    width: 100%;
  }
  
  .products-table th,
  .products-table td {
    padding: 12px 8px;
    font-size: 0.85rem;
  }
  
  .actions-cell {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .inventory-container {
    padding: 10px;
  }
  
  .inventory-header h2 {
    font-size: 1.5rem;
  }
  
  .products-table thead {
    display: none;
  }
  
  .products-table,
  .products-table tbody,
  .products-table tr,
  .products-table td {
    display: block;
    width: 100%;
  }
  
  .products-table tr {
    margin-bottom: 15px;
    border: 1px solid #ddd;
    border-radius: 6px;
  }
  
  .products-table td {
    text-align: right;
    padding-left: 50%;
    position: relative;
    border-bottom: none;
  }
  
  .products-table td::before {
    content: attr(data-label);
    position: absolute;
    left: 0;
    width: 50%;
    padding-left: 12px;
    font-weight: 600;
    color: #6c757d;
  }
  
  .products-table td:last-child {
    border-bottom: 0;
  }
  
  .actions-cell {
    justify-content: flex-start;
  }
}
</style>