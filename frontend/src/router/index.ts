import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/fortune',
    },
    {
      path: '/fortune',
      name: 'fortune',
      component: () => import('@/views/fortune/FortuneView.vue'),
      meta: { title: '运势看板', tabBar: true, requiresAuth: true },
    },
    {
      path: '/answer',
      name: 'answer',
      component: () => import('@/views/answer/AnswerView.vue'),
      meta: { title: '答案之书', tabBar: true, requiresAuth: true },
    },
    {
      path: '/plaza',
      name: 'plaza',
      component: () => import('@/views/plaza/PlazaView.vue'),
      meta: { title: '分享广场', tabBar: true, requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/profile/ProfileView.vue'),
      meta: { title: '我的', tabBar: true, requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { title: '登录' },
    },
  ],
})

// 登录状态检测（示例：检查 localStorage 中是否有 token）
function isAuthenticated(): boolean {
  return !!localStorage.getItem('token')
}

// 全局前置守卫
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} | 心运岛`
  }

  // 需要登录的页面
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
