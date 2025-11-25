import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import './index.css'
import App from './App.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import Home from './views/Home.vue'

const pinia = createPinia()

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { 
      path: '/', 
      name: 'home',
      component: Home 
    },
    { 
      path: '/login', 
      name: 'login',
      component: Login 
    },
    { 
      path: '/register', 
      name: 'register',
      component: Register 
    },
    {
      path: '/comments/:id',
      name: 'comment-detail',
      component: () => import('./views/CommentDetail.vue')
    }
  ],
})

const app = createApp(App)

app.use(pinia)
app.use(router)
app.mount('#app')
