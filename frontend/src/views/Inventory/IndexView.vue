<template>
  <div>
    <ProductListView 
      :company-id="$route.params.companyId || 1"
    />
  </div>
</template>

<script>
import ProductListView from '@/views/Inventory/ProductListView.vue'

export default {
  name: 'InventoryIndexView',
  components: {
    ProductListView
  }
}
</script>