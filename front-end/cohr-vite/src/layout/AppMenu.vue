<script setup>
import { ref } from 'vue';
import AppMenuItem from './AppMenuItem.vue';

const model = ref([
    {
        label: 'Home',
        items: [
            {
                label: 'Dashboard',
                icon: 'pi pi-fw pi-home',
                to: '/dashboard'
            }
        ]
    },
    {
        label: 'Actions',
        items: [
            {
                label: 'Upload Resume',
                icon: 'pi pi-fw pi-id-card',
                to: '/upload-resume'
            },
            // {
            //     label: 'Input',
            //     icon: 'pi pi-fw pi-check-square',
            //     to: '/uikit/input'
            // },
            // {
            //     label: 'Button',
            //     icon: 'pi pi-fw pi-mobile',
            //     to: '/uikit/button',
            //     class: 'rotated-icon'
            // },
        ]
    },
    // {
    //     label: 'Prime Blocks',
    //     icon: 'pi pi-fw pi-prime',
    //     path: '/blocks',
    //     items: [
    //         {
    //             label: 'Free Blocks',
    //             icon: 'pi pi-fw pi-eye',
    //             to: '/blocks/free'
    //         },
    //         {
    //             label: 'All Blocks',
    //             icon: 'pi pi-fw pi-globe',
    //             url: 'https://blocks.primevue.org/',
    //             target: '_blank'
    //         }
    //     ]
    // },
    // {
    //     label: 'Pages',
    //     icon: 'pi pi-fw pi-briefcase',
    //     path: '/pages',
    //     items: [
    //         {
    //             label: 'Landing',
    //             icon: 'pi pi-fw pi-globe',
    //             to: '/landing'
    //         },
    //         {
    //             label: 'Auth',
    //             icon: 'pi pi-fw pi-user',
    //             path: '/auth',
    //             items: [
    //                 {
    //                     label: 'Login',
    //                     icon: 'pi pi-fw pi-sign-in',
    //                     to: '/auth/login'
    //                 },
    //                 {
    //                     label: 'Error',
    //                     icon: 'pi pi-fw pi-times-circle',
    //                     to: '/auth/error'
    //                 },
    //                 {
    //                     label: 'Access Denied',
    //                     icon: 'pi pi-fw pi-lock',
    //                     to: '/auth/access'
    //                 }
    //             ]
    //         },
    //         {
    //             label: 'Crud',
    //             icon: 'pi pi-fw pi-pencil',
    //             to: '/pages/crud'
    //         },
    //         {
    //             label: 'Not Found',
    //             icon: 'pi pi-fw pi-exclamation-circle',
    //             to: '/pages/notfound'
    //         },
    //         {
    //             label: 'Empty',
    //             icon: 'pi pi-fw pi-circle-off',
    //             to: '/pages/empty'
    //         }
    //     ]
    // },
    // {
    //     label: 'Hierarchy',
    //     icon: 'pi pi-fw pi-align-left',
    //     path: '/hierarchy',
    //     items: [
    //         {
    //             label: 'Submenu 1',
    //             icon: 'pi pi-fw pi-align-left',
    //             path: '/submenu_1',
    //             items: [
    //                 {
    //                     label: 'Submenu 1.1',
    //                     icon: 'pi pi-fw pi-align-left',
    //                     path: '/submenu_1_1',
    //                     items: [
    //                         {
    //                             label: 'Submenu 1.1.1',
    //                             icon: 'pi pi-fw pi-align-left'
    //                         },
    //                         {
    //                             label: 'Submenu 1.1.2',
    //                             icon: 'pi pi-fw pi-align-left'
    //                         },
    //                         {
    //                             label: 'Submenu 1.1.3',
    //                             icon: 'pi pi-fw pi-align-left'
    //                         }
    //                     ]
    //                 },
    //                 {
    //                     label: 'Submenu 1.2',
    //                     icon: 'pi pi-fw pi-align-left',
    //                     path: '/submenu_1_2',
    //                     items: [
    //                         {
    //                             label: 'Submenu 1.2.1',
    //                             icon: 'pi pi-fw pi-align-left'
    //                         }
    //                     ]
    //                 }
    //             ]
    //         },
    //         {
    //             label: 'Submenu 2',
    //             icon: 'pi pi-fw pi-align-left',
    //             path: '/submenu_2',
    //             items: [
    //                 {
    //                     label: 'Submenu 2.1',
    //                     icon: 'pi pi-fw pi-align-left',
    //                     path: '/submenu_2_1',
    //                     items: [
    //                         {
    //                             label: 'Submenu 2.1.1',
    //                             icon: 'pi pi-fw pi-align-left'
    //                         },
    //                         {
    //                             label: 'Submenu 2.1.2',
    //                             icon: 'pi pi-fw pi-align-left'
    //                         }
    //                     ]
    //                 },
    //                 {
    //                     label: 'Submenu 2.2',
    //                     icon: 'pi pi-fw pi-align-left',
    //                     path: '/submenu_2_2',
    //                     items: [
    //                         {
    //                             label: 'Submenu 2.2.1',
    //                             icon: 'pi pi-fw pi-align-left'
    //                         }
    //                     ]
    //                 }
    //             ]
    //         }
    //     ]
    // },
    // {
    //     label: 'Get Started',
    //     path: '/start',
    //     items: [
    //         {
    //             label: 'Documentation',
    //             icon: 'pi pi-fw pi-book',
    //             to: '/start/documentation'
    //         },
    //         {
    //             label: 'View Source',
    //             icon: 'pi pi-fw pi-github',
    //             url: 'https://github.com/primefaces/sakai-vue',
    //             target: '_blank'
    //         }
    //     ]
    // }
]);
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model" :key="item">
            <app-menu-item v-if="!item.separator" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped>
.layout-menu {
    :deep(.layout-menuitem-root-text) {
        font-size: 1rem !important; /* Adjust the root category label size */
    }

    :deep(a) {
        /* Add some extra padding to make the clickable area larger */
        padding: 1rem 1.5rem;

        .layout-menuitem-icon {
            font-size: 1.5rem; /* Adjust to enlarge the icon */
        }

        .layout-menuitem-text {
            font-size: 1.25rem; /* Adjust to enlarge the text */
        }
    }
}
</style>
