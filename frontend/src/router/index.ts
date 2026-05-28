// frontend/src/router/index.ts — 路由配置
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
    { path: '/email/:token/:emailId', name: 'email-detail', component: () => import('../views/EmailDetailView.vue') },
    { path: '/temp-email-for-:slug', name: 'landing', component: () => import('../views/LandingView.vue') },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('../views/NotFoundView.vue') },
  ],
})

export default router
