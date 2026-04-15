<template>
    <div class="grid grid-cols-12 gap-8">
        <div class="col-span-12 grid grid-cols-1 xl:grid-cols-2 gap-8">
            <div class="card">
                <div class="text-right">
                    <Button @click="goToUpload" label="Add" style="background-color: #c7d2fe; border: 2px solid #1e1b4b; color: #1e1b4b;" icon="pi pi-plus" iconPos="right" rounded class="hover:ring-2 mb-1" />
                </div>
                <DataTable class="main-table" :value="customers" paginator :rows="5" :rowsPerPageOptions="[5, 10, 20, 50]" scrollable selectionMode="single" scrollHeight="400px" tableStyle="min-width: 100%">
                    <Column field="name" header="Name" style="width: 25%"></Column>
                    <Column field="status" header="Status" style="width: 25%">
                    <template #body="{ data, index }">
                        <Badge :value="data.status" :severity="data.status === 'New' ? 'info' : data.status === 'In Progress' ? 'warn' : 'success'"></Badge>
                    </template>
                    </Column>
                    <Column field="score" header="Score" style="width: 25%;"></Column>
                    <Column field="result" header="Result" style="width: 25%">
                        <template #body="{ data, index }">
                            <Button style="font-size: x-small;" label="Open" icon="pi pi-external-link" iconPos="right" :severity="index % 2 === 0 ? 'primary' : null" :style="index % 2 !== 0 ? 'background-color: #3730a3; border-color: #3730a3; color: white;' : ''" size="small" />
                        </template>
                    </Column>
                </DataTable>
            </div>
            <div class="card">
            </div>
        </div>

        <!-- <StatsWidget />

        <div class="col-span-12 xl:col-span-6">
            <RecentSalesWidget />
            <BestSellingWidget />
        </div>
        <div class="col-span-12 xl:col-span-6">
            <RevenueStreamWidget />
            <NotificationsWidget />
        </div> -->
    </div>
</template>

<script setup>
import BestSellingWidget from '@/components/dashboard/BestSellingWidget.vue';
import NotificationsWidget from '@/components/dashboard/NotificationsWidget.vue';
import RecentSalesWidget from '@/components/dashboard/RecentSalesWidget.vue';
import RevenueStreamWidget from '@/components/dashboard/RevenueStreamWidget.vue';
import StatsWidget from '@/components/dashboard/StatsWidget.vue';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const customers = ref([
    { name: 'John Doe', status: 'New', score: '', result: 'Passed' },
    { name: 'Jane Smith', status: 'In Progress', score: '', result: 'Passed' },
    { name: 'Sam Wilson', status: 'In Progress', score: '', result: 'Passed' },
    { name: 'Alice Johnson', 'status': 'Finished', score: 8, result: 'Failed' },
    { name: 'Bob Brown', status: 'Finished', score: 9, result: 'Passed' }
]);

const router = useRouter();

const goToUpload = () => {
    router.push('/upload');
};
</script>

<style scoped>
/* .main-table :deep(.p-datatable-table-container) {
    overflow-x: hidden !important;
} */
</style>
