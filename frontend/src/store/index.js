import { createStore } from 'vuex'
import auth from './modules/auth'
import company from './modules/company'
import admin from './modules/admin'
import inventory from './modules/inventory'
import accounting from './modules/accounting'
import partners from './modules/partners'
import wallet from './modules/wallet'
import repair from './modules/repair'
import invoicing from './modules/invoicing'
import treasury from './modules/treasury'
import purchases from './modules/purchases'

export default createStore({
  state: {},
  mutations: {},
  actions: {},
  modules: {
    auth,
    company,
    admin,
    inventory,
    accounting,
    partners,
    wallet,
    repair,
    invoicing,
    treasury,
    purchases
  }
})