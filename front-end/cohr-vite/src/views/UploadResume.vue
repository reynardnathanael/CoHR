<template>
    <div class="grid grid-cols-1 gap-8">
        <!-- <FileUpload name="demo[]" customUpload @uploader="onTemplatedUpload" :multiple="true" accept="application/pdf" :maxFileSize="1000000" @select="onSelectedFiles">
            <template #header="{ chooseCallback, uploadCallback, clearCallback, files }">
                <div class="flex flex-wrap justify-between items-center flex-1 gap-4">
                    <div class="flex gap-2">
                        <Button @click="chooseCallback()" icon="pi pi-file-pdf" rounded variant="outlined" severity="secondary"></Button>
                        <Button @click="uploadEvent(uploadCallback)" icon="pi pi-cloud-upload" rounded variant="outlined" severity="success" :disabled="!files || files.length === 0"></Button>
                        <Button @click="clearCallback()" icon="pi pi-times" rounded variant="outlined" severity="danger" :disabled="!files || files.length === 0"></Button>
                    </div>
                    <ProgressBar :value="totalSizePercent" :showValue="false" class="md:w-20rem h-1 w-full md:ml-auto">
                        <span class="whitespace-nowrap">{{ formatSize(totalSize) }} / 1 MB</span>
                    </ProgressBar>
                </div>
            </template>
            <template #content="{ files, uploadedFiles, removeUploadedFileCallback, removeFileCallback, messages }">
                <div class="flex flex-col gap-8 pt-4">
                    <Message v-for="message of messages" :key="message" :class="{ 'mb-8': !files.length && !uploadedFiles.length}" severity="error">
                        {{ message }}
                    </Message>

                    <div v-if="files.length > 0">
                        <h5>Pending</h5>
                        <div class="flex flex-wrap gap-4">
                            <div v-for="(file, index) of files" :key="file.name + file.type + file.size" class="p-8 rounded-border flex flex-col border border-surface items-center gap-4">
                                <div>
                                    <i class="pi pi-file-pdf text-4xl text-primary"></i>
                                </div>
                                <span class="font-semibold text-ellipsis max-w-60 whitespace-nowrap overflow-hidden">{{ file.name }}</span>
                                <div>{{ formatSize(file.size) }}</div>
                                <Badge value="Pending" severity="warn" />
                                <Button icon="pi pi-times" @click="onRemoveTemplatingFile(file, removeFileCallback, index)" variant="outlined" rounded severity="danger" />
                            </div>
                        </div>
                    </div>

                    <div v-if="uploadedFiles.length > 0">
                        <h5>Completed</h5>
                        <div class="flex flex-wrap gap-4">
                            <div v-for="(file, index) of uploadedFiles" :key="file.name + file.type + file.size" class="p-8 rounded-border flex flex-col border border-surface items-center gap-4">
                                <div>
                                    <i class="pi pi-file-pdf text-4xl text-primary"></i>
                                </div>
                                <span class="font-semibold text-ellipsis max-w-60 whitespace-nowrap overflow-hidden">{{ file.name }}</span>
                                <div>{{ formatSize(file.size) }}</div>
                                <Badge value="Completed" class="mt-4" severity="success" />
                                <Button icon="pi pi-times" @click="onRemoveUploadedFile(file, removeUploadedFileCallback, index)" variant="outlined" rounded severity="danger" />
                            </div>
                        </div>
                    </div>
                </div>
            </template>
            <template #empty>
                <div class="flex items-center justify-center flex-col">
                    <i class="pi pi-cloud-upload !border-2 !rounded-full !p-8 !text-4xl !text-muted-color" />
                    <p class="mt-6 mb-0">Drag and drop files to here to upload.</p>
                </div>
            </template>
        </FileUpload> -->
        <div class="px-4 mt-3 w-full rounded-lg" style="background-color: #1C1C1C;">
            <p class="text-white py-3 text-sm">Upload file attachments</p>
            <FileUpload :showUploadButton="false" ref="fileUpload" name="files" :multiple="false" accept="image/*,application/pdf" :auto="false" style="background-color: #1C1C1C; border: 0;">
                <template #empty>
                    <div class="flex justify-center items-center space-x-4 border-2 py-4 border-dashed rounded-lg" style="border-color: #1C1C1C;">
                        <!-- <i class="pi pi-cloud-upload !text-4xl" /> -->
                        <img src="../assets/img/cloud.png" alt="" class="h-20">
                        
                    </div> 
                </template>
            </FileUpload>
            <p class="text-white py-3 text-sm">Only IMAGE & PDF files</p>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const totalSize = ref(0);
const totalSizePercent = ref(0);

const onSelectedFiles = (event) => {
    let _totalSize = 0;
    event.files.forEach((file) => {
        _totalSize += file.size;
    });
    totalSize.value = _totalSize;
    totalSizePercent.value = Math.min(Math.round((_totalSize / 1000000) * 100), 100);
};

const uploadEvent = (uploadCallback) => {
    uploadCallback();
};

const onTemplatedUpload = (event) => {
    // In a real app, you would make an axios/fetch request to your backend here.
    // By using customUpload, this allows us to simulate a successful upload for the UI.
    console.log("File uploaded successfully!");
};

const onRemoveTemplatingFile = (file, removeFileCallback, index) => {
    removeFileCallback(index);
    totalSize.value -= file.size;
    totalSizePercent.value = Math.min(Math.round((totalSize.value / 1000000) * 100), 100);
};

const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};
</script>