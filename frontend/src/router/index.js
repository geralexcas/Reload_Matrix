import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Auth/LoginView.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/Auth/RegisterView.vue'),
    meta: { guest: true }
  },
  {
    path: '/setup',
    name: 'setup',
    component: () => import('@/views/Company/SetupView.vue')
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/components/layout/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard-home',
        component: () => import('@/views/DashboardView.vue')
      },
      {
        path: '/companies',
        name: 'companies',
        component: () => import('@/views/Company/SetupView.vue')
      },
      {
        path: '/partners',
        name: 'partners',
        component: () => import('@/views/Partners/PartnersView.vue')
      },
      {
        path: '/partners/new',
        name: 'partner-new',
        component: () => import('@/views/Partners/PartnerFormView.vue')
      },
      {
        path: '/partners/edit/:id',
        name: 'partner-edit',
        component: () => import('@/views/Partners/PartnerFormView.vue')
      },
      {
        path: '/inventory',
        name: 'inventory',
        component: () => import('@/views/Inventory/ProductListView.vue')
      },
      {
        path: '/inventory/new',
        name: 'inventory-new',
        component: () => import('@/views/Inventory/ProductFormView.vue')
      },
      {
        path: '/inventory/edit/:id',
        name: 'inventory-edit',
        component: () => import('@/views/Inventory/ProductFormView.vue')
      },
      {
        path: '/invoicing',
        name: 'invoicing',
        component: () => import('@/views/Invoicing/InvoicingView.vue')
      },
      {
        path: '/accounting',
        name: 'accounting',
        component: () => import('@/views/Accounting/IndexView.vue')
      },
      {
        path: '/accounting/chart-of-accounts',
        name: 'chart-of-accounts',
        component: () => import('@/views/Accounting/ChartOfAccountsListView.vue')
      },
      {
        path: '/accounting/journal-entries',
        name: 'journal-entries',
        component: () => import('@/views/Accounting/JournalEntryListView.vue')
      },
      {
        path: '/accounting/journal-entries/:entryId',
        name: 'journal-entry-detail',
        component: () => import('@/views/Accounting/JournalEntryDetailView.vue')
      },
      {
        path: '/accounting/journal-entries/new',
        name: 'journal-entry-new',
        component: () => import('@/views/Accounting/JournalEntryDetailView.vue')
      },
      {
        path: '/accounting/libro-mayor',
        name: 'libro-mayor',
        component: () => import('@/views/Accounting/LibroMayorView.vue')
      },
      {
        path: '/accounting/libro-ventas',
        name: 'libro-ventas',
        component: () => import('@/views/Accounting/LibroVentasView.vue')
      },
      {
        path: '/accounting/libro-compras',
        name: 'libro-compras',
        component: () => import('@/views/Accounting/LibroComprasView.vue')
      },
      {
        path: '/accounting/declaracion-iva',
        name: 'declaracion-iva',
        component: () => import('@/views/Accounting/DeclaracionIVAView.vue')
      },
      {
        path: '/accounting/reporte-retenciones',
        name: 'reporte-retenciones',
        component: () => import('@/views/Accounting/ReporteRetencionesView.vue')
      },
      {
        path: '/accounting/reporte-ingresos',
        name: 'reporte-ingresos',
        component: () => import('@/views/Accounting/ReporteIngresosView.vue')
      },
      {
        path: '/accounting/reporte-patrimonio',
        name: 'reporte-patrimonio',
        component: () => import('@/views/Accounting/ReportePatrimonioView.vue')
      },
      {
        path: '/accounting/estado-resultados',
        name: 'estado-resultados',
        component: () => import('@/views/Accounting/EstadoResultadosView.vue')
      },
      {
        path: '/accounting/balance-general',
        name: 'balance-general',
        component: () => import('@/views/Accounting/BalanceGeneralView.vue')
      },
      {
        path: '/admin/users',
        name: 'admin-users',
        component: () => import('@/views/Admin/UsersView.vue')
      },
      {
        path: '/admin/backups',
        name: 'admin-backups',
        component: () => import('@/views/Admin/BackupView.vue')
      },
      {
        path: '/repair',
        name: 'repair',
        component: () => import('@/views/Repair/RepairView.vue')
      },
      {
        path: '/repair/:id',
        name: 'repair-detail',
        component: () => import('@/views/Repair/RepairDetailView.vue')
      },
      {
        path: '/wallet',
        name: 'wallet',
        component: () => import('@/views/Wallet/WalletView.vue')
      },
      {
        path: '/purchases',
        name: 'purchases',
        component: () => import('@/views/Purchases/IndexView.vue')
      },
      {
        path: '/treasury',
        name: 'treasury',
        component: () => import('@/views/Treasury/IndexView.vue')
      },
      {
        path: '/treasury/bank-accounts',
        name: 'treasury-bank-accounts',
        component: () => import('@/views/Treasury/BankAccountsView.vue')
      },
      {
        path: '/treasury/cash-accounts',
        name: 'treasury-cash-accounts',
        component: () => import('@/views/Treasury/CashAccountsView.vue')
      },
      {
        path: '/treasury/transactions',
        name: 'treasury-transactions',
        component: () => import('@/views/Treasury/TransactionsView.vue')
      },
      {
        path: '/treasury/transfers',
        name: 'treasury-transfers',
        component: () => import('@/views/Treasury/TransfersView.vue')
      },
      {
        path: '/treasury/checks',
        name: 'treasury-checks',
        component: () => import('@/views/Treasury/CheckRegisterView.vue')
      },
      {
        path: '/treasury/cash-flow',
        name: 'treasury-cash-flow',
        component: () => import('@/views/Treasury/CashFlowView.vue')
      },
      {
        path: '/treasury/reconciliations',
        name: 'treasury-reconciliations',
        component: () => import('@/views/Treasury/BankReconciliationView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = store.getters['auth/isLoggedIn']

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      next({ name: 'login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  } else if (to.matched.some(record => record.meta.guest)) {
    if (isLoggedIn) {
      next({ name: 'dashboard' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
