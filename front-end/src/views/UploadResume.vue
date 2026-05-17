<template>
    <div class="grid grid-cols-12 gap-8">
        <div class="card col-span-12">
            <div class="px-4 mt-3 w-full rounded-2xl bg-indigo-900">
                <p class="text-white text-lg pt-3 font-semibold">Upload a CV or Resume</p>
                <FileUpload @select="onFileSelect" :showUploadButton="false" ref="fileUpload" name="files" :multiple="true" accept="application/pdf" :auto="false" style="border: 0;" class="bg-indigo-900">
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
                <p class="text-white py-3 text-sm">Upload one or more PDF resumes</p>
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
        <div class="card col-span-12 lg:col-span-7">
            <div class="flex flex-col gap-1">
                <label for="result" class="text-lg font-medium">Result</label>
                <Textarea class="text-justify" id="result" v-model="result" rows="5" fluid autoResize readonly />
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { api } from "../helpers/axios";
import { useRouter } from "vue-router";

const fileUpload = ref();
const router = useRouter();
const selectedCountry = ref();
const jobDescription = ref("Cras nec velit aliquet, tempus velit eu, luctus lacus. Nulla vulputate lacus nisl, accumsan tristique magna rutrum id. Sed nisi magna, cursus vel velit eget, maximus cursus lacus. Donec non libero magna. Vestibulum vitae finibus ante. Praesent sit amet turpis faucibus, posuere augue a, posuere nisl. Donec ut enim varius, porttitor ligula in, accumsan neque. Etiam vel convallis lorem. Aliquam erat volutpat. Vestibulum gravida urna quis dolor ornare, ullamcorper condimentum justo aliquet. In ligula tortor, posuere accumsan diam id, vestibulum porta metus. Praesent eget imperdiet eros. \n\nCurabitur non quam sed magna tincidunt iaculis nec ac felis. Quisque pulvinar ligula neque, vitae hendrerit felis hendrerit ac. Vivamus nec vehicula elit, sit amet condimentum quam. Morbi quis orci ac massa semper congue. Aliquam eget imperdiet nibh, vel bibendum neque. Etiam sit amet massa ut sem feugiat euismod. Maecenas convallis mollis libero, a bibendum risus placerat nec. Praesent blandit faucibus neque vitae convallis. Nam sed ornare augue.Proin eu ullamcorper orci. In at erat nibh. Vestibulum a turpis sapien. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.");
const loading = ref(false);
const result = ref("Select one or more resumes and submit to rank them against the chosen job description.");

const defaultJobDescription = jobDescription.value;
const roleDescriptions = {
    'Software Engineer': 'Looking for a software engineer with experience in building web applications, writing clean code, debugging production issues, and collaborating with product teams.',
    'Product Manager': 'Looking for a product manager who can translate user needs into roadmaps, coordinate delivery, and work closely with engineering and design teams.',
    'Data Scientist': 'Looking for a data scientist with experience in statistics, machine learning, data cleaning, model evaluation, and communicating insights clearly.',
    'UX Designer': 'Looking for a UX designer with experience in wireframing, prototyping, user research, interaction design, and accessibility.',
    'Marketing Specialist': 'Looking for a marketing specialist who understands campaign planning, content creation, analytics, and audience growth.',
    'Sales Associate': 'Looking for a sales associate with strong communication skills, customer engagement experience, and the ability to meet sales targets.',
    'Data Analyst': 'Looking for a data analyst with experience in SQL, dashboards, reporting, data visualization, and turning data into recommendations.',
    'Human Resources Manager': 'Looking for an HR manager with experience in recruitment, employee relations, policy implementation, and talent screening.',
    'Financial Analyst': 'Looking for a financial analyst with experience in financial modeling, forecasting, reporting, and business analysis.',
    'Project Manager': 'Looking for a project manager who can plan delivery, manage timelines, coordinate stakeholders, and keep projects on track.',
    'Quality Assurance Engineer': 'Looking for a quality assurance engineer with experience in test planning, automation, bug tracking, and release validation.',
    'Customer Support Representative': 'Looking for a customer support representative with strong communication, issue resolution, and service-oriented experience.',
};

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

watch(selectedCountry, (role) => {
    const roleName = role?.name;
    jobDescription.value = roleName && roleDescriptions[roleName]
        ? roleDescriptions[roleName]
        : defaultJobDescription;
});

const onFileSelect = (event) => {
    const files = event?.files ?? [];
    result.value = files.length > 0
        ? `${files.length} file(s) ready for analysis.`
        : 'Select one or more resumes and submit to rank them.';
};

const createPostFile = async () => {
    if (!fileUpload.value || fileUpload.value.files.length === 0) {
        alert("Please select at least one PDF file first.");
        return;
    }

    const formData = new FormData();
    const files = Array.from(fileUpload.value.files);

    files.forEach((file) => {
        formData.append('files', file);
    });
    formData.append('job_description', jobDescription.value);

    loading.value = true;
    result.value = 'Analyzing resumes...';

    try {
        const response = await api.post('/analyze-resumes', formData);

        sessionStorage.setItem('cohr_analysis_result', JSON.stringify(response.data));
        result.value = `Analysis complete. Ranked ${response.data.total} candidate(s).`;
        await router.push('/result');
    } catch (error) {
        console.error("Error uploading resumes:", error);
        if (!error?.response) {
            result.value = 'Could not reach the backend at http://localhost:8080. Start the FastAPI server, then try again.';
        } else {
            result.value = error?.response?.data?.detail || 'Something went wrong while analyzing resumes.';
        }
    } finally {
        loading.value = false;
    }
};
</script>
