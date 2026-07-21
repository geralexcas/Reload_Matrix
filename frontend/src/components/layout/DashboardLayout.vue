<template>
  <div class="dashboard-layout">
    <SidebarNav :is-collapsed="sidebarCollapsed" @toggle="sidebarCollapsed = !sidebarCollapsed" />
    <div class="main-content" :class="{ expanded: sidebarCollapsed }">
      <TopHeader :title="pageTitle" @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />
      <div v-if="showTrialBanner" :class="['trial-banner', { expired: isExpired }]">
        <template v-if="isExpired">
          Tu período de prueba ha expirado. Contacta con soporte para reactivar el servicio.
        </template>
        <template v-else>
          Te quedan <strong>{{ daysRemaining }}</strong> día{{ daysRemaining === 1 ? '' : 's' }} de tu período de prueba de 60 días. Contacta con soporte para mantener el servicio.
        </template>
      </div>
      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
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
  created() {
    const companyId = this.$store.state.auth.user?.company_id
    if (companyId && !this.$store.state.company.company) {
      this.$store.dispatch('company/fetchCompany', companyId)
    }
  },
  computed: {
    ...mapState('company', ['company']),
    showTrialBanner() {
      if (!this.company?.is_trial) return false
      return this.daysRemaining <= 10
    },
    isExpired() {
      return this.daysRemaining <= 0
    },
    daysRemaining() {
      if (!this.company?.created_at) return 60
      const created = new Date(this.company.created_at)
      const now = new Date()
      const elapsed = Math.floor((now - created) / (1000 * 60 * 60 * 24))
      return 60 - elapsed
    },
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

.trial-banner {
  background: #fff3cd;
  color: #856404;
  padding: 0.75rem 1.5rem;
  text-align: center;
  font-weight: 600;
  border-bottom: 1px solid #ffc107;
}

.trial-banner.expired {
  background: #f8d7da;
  color: #721c24;
  border-color: #f5c6cb;
}
</style>
