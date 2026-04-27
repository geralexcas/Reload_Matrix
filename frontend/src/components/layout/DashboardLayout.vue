<template>
  <div class="dashboard-layout">
    <SidebarNav :is-collapsed="sidebarCollapsed" @toggle="sidebarCollapsed = !sidebarCollapsed" />
    <div class="main-content" :class="{ expanded: sidebarCollapsed }">
      <TopHeader :title="pageTitle" @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />
      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import SidebarNav from '@/components/layout/SidebarNav.vue'
import TopHeader from '@/components/layout/TopHeader.vue'

export default {
  name: 'DashboardLayout',
  components: { SidebarNav, TopHeader },
  data() {
    return {
      sidebarCollapsed: false
    }
  },
  computed: {
    pageTitle() {
      const routeName = this.$route.name || ''
      const titles = {
        'dashboard': 'Dashboard',
        'companies': 'Gestión de Empresa',
        'partners': 'Socios (Proveedores y Clientes)',
        'inventory': 'Inventario',
        'invoicing': 'Facturación',
        'accounting': 'Contabilidad',
        'libro-mayor': 'Libro Mayor',
        'libro-ventas': 'Libro de Ventas',
        'libro-compras': 'Libro de Compras',
        'declaracion-iva': 'Declaración de IVA',
        'reporte-retenciones': 'Reporte de Retenciones',
        'reporte-ingresos': 'Reporte de Ingresos',
        'reporte-patrimonio': 'Reporte de Patrimonio',
        'repair': 'Módulo de Reparación',
        'wallet': 'Monedero Electrónico',
        'treasury': 'Tesorería',
        'treasury-bank-accounts': 'Cuentas Bancarias',
        'treasury-cash-accounts': 'Cuentas de Caja',
        'treasury-transactions': 'Transacciones de Tesorería',
        'treasury-transfers': 'Transferencias',
        'treasury-checks': 'Registro de Cheques',
        'treasury-cash-flow': 'Flujo de Caja',
        'treasury-reconciliations': 'Conciliación Bancaria',
        'admin-users': 'Gestión de Usuarios'
      }
      return titles[routeName] || 'Sistema de Gestión'
    }
  }
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  margin-left: 250px;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
}

.main-content.expanded {
  margin-left: 60px;
}

.page-content {
  flex: 1;
  padding: 1.5rem;
  background-color: #f8f9fa;
}
</style>
