<style scoped>
/* Allow the circle to overflow outside the progress bar boundaries */
:deep(.p-progressbar) {
    overflow: visible !important;
}

:deep(.p-progressbar-value) {
    position: relative;
    overflow: visible !important;
    border-radius: 6px; /* Rounds the inner bar since the parent no longer clips it */
}

/* Create the circle and attach it to the end of the progress bar value */
:deep(.p-progressbar-value::after) {
    content: '';
    position: absolute;
    top: 50%;
    right: 0;
    transform: translate(25%, -50%);
    width: 1.5rem;
    height: 1.5rem;
    background-color: #ffffff; 
    border: 3px solid rgb(55, 48, 163);
    border-radius: 50%;
    z-index: 10;
}
</style>

<template>
    <div class="flex flex-col w-full">
        <div class="card flex justify-center">
            <Chart type="radar" :data="chartData" :options="chartOptions" class="w-full md:w-[30rem]" />
        </div>
    </div>
    <div class="card flex flex-col gap-4 w-full mt-4">
        <!-- Header Row -->
        <div class="flex items-center w-full font-bold">
            <div class="w-1/6 text-lg text-right pr-8">Aptitude</div>
            <div class="w-2/3 grid grid-cols-10 text-right">
                <span>1</span>
                <span>2</span>
                <span>3</span>
                <span>4</span>
                <span>5</span>
                <span>6</span>
                <span>7</span>
                <span>8</span>
                <span>9</span>
                <span>10</span>
            </div>
            <div class="w-1/6"></div>
        </div>
        
        <!-- Result Row -->
        <div class="flex items-center w-full">
            <div class="w-1/6 text-right pr-8">General Abilities</div>
            <div class="w-2/3">
                <ProgressBar :value="60">6</ProgressBar>
            </div>
            <div class="w-1/6 pl-4 text-left">Medium</div>
        </div>
        <div class="flex items-center w-full">
            <div class="w-1/6 text-right pr-8">Numbers</div>
            <div class="w-2/3">
                <ProgressBar :value="100">10</ProgressBar>
            </div>
            <div class="w-1/6 pl-4 text-left">High</div>
        </div>
        <div class="flex items-center w-full">
            <div class="w-1/6 text-right pr-8">Words</div>
            <div class="w-2/3">
                <ProgressBar :value="80">8</ProgressBar>
            </div>
            <div class="w-1/6 pl-4 text-left">High</div>
        </div>
        <div class="flex items-center w-full">
            <div class="w-1/6 text-right pr-8">Shapes</div>
            <div class="w-2/3">
                <ProgressBar :value="30">3</ProgressBar>
            </div>
            <div class="w-1/6 pl-4 text-left">Low</div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

onMounted(() => {
    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
});

const chartData = ref();
const chartOptions = ref();
        
const setChartData = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--p-text-color');

    return {
        labels: ['Eating', 'Drinking', 'Sleeping', 'Designing', 'Coding', 'Cycling', 'Running'],
        datasets: [
            {
                label: 'Required Skills',
                borderColor: documentStyle.getPropertyValue('--p-gray-400'),
                pointBackgroundColor: documentStyle.getPropertyValue('--p-gray-400'),
                pointBorderColor: documentStyle.getPropertyValue('--p-gray-400'),
                pointHoverBackgroundColor: textColor,
                pointHoverBorderColor: documentStyle.getPropertyValue('--p-gray-400'),
                data: [65, 59, 90, 81, 56, 55, 40]
            },
            {
                label: 'Actual Skills',
                borderColor: documentStyle.getPropertyValue('--p-pink-400'),
                pointBackgroundColor: documentStyle.getPropertyValue('--p-pink-400'),
                pointBorderColor: documentStyle.getPropertyValue('--p-pink-400'),
                pointHoverBackgroundColor: textColor,
                pointHoverBorderColor: documentStyle.getPropertyValue('--p-pink-400'),
                data: [28, 48, 40, 19, 96, 27, 100]
            }
        ]
    };
};
const setChartOptions = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--p-text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');

    return {
        plugins: {
            legend: {
                labels: {
                    color: textColor
                }
            }
        },
        scales: {
            r: {
                grid: {
                    color: textColorSecondary
                }
            }
        }
    };
}
</script>