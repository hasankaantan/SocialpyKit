import {
  createRouter,
  createWebHistory,
  type NavigationGuardWithThis,
  type RouteRecordRaw,
} from "vue-router"

import { useAuthStore } from "@/stores/auth"

declare module "vue-router" {
  interface RouteMeta {
    /** Route requires a signed-in user. Defaults to false. */
    requiresAuth?: boolean
    /** Route requires an admin user. Implies requiresAuth. */
    requiresAdmin?: boolean
    /** Route is only for unauthenticated users (e.g. /login). */
    publicOnly?: boolean
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/pages/LoginPage.vue"),
    meta: { publicOnly: true },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("@/pages/RegisterPage.vue"),
    meta: { publicOnly: true },
  },
  {
    path: "/dashboard",
    component: () => import("@/pages/dashboard/DashboardLayout.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "dashboard",
        component: () => import("@/pages/dashboard/DashboardHome.vue"),
      },
      {
        path: "profile",
        name: "profile",
        component: () => import("@/pages/dashboard/ProfilePage.vue"),
      },
      {
        path: "users",
        name: "users",
        component: () => import("@/pages/dashboard/UsersPage.vue"),
        meta: { requiresAdmin: true },
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("@/pages/NotFoundPage.vue"),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

const authGuard: NavigationGuardWithThis<undefined> = async (to) => {
  const store = useAuthStore()

  // Hydrate the current user once if a token is present but the store
  // has not seen the backend yet (typical for a page refresh).
  if (store.isAuthenticated && store.user === null) {
    try {
      await store.fetchMe()
    } catch {
      store.logout()
    }
  }

  if (to.meta.publicOnly && store.isAuthenticated) {
    return { name: "dashboard" }
  }

  const requiresAuth = to.meta.requiresAuth || to.meta.requiresAdmin
  if (requiresAuth && !store.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } }
  }

  if (to.meta.requiresAdmin && store.user?.role !== "admin") {
    return { name: "dashboard" }
  }

  return true
}

router.beforeEach(authGuard)
