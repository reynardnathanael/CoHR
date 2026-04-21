<template>
    <div class="grid grid-cols-12 gap-8">
        <div class="card col-span-12">
            <div class="px-4 mt-3 w-full rounded-2xl bg-indigo-900">
                <p class="text-white text-lg pt-3 font-semibold">Upload a CV or Resume</p>
                <FileUpload @select="onFileSelect" :showUploadButton="false" ref="fileUpload" name="files" :multiple="false" accept="application/pdf" :auto="false" style="border: 0;" class="bg-indigo-900">
                    <template #empty>
                        <div class="flex justify-center items-center space-x-4 border-2 py-4 border-dashed rounded-2xl" style="border-color: #1C1C1C;">
                            <!-- <i class="pi pi-cloud-upload !text-4xl" /> -->
                            <div class="flex flex-col items-center">
                                <img src="../assets/img/cloud.png" alt="" class="h-20 w-20">
                                <p class="text-lg font-semibold">Drag and drop your file here</p>
                            </div>
                        </div> 
                    </template>
                    <template #content="{ files, removeFileCallback }">
                        <div v-if="files.length > 0" class="flex flex-col gap-4 mt-4">
                            <div v-for="(file, index) of files" :key="file.name + file.type + file.size" class="p-4 rounded-xl flex items-center gap-4 bg-indigo-50 border border-indigo-700">
                                <i class="pi pi-file-pdf text-9xl text-red-400" style="font-size: 2rem;"></i>
                                <div class="flex flex-col flex-1 overflow-hidden">
                                    <span class="font-semibold text-ellipsis whitespace-nowrap overflow-hidden text-indigo-800">{{ file.name }}</span>
                                    <span class="text-sm text-indigo-800">{{ formatSize(file.size) }}</span>
                                </div>
                                <Button icon="pi pi-times" @click="removeFileCallback(index)" variant="text" rounded severity="danger" class="hover:bg-indigo-700" />
                            </div>
                        </div>
                    </template>
                </FileUpload>
                <p class="text-white py-3 text-sm">Only PDF files</p>
            </div>
            <div class="my-8 flex justify-center">
                <Select v-model="selectedCountry" :options="roles" filter optionLabel="name" placeholder="Select job position" class="w-full">
                    <template #value="slotProps">
                        <div v-if="slotProps.value" class="flex items-center">
                            <div>{{ slotProps.value.name }}</div>
                        </div>
                        <span v-else>
                            {{ slotProps.placeholder }}
                        </span>
                    </template>
                    <template #option="slotProps">
                        <div class="flex items-center">
                            <div>{{ slotProps.option.name }}</div>
                        </div>
                    </template>
                </Select>
            </div>
            <div class="flex flex-col gap-1">
                <label for="description" class="text-lg font-medium ">Job Description</label>
                <Textarea class="text-justify" id="description" v-model="jobDescription" rows="5" fluid autoResize readonly />
            </div>
            <div class="flex justify-center mt-10 pb-5">
                <Button :loading="loading" class="w-40 !bg-indigo-200 !text-black !border-indigo-900" type="button" label="Submit" icon="pi pi-upload" iconPos="right" @click="createPostFile" style="border-radius: 16px;"></Button>
            </div>
        </div>
        <!-- <div class="card col-span-12 lg:col-span-7">
            <div class="flex flex-col gap-1">
                <label for="description" class="text-lg font-medium">Result</label>
                <Textarea class="text-justify" id="description" v-model="result" rows="5" fluid autoResize readonly />
            </div>
        </div> -->
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const fileUpload = ref();
const totalSize = ref(0);
const totalSizePercent = ref(0);
const selectedCountry = ref();
const jobDescription = ref("Cras nec velit aliquet, tempus velit eu, luctus lacus. Nulla vulputate lacus nisl, accumsan tristique magna rutrum id. Sed nisi magna, cursus vel velit eget, maximus cursus lacus. Donec non libero magna. Vestibulum vitae finibus ante. Praesent sit amet turpis faucibus, posuere augue a, posuere nisl. Donec ut enim varius, porttitor ligula in, accumsan neque. Etiam vel convallis lorem. Aliquam erat volutpat. Vestibulum gravida urna quis dolor ornare, ullamcorper condimentum justo aliquet. In ligula tortor, posuere accumsan diam id, vestibulum porta metus. Praesent eget imperdiet eros. \n\nCurabitur non quam sed magna tincidunt iaculis nec ac felis. Quisque pulvinar ligula neque, vitae hendrerit felis hendrerit ac. Vivamus nec vehicula elit, sit amet condimentum quam. Morbi quis orci ac massa semper congue. Aliquam eget imperdiet nibh, vel bibendum neque. Etiam sit amet massa ut sem feugiat euismod. Maecenas convallis mollis libero, a bibendum risus placerat nec. Praesent blandit faucibus neque vitae convallis. Nam sed ornare augue.Proin eu ullamcorper orci. In at erat nibh. Vestibulum a turpis sapien. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.");
const loading = ref(false);
const result = ref("Curabitur a elit nec quam finibus vehicula. Cras nec lacus vitae diam euismod maximus ut et mauris. Vestibulum aliquet turpis eu erat luctus malesuada. Curabitur id accumsan nisi. Mauris ut diam a tortor varius hendrerit nec a sapien. Aenean congue mi libero, id molestie sapien egestas vitae. Pellentesque turpis erat, cursus vel nunc ac, iaculis pellentesque justo. Etiam euismod lectus mollis est consequat, in fringilla purus dignissim. Aliquam viverra, tortor et sagittis auctor, elit quam fermentum lorem, ut venenatis sapien lacus ac sem. Cras tempor id sapien at efficitur. Fusce sodales blandit orci. Nullam purus augue, efficitur rutrum ipsum in, luctus laoreet elit. Maecenas et fringilla nunc. Pellentesque ac metus elit. Pellentesque et molestie tortor. Aliquam pulvinar nibh turpis, ut vulputate mi scelerisque vel. Cras nulla orci, faucibus quis libero non, bibendum consectetur purus. Maecenas vel nisi eget arcu egestas consequat. \n\nSed consequat risus felis, a ullamcorper felis elementum facilisis. Donec dignissim libero non interdum blandit. Interdum et malesuada fames ac ante ipsum primis in faucibus.Cras lacus nisl, tempus volutpat pharetra nec, vehicula sed dolor. Suspendisse sapien lorem, tempus ut pharetra in, tincidunt non justo. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nullam semper, erat eu convallis posuere, turpis mauris placerat felis, sed dictum sem augue varius libero. Phasellus eleifend lacus purus, eu tempor metus pulvinar ac. Duis euismod nibh malesuada rutrum viverra. Vivamus gravida molestie nisi ac auctor. Nulla facilisi. Ut eget risus diam. Nunc hendrerit nisi at lectus elementum, eu rutrum massa fermentum. Donec maximus mi nec pellentesque tempor. Integer tempor felis sed dui feugiat, dignissim egestas orci vehicula. Fusce volutpat a ligula non posuere. Quisque eget lacus dapibus risus pulvinar suscipit. Sed a libero et quam interdum pharetra. Duis lobortis tincidunt arcu, nec maximus ante pellentesque ac. Sed velit sapien, tempus id molestie nec, ultricies id urna.Etiam lorem turpis, semper vitae dignissim vitae, mattis at mauris. Etiam cursus nisl nec congue mattis. Maecenas iaculis eleifend quam. Aliquam nisi mi, sollicitudin id diam nec, elementum tempus arcu. Curabitur et est id massa semper scelerisque. Duis ut vulputate felis. In malesuada ante posuere, finibus nunc ut, egestas mauris. \n\nSuspendisse at volutpat eros. Duis eget feugiat erat. Maecenas et suscipit mauris. Curabitur id sollicitudin erat. Aenean ultricies felis et mauris viverra pellentesque. Duis tempor nisl mollis ante malesuada, at elementum lorem pharetra. Quisque ultricies ac erat vitae gravida. Ut vitae ornare tellus, sed cursus velit. Quisque ipsum mi, pretium et imperdiet sit amet, euismod sed mi. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Maecenas tristique posuere tincidunt. Cras faucibus, enim in molestie tincidunt, magna neque lobortis elit, vitae bibendum eros justo at risus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Ut efficitur pretium velit vitae mattis. Sed quis nunc porta turpis tincidunt feugiat. Phasellus nec tortor justo. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Phasellus tincidunt libero tellus, sit amet malesuada diam condimentum sed. Duis. Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. \n\nUt hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. Sed ut perspiciatis, unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam eaque ipsa, quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt, explicabo. Nemo enim ipsam voluptatem, quia voluptas sit, aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos, qui ratione voluptatem sequi nesciunt, neque porro quisquam est, qui dolorem ipsum, quia dolor sit amet consectetur adipisci[ng] velit, sed quia non numquam [do] eius modi tempora inci[di]dunt, ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum[d] exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? [D]Quis autem vel eum i[r]ure reprehenderit, qui in ea voluptate velit esse, quam nihil molestiae consequatur, vel illum, qui dolorem eum fugiat, quo voluptas nulla pariatur?");

const roles = ref([
    { name: 'Software Engineer' },
    { name: 'Product Manager' },
    { name: 'Data Scientist' },
    { name: 'UX Designer' },
    { name: 'Marketing Specialist' },
    { name: 'Sales Associate' },
    { name: 'Data Analyst' },
    { name: 'Human Resources Manager' },
    { name: 'Financial Analyst' },
    { name: 'Project Manager' },
    { name: 'Quality Assurance Engineer' },
    { name: 'Customer Support Representative' },    
]);

const onFileSelect = (event) => {
    // When multiple is false, we only want one file in the list.
    // The event.files array contains the files that were just selected.
    // We'll replace the component's entire file list with an array containing only the first of the newly selected files.
    if (fileUpload.value.files.length > 1) {
        fileUpload.value.files.splice(0, fileUpload.value.files.length - 1);
    }
};

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