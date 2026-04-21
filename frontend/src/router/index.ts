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
      meta: { title: '运势看板', tabBar: true },
    },
    {
      path: '/answer',
      name: 'answer',
      component: () => import('@/views/answer/AnswerView.vue'),
      meta: { title: '答案之书', tabBar: true },
    },
    {
      path: '/plaza',
      name: 'plaza',
      component: () => import('@/views/plaza/PlazaView.vue'),
      meta: { title: '分享广场', tabBar: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/profile/ProfileView.vue'),
      meta: { title: '我的', tabBar: true },
    },
    // 登录页（后续添加）
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { title: '登录' },
    },
  ],
})

// 动态设置页面标题
router.beforeEach((to, _from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} | 心运岛`
  }
  next()
})

export default router