import { createRouter, createWebHistory } from 'vue-router';
import AppLayout from '@/layout/AppLayout.vue';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            component: AppLayout, // This acts as the wrapper for all admin pages
            children: [
                {
                    path: '/dashboard',
                    name: 'dashboard',
                    component: () => import('@/views/Dashboard.vue')
                },
                {
                    path: '/upload-resume',
                    name: 'upload-resume',
                    component: () => import('@/views/UploadResume.vue')
                },
            ]
        }
    ]
});

export default router;
